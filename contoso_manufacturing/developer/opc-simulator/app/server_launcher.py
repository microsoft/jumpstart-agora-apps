import sys
import json
import os
import asyncio
from typing import Callable, Dict
import logging
from collections import OrderedDict
from signal import signal, SIGINT, SIGTERM

try:
    from .opcua_server_controller import OpcUaServerController
except ImportError:
    from opcua_server_controller import OpcUaServerController


def load_config(config_source=None):
    config = {}
    if not config_source:
        config_source = sys.argv[1] if len(sys.argv) > 1 else "-"
    if isinstance(config_source, str):
        if config_source == "-":
            config = json.load(sys.stdin, object_pairs_hook=OrderedDict)
        elif os.path.isfile(config_source):
            with open(config_source, encoding="utf-8") as fp:
                config = json.load(fp, object_pairs_hook=OrderedDict)
        else:
            config = json.loads(config_source, object_pairs_hook=OrderedDict)
    return config


def launch_server(
    server_create: Callable[[Dict], OpcUaServerController], relaunch_after=0.0
):  # pragma: no cover
    opcua_impl_server = None
    server_stop = False

    async def start_server():
        nonlocal opcua_impl_server
        while not server_stop:
            try:
                logging.basicConfig(level=logging.INFO)
                opcua_impl_server = server_create(load_config())
                await opcua_impl_server.start()
            except:  # pylint: disable=W0702
                if relaunch_after <= 0:
                    return
                logging.exception("Restarting server in %f seconds...", relaunch_after)
                await asyncio.sleep(1.0)

    def stop_server(*_):
        nonlocal server_stop
        logging.info("Stopping OPC UA server ...")
        server_stop = True
        opcua_impl_server.stop()

    loop = asyncio.get_event_loop()
    main_task = asyncio.ensure_future(start_server())
    signal(SIGINT, stop_server)
    signal(SIGTERM, stop_server)
    try:
        loop.run_until_complete(main_task)
    finally:
        loop.close()
