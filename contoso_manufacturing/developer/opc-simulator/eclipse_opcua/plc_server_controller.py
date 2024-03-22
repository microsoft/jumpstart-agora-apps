from __future__ import annotations

import json
import logging
import os
import re
import sys
from datetime import timezone
from typing import Any, Dict, List, Set

from asyncua import Node, ua
from pylogix import PLC

this_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, this_dir)

# pylint: disable=wrong-import-position
try:
    from .type_definitions import UpdateListWithTimeStamp
    from .config_types import VarTypeConfig
    from .di_opcua_server import Device, DiOpcUaServer
    from .opcua_server_controller import OpcUaServerController
    from .server_launcher import launch_server
except ImportError:
    from type_definitions import UpdateListWithTimeStamp
    from config_types import VarTypeConfig
    from di_opcua_server import Device, DiOpcUaServer
    from opcua_server_controller import OpcUaServerController
    from server_launcher import launch_server


# pylint: disable=R0903
class SubscriptionHandler:
    def __init__(
        self,
        nodes_to_tag_names: Dict[Node, str],
        plc: PLC,
        values: Dict[str, Any],
        tags_being_written: Set[str],
    ):
        self.nodes_to_tag_names = nodes_to_tag_names
        self.plc = plc
        self.values = values
        self.tags_being_written = tags_being_written

    def datachange_notification(self, node: Node, val: Any, _: ua.DataChangeNotification):
        tag_name = self.nodes_to_tag_names.get(node)
        old_val = self.values.get(tag_name, None)
        if old_val is None or old_val == val:
            return
        self.tags_being_written.add(tag_name)
        self.values[tag_name] = val
        logging.info("Updating PLC tag %s with value %s", tag_name, str(val))
        self.plc.Write(tag=tag_name, value=val)


# pylint: enable=R0903

re_local_output = re.compile(r"(Local:(?:\d)+:O)\.DATA\.(\d+)")
re_array_element = re.compile(r"([A-z0-9_]+)\[(\d+)]")


class RockwellPLCServer(OpcUaServerController):
    """
    Implements an OPCUA server that exposes all tags of a Rockwell PLC under one device
    """

    def __init__(self, config: Dict[str, Any]):
        plc_conf = config.get("PLCSettings", {})
        ip_address = plc_conf["IPAddress"]
        device_type_name = plc_conf.get("DeviceTypeName", "RockwellPLC")
        device_instance_name = plc_conf.get("DeviceInstanceName", "FluidDemoPLC")

        logging.info("Connecting to PLC at %s ...", ip_address)
        self.plc = PLC(ip_address)
        res = self.plc.GetDeviceProperties()
        dev_props = res.Value

        logging.info("Retrieving PLC tags ...")
        variables = self.query_plc_tags(plc_conf)

        config.update(
            {
                "DeviceTypes": [
                    {
                        "DeviceType": device_type_name,
                        "Variables": variables,
                        "Properties": {},
                    }
                ],
                "Devices": [
                    {
                        "Name": device_instance_name,
                        "DeviceType": device_type_name,
                        "UseStringNodeIds": plc_conf.get("UseStringNodeIds", False),
                        "Properties": [
                            {
                                "Name": "SerialNumber",
                                "Type": "String",
                                "Value": dev_props.SerialNumber,
                            },
                            {
                                "Name": "HardwareRevision",
                                "Value": dev_props.Revision,
                            },
                            {
                                "Name": "SoftwareRevision",
                                "Value": dev_props.Revision,
                            },
                            {
                                "Name": "Manufacturer",
                                "Type": "LocalizedText",
                                "Value": {
                                    "Text": dev_props.Vendor,
                                    "Locale": "en_US",
                                },
                            },
                            {
                                "Name": "Model",
                                "Type": "LocalizedText",
                                "Value": {
                                    "Text": dev_props.ProductName,
                                    "Locale": "en_US",
                                },
                            },
                        ],
                    }
                ],
            }
        )

        self.tags_being_written = set()
        self.subscription = None
        super().__init__(config)
        self.cached_values: Dict[str, Any] = {}

    def query_plc_tags(self, plc_conf: Dict[str, Any]) -> List[VarTypeConfig]:
        tag_include_list = plc_conf.get("TagIncludeList", [])
        tag_exclude_list = plc_conf.get("TagExcludeList", [])
        writable_tags = set(plc_conf.get("WritableTags", []))
        tag_plc_to_opcua_mapping: Dict[str, str] = plc_conf.get("TagPlcToOpcuaMapping", {})
        data_types = {
            "BOOL": "Boolean",
            "SINT": "SByte",
            "INT": "Int16",
            "DINT": "Int32",
            "REAL": "Float",
            "COUNTER": "UInt32",
            "TIMER": "Int32",
        }
        tags = self.plc.GetTagList(allTags=False)

        tag_name_to_data_type = {t.TagName: data_types.get(t.DataType) for t in tags.Value}
        self.counter_tags = {t.TagName for t in tags.Value if t.DataType == "COUNTER"}

        self.simple_tag_names = []
        self.complex_tag_names = []
        variables = []

        if tag_plc_to_opcua_mapping:
            variables = self.process_tag_mappings(
                tag_plc_to_opcua_mapping, tag_name_to_data_type, writable_tags
            )
        else:  # simple mapping with inclusion/exclusion list
            for tag in tags.Value:
                tag_name = tag.TagName
                if tag_include_list and tag_name not in tag_include_list:
                    continue
                if tag_exclude_list and tag_name in tag_exclude_list:
                    continue
                val = self.plc.Read(tag_name)
                data_type = tag_name_to_data_type[tag_name]
                self.simple_tag_names.append(tag_name)
                writable = tag_name in writable_tags
                variables.append(self.opc_var_define(tag_name, data_type, val.Value, writable))

        self.tag_plc_to_opcua_mapping = tag_plc_to_opcua_mapping
        return variables

    def opc_var_define(self, opc_var_name, opcua_variant_type, value, writable=False):
        return {
            "Name": opc_var_name,
            "Type": opcua_variant_type,
            "Value": value,
            "Writable": writable,
        }

    def process_tag_mappings(
        self,
        tag_plc_to_opcua_mapping: Dict[str, str],
        tag_name_to_data_type,
        writable_tags: List[str],
    ):
        variables = []
        for tag_name, var_name in tag_plc_to_opcua_mapping.items():
            match_res = re_local_output.match(tag_name)
            if match_res:  # local output bits mapping
                val, _ = self.read_complex_tag(tag_name)
                variables.append(self.opc_var_define(var_name, "Boolean", val))
                self.complex_tag_names.append(tag_name)
                continue
            match_res = re_array_element.match(tag_name)
            if match_res:  # array mapping
                data_type = tag_name_to_data_type[match_res.group(1)]
                val, _ = self.read_complex_tag(tag_name)
                variables.append(self.opc_var_define(var_name, data_type, val))
                self.complex_tag_names.append(tag_name)
                continue
            if tag_name in self.counter_tags:
                val, _ = self.read_complex_tag(tag_name)
                variables.append(self.opc_var_define(var_name, "Int32", val))
                self.complex_tag_names.append(tag_name)
                continue

            val = self.plc.Read(tag_name)
            data_type = tag_name_to_data_type[tag_name]
            self.simple_tag_names.append(tag_name)
            writable = tag_name in writable_tags
            var_definition = self.opc_var_define(var_name, data_type, val.Value, writable)
            variables.append(var_definition)
        return variables

    def read_complex_tag(self, tag_name):
        if tag_name in self.counter_tags:  # counter
            res = self.plc.Read(tag_name)
            is_good = res.Status == "Success"
            value = int.from_bytes(res.Value[8:12], "little") if is_good else None
            return value, is_good

        match_res = re_local_output.match(tag_name)
        if match_res:  # Local:#:O output
            res = self.plc.Read(match_res.group(1))
            bit_number = int(match_res.group(2))
            is_good = res.Status == "Success"
            if is_good:
                bytes_arr = res.Value
                new_val = bool(((bytes_arr[bit_number // 8]) >> (bit_number % 8)) & 1)
            return new_val, is_good

        match_res = re_array_element.match(tag_name)
        if match_res:  # Array read
            idx = int(match_res.group(2))
            res = self.plc.Read(match_res.group(1), idx + 1)
            is_good = res.Status == "Success"
            value = (res.Value[idx] if idx > 0 else res.Value) if is_good else None
            return value, is_good
        assert False, "Logic error: unsupported complex tag"

    def get_update_list(self, _: Device) -> UpdateListWithTimeStamp:
        response = self.plc.GetPLCTime()
        ts = response.Value.replace(tzinfo=timezone.utc)
        self.tags_being_written.clear()
        if self.simple_tag_names:
            responses = self.plc.Read(self.simple_tag_names)
            update_list = []
            for response in responses:
                tag_name = response.TagName
                is_good = response.Status == "Success"
                new_val = response.Value
                # skip the tag if it was written since we started
                if tag_name in self.tags_being_written:
                    logging.info(
                        "Skipping read of tag %s as it was just written to PLC",
                        tag_name,
                    )
                    continue
                if tag_name in self.counter_tags:
                    if isinstance(new_val, str):
                        new_val = 0
                    else:
                        new_val = int.from_bytes(new_val[8:12], "little")

                prev_val = self.cached_values.get(tag_name, None)
                if new_val != prev_val:
                    var_name = self.tag_plc_to_opcua_mapping.get(tag_name, tag_name)
                    update_list.append((var_name, new_val, is_good))
                    self.cached_values[tag_name] = new_val
        # Read complex tags one by one
        for tag_name in self.complex_tag_names:
            new_val, is_good = self.read_complex_tag(tag_name)
            var_name = self.tag_plc_to_opcua_mapping.get(tag_name, tag_name)
            update_list.append((var_name, new_val, is_good))
        return update_list, ts

    async def on_server_created(self, server: DiOpcUaServer):
        nodes_to_tag_names = {}
        opc_to_plc = {v: k for k, v in self.tag_plc_to_opcua_mapping.items()}

        for _, device in server.devices.items():
            node_to_names = {
                v: opc_to_plc.get(k, k) for k, v in device.nodes.nodes_by_display_name.items()
            }
            nodes_to_tag_names.update(node_to_names)

        nodes_to_monitor = []
        for _, devices in server.devices.items():
            nodes_to_monitor += devices.nodes.nodes_by_browse_name.values()

        logging.info("Subscribing to data value changes on %d nodes... ", len(nodes_to_monitor))
        handler = SubscriptionHandler(
            nodes_to_tag_names, self.plc, self.cached_values, self.tags_being_written
        )
        self.subscription = await server.server.create_subscription(0, handler)
        await self.subscription.subscribe_data_change(nodes_to_monitor)

        # dump server config if requested
        dump_config_file_path = self.config.get("DumpDeviceConfigFilePath", "")
        if dump_config_file_path:
            config = self.config.copy()
            config.pop("PLCSettings", None)
            with open(dump_config_file_path, "w", encoding="utf-8") as fp:
                json.dump(self.config, fp, indent=2)


def main():
    def create_server(cfg: Dict[str, Any]):
        return RockwellPLCServer(cfg)

    launch_server(create_server, relaunch_after=1.0)


if __name__ == "__main__":
    main()
