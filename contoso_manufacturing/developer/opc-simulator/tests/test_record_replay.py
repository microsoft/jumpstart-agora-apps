import sys
import os

import pytest
import filecmp


this_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, this_dir)
sys.path.insert(0, os.path.join(this_dir, "../app"))


# pylint: disable=wrong-import-position
from opcua_server_controller import OpcUaServerController
from server_launcher import load_config


@pytest.mark.asyncio
async def test_can_record_replay():
    config_source = os.path.join(this_dir, "data/replay-record.json")
    config = load_config(config_source)

    src_frames_file = os.path.join(this_dir, "data/frames.dat")
    dst_frames_file = os.path.join(this_dir, "data/frames2.dat")

    config["RunSettings"]["ReplayDataFrameFilePath"] = src_frames_file
    config["RunSettings"]["RecordDataFrameFilePath"] = dst_frames_file

    server = OpcUaServerController(config)

    await server.start()

    assert filecmp.cmp(src_frames_file, dst_frames_file, shallow=False)
    os.remove(dst_frames_file)
