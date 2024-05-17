import asyncio
import logging
import os
import sys
from typing import Dict
from threading import Event, Thread

from quart import Quart, jsonify, request


this_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, this_dir)

# pylint: disable=wrong-import-position
try:
    from .sim_server_controller import SimulationServer
    from .server_launcher import load_config
except ImportError:
    from sim_server_controller import SimulationServer
    from server_launcher import load_config


class QuartApp(Quart):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        logging.basicConfig(level=logging.INFO)
        self.sim_config = None
        self.simulator_instance = None
        self.sim_thread = None
        self.sim_started_event = Event()

    def start(self, config) -> None:
        self.stop()
        self.sim_config = load_config(config)
        self.sim_thread = Thread(target=self._worker)
        self.sim_started_event.clear()
        self.sim_thread.start()
        self.sim_started_event.wait()
        self.simulator_instance.started_event.wait()

    def wait_to_complete(self) -> None:
        if self.sim_thread and self.sim_thread.is_alive():
            self.sim_thread.join()

    def stop(self) -> None:
        if self.simulator_instance is not None:
            self.simulator_instance.stop()
        self.wait_to_complete()

    def get_sim_stats(self) -> Dict[str, Dict[str, int]]:
        return self.simulator_instance.stats if self.simulator_instance else {}

    def is_running(self) -> bool:
        return bool(self.simulator_instance and self.simulator_instance.server_running)

    def _worker(self):
        loop = asyncio.new_event_loop()
        try:
            main_task = asyncio.ensure_future(self._start_opcua(), loop=loop)
            loop.run_until_complete(main_task)
        finally:
            loop.close()

    async def _start_opcua(self):
        self.simulator_instance = SimulationServer(self.sim_config)
        coroutine = self.simulator_instance.start()
        self.sim_started_event.set()
        await coroutine


app = QuartApp(__name__)


@app.route("/api/version")
async def get_version():
    return jsonify({"version": "1.0.0"})


# %% OPC UA endpoints
@app.route("/api/start", methods=["POST"])
async def start():
    wait = request.args.get("wait", "False").lower() in ["true", "1"]
    config = await request.get_data()
    app.start(config.decode())
    if wait:
        app.wait_to_complete()
    return status()


@app.route("/api/stop", methods=["POST"])
def stop():
    app.stop()
    return status()


@app.route("/api/running", methods=["GET"])
def status():
    res = {"running": app.is_running(), "stats": app.get_sim_stats()}
    return jsonify(res)


@app.after_serving
async def stop_simulator():
    app.stop()


# %% main
def main():
    app.run()


if __name__ == "__main__":
    main()
