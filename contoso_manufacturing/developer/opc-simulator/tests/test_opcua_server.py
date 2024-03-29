import os
import sys

import pytest

this_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, this_dir)
sys.path.insert(0, os.path.join(this_dir, "../app"))

# pylint: disable=wrong-import-position
from di_opcua_server import DiOpcUaServer
from server_launcher import load_config


@pytest.mark.asyncio
async def test_can_instantiate_device():
    config_source = os.path.join(this_dir, "data/sample-definition.json")
    config = load_config(config_source)

    async with DiOpcUaServer(config) as di_server:
        assert "Device1Type" in di_server.device_types

        # Check we have one new namespace
        namespaces = await di_server.server.get_namespace_array()
        assert len(namespaces) == 4
        assert config["Server"]["CustomNamespace"] in namespaces

        # Check device property serial number matches the expected value
        device_instance_node = await di_server.server.nodes.objects.get_child("Device1")
        serial_number_node = await device_instance_node.get_child("2:SerialNumber")
        serial_number_value = await serial_number_node.read_value()
        assert serial_number_value == "42424242"

        # Check instantiated device has device type initialized properties
        parameter_set_node = await device_instance_node.get_child("3:ParameterSet")
        for var_def in config["DeviceTypes"][0]["Variables"]:
            var_node = await parameter_set_node.get_child(f'3:{var_def["Name"]}')
            var_val = await var_node.read_value()
            assert var_def["Value"] == var_val


if __name__ == "__main__":
    pytest.main(["-x", __file__])
