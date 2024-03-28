from __future__ import annotations
from collections import OrderedDict
from dataclasses import dataclass

import logging
import os.path

from datetime import datetime
from typing import Any, Dict, List

from asyncua import ua, Server, Node
from asyncua.common.instantiate_util import instantiate


class NodeCollection:
    """
    Utility class to easily access a group of nodes by display name
    """

    def __init__(
        self,
        nodes_by_browse_name: Dict[str, Node],
        nodes_by_display_name: Dict[str, Node],
    ):
        self.nodes_by_browse_name = nodes_by_browse_name
        self.nodes_by_display_name = nodes_by_display_name

    def get_by_display_name(self, name) -> Node:
        return self.nodes_by_display_name[name]

    @classmethod
    async def create(cls, server: Server, node_ids: List[ua.NodeId]):
        nodes_by_browse_name = {}
        nodes_by_display_name = {}
        for node_id in node_ids:
            node = server.get_node(node_id)
            attrs = await node.read_attributes(
                [
                    ua.AttributeIds.DisplayName,
                    ua.AttributeIds.BrowseName,
                ]
            )
            display_name = attrs[0].Value.Value.Text
            browse_name = attrs[1].Value.Value.to_string()
            nodes_by_display_name[display_name] = node
            nodes_by_browse_name[browse_name] = node
        return cls(nodes_by_browse_name, nodes_by_display_name)


@dataclass
class DeviceType:
    def __init__(
        self,
        name: str,
        ns_idx: int,
        type_node: Node,
        var_types: Dict[str, ua.VariantType],
        server: Server,
    ):
        self.name = name
        self.node = type_node
        self.ns_idx = ns_idx
        self.var_types = var_types
        self.server = server

    @classmethod
    async def create(
        cls,
        server,
        ns_idx,
        di: NodeCollection,
        dev_type_info: Dict[str, Any],
    ) -> DeviceType:
        di_device_type_node = di.get_by_display_name("DeviceType")
        device_type_name = dev_type_info["DeviceType"]

        device_vars_info: List[Dict[str, Any]] = dev_type_info["Variables"]

        subtype_node = await di_device_type_node.add_object_type(ns_idx, device_type_name)
        param_set = await subtype_node.add_object(ns_idx, "ParameterSet")
        await param_set.set_modelling_rule(True)

        var_types = {}
        for var_info in device_vars_info:
            var_name = var_info["Name"]
            var_type = ua.VariantType[var_info["Type"]]
            var_types[var_name] = var_type
            var = await param_set.add_variable(ns_idx, var_name, var_info["Value"], var_type)
            await var.set_modelling_rule(True)
            if var_info.get("Writable", False):
                await var.set_writable()

        return cls(device_type_name, ns_idx, subtype_node, var_types, server)


class Device:
    def __init__(self, nodes: NodeCollection, name: str, device_type: DeviceType):
        self.nodes = nodes
        self.name = name
        self.device_type = device_type

    @classmethod
    async def create(
        cls, parent_node: Node, dev_type: DeviceType, dev_info: Dict[str, Any]
    ) -> Device:
        name = dev_info["Name"]
        use_string_in_node_ids = dev_info.get("UseStringNodeIds", False)
        dev_nodeid = ua.NodeId(name, dev_type.ns_idx) if use_string_in_node_ids else None
        device_nodes = await instantiate(
            parent_node,
            dev_type.node,
            nodeid=dev_nodeid,
            bname=name,
            dname=ua.LocalizedText(name),
            idx=dev_type.ns_idx,
            instantiate_optional=False,
        )

        dev_instance_nodes = await NodeCollection.create(dev_type.server, device_nodes)

        # set properties of this device instance
        for prop in dev_info.get("Properties", []):
            prop_name = prop["Name"]
            prop_value = prop["Value"]
            property_node = dev_instance_nodes.get_by_display_name(prop_name)
            prop_type = prop.get("Type")
            if prop_type is not None:
                if prop_type == "LocalizedText":
                    prop_value = ua.LocalizedText(prop_value["Text"], prop_value["Locale"])
                else:
                    prop_value = ua.Variant(prop_value, ua.VariantType[prop_type])
            await property_node.write_value(prop_value)
        return cls(dev_instance_nodes, name, dev_type)

    def update_variable(
        self,
        var_name: str,
        new_val: Any,
        is_good: bool = True,
        timestamp=datetime.utcnow(),
    ):
        var_type = self.device_type.var_types[var_name]
        var_node = self.nodes.get_by_display_name(var_name)
        code = ua.StatusCodes.Good if is_good else ua.StatusCodes.BadDataUnavailable
        dv = ua.DataValue(
            ua.Variant(new_val, var_type),
            ua.StatusCode(code),
            ServerTimestamp=datetime.utcnow(),
            SourceTimestamp=timestamp,
        )
        return var_node.write_value(dv)


class DiOpcUaServer:
    def __init__(self, config: Dict):
        self.server = Server()
        self.config = config

        server_info = config.get("Server", {})
        self.server.set_server_name(server_info.get("Name", "An OPC UA server"))
        self.server.set_endpoint(server_info.get("Endpoint", "opc.tcp://0.0.0.0:4840"))

        self.devices: Dict[str, Device] = OrderedDict()
        self.device_types: Dict[str, DeviceType] = OrderedDict()

    async def init(self):
        server = self.server
        await server.init()

        # import DI companion spec nodes first!
        this_dir = os.path.dirname(os.path.realpath(__file__))
        di_model_path = os.path.join(this_dir, "Opc.Ua.Di.NodeSet2.xml")
        di_node_ids = await server.import_xml(di_model_path)
        di = await NodeCollection.create(server, di_node_ids)

        # add a custom namespace for our nodes
        info = self.config.get("Server", {})
        ns = info.get("CustomNamespace", "http://microsoft.com/Opc/DefineMe")
        ns_idx = await server.register_namespace(ns)

        # create device types nodes
        for dev_type_info in self.config.get("DeviceTypes", []):
            dev_type = await DeviceType.create(server, ns_idx, di, dev_type_info)
            self.device_types[dev_type.name] = dev_type

        # instantiate device instances
        for dev_info in self.config.get("Devices", []):
            dev_type = self.device_types[dev_info["DeviceType"]]
            dev = await Device.create(server.nodes.objects, dev_type, dev_info)
            self.devices[dev.name] = dev

    async def __aenter__(self):
        await self.init()
        logging.info("Starting server on %s", self.server.endpoint.geturl())
        await self.server.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.server.stop()
