import asyncio
import json
import os
import sys

import pytest
from typing import Dict, Any

this_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, this_dir)
sys.path.insert(0, os.path.join(this_dir, "../app"))

# pylint: disable=wrong-import-position
from test_harness import app

try:
    from .opcua_client_data_capture import OpcUaClientDataCapture
except ImportError:
    from opcua_client_data_capture import OpcUaClientDataCapture


@pytest.fixture(name="testapp")
def _test_app():
    return app


def read_json(file_path):
    with open(file_path, encoding="utf-8") as fp:
        return json.load(fp)


@pytest.mark.asyncio
async def test_can_get_version(testapp):
    client = testapp.test_client()
    response = await client.get("/api/version")
    assert response.status_code == 200
    res = await response.json
    assert res["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_can_collect_specified_number_of_samples(testapp):
    client = testapp.test_client()
    opc_sim_cfg: Dict[str, Any] = read_json(os.path.join(this_dir, "data/simulator3.json"))

    var1_name = "ns=3;s=Device1.ParameterSet.Var1"
    var2_name = "ns=3;s=Device1.ParameterSet.Var2"
    var3_name = "ns=3;s=Device1.ParameterSet.Var3"

    run_settings = opc_sim_cfg["RunSettings"]
    run_settings["StopSimulatorAfterFullLoop"] = True
    sim_sources = run_settings["SimulationSources"]
    expected_list_var1_2 = sim_sources[0]["ValueSequence"]
    expected_list_var3 = sim_sources[1]["ValueSequence"]
    capturer = OpcUaClientDataCapture(
        url=opc_sim_cfg["Server"]["Endpoint"],
        node_samples={
            var1_name: len(expected_list_var1_2),
            var2_name: len(expected_list_var1_2),
            var3_name: len(expected_list_var3),
        },
    )

    response = await client.post("/api/start", json=opc_sim_cfg)
    assert response.status_code == 200
    res = await response.json
    assert res["running"]

    capturer.start_capture()

    data = capturer.wait_for_completion()

    assert len(data[var1_name]) == len(expected_list_var1_2)
    assert all([a == b for a, b in zip(expected_list_var1_2, data[var1_name])])
    assert all([a == b for a, b in zip(expected_list_var1_2, data[var2_name])])

    assert len(data[var3_name]) == len(expected_list_var3)
    assert all([a == b for a, b in zip(expected_list_var3, data[var3_name])])

    response = await client.post("/api/stop")
    assert response.status_code == 200
    res = await response.json
    assert not res["running"]


@pytest.mark.asyncio
async def test_can_collect_for_while(testapp):
    client = testapp.test_client()
    opc_sim_cfg: Dict[str, Any] = read_json(os.path.join(this_dir, "data/simulator3.json"))

    response = await client.post("/api/start", json=opc_sim_cfg)
    assert response.status_code == 200
    res = await response.json
    assert res["running"]

    var1_name = "ns=3;s=Device1.ParameterSet.Var1"
    var2_name = "ns=3;s=Device1.ParameterSet.Var2"
    var3_name = "ns=3;s=Device1.ParameterSet.Var3"
    capturer = OpcUaClientDataCapture(
        url=opc_sim_cfg["Server"]["Endpoint"],
        node_samples={
            var1_name: -1,
            var2_name: -1,
            var3_name: -1,
        },
    )

    capturer.start_capture()

    await asyncio.sleep(1.0)

    data = capturer.end_capture()

    # we should have some samples now
    assert len(data[var1_name]) > 0
    assert len(data[var2_name]) > 0
    assert len(data[var3_name]) > 0

    response = await client.post("/api/stop")
    assert response.status_code == 200
    res = await response.json
    assert not res["running"]
