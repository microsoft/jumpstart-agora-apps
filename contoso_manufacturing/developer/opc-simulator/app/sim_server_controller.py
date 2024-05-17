from __future__ import annotations
from copy import deepcopy
import os
import sys
from collections import OrderedDict
from time import time
from datetime import datetime
from typing import Dict, List, Tuple, Any


this_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, this_dir)

# pylint: disable=wrong-import-position
try:
    from .di_opcua_server import Device
    from .type_definitions import UpdateListWithTimeStamp, UpdateList
    from .opcua_server_controller import OpcUaServerController
    from .server_launcher import launch_server
except ImportError:
    from di_opcua_server import Device
    from type_definitions import UpdateListWithTimeStamp, UpdateList
    from opcua_server_controller import OpcUaServerController
    from server_launcher import launch_server


class SimulationVariable:
    def __init__(self, config: Dict[str, Any]):
        self.values: [] = config["ValueSequence"]
        self.periods: [] = config.get("UpdatePeriodSeconds", [0])
        assert all(p >= 0 for p in self.periods), "Sample periods need to be non-negative"
        self.repeat: bool = config.get("RepeatForever", True)
        self.target_devices = config.get("TargetDevices")
        self.target_variables = config.get("TargetVariables")
        self.idx = 0
        self.start_ts = None

    def start(self):
        self.idx = 0

    def get_value(self):
        return self.values[self.idx % len(self.values)]

    def get_period_seconds(self):
        return self.periods[self.idx % len(self.periods)]

    def full_loop_completed(self):
        return self.idx >= len(self.values)

    def new_value_ready(self, now_ts) -> bool:
        if not self.start_ts:
            self.start_ts = now_ts
            return True

        if not self.repeat and self.idx >= len(self.values):
            return False

        current_period = self.get_period_seconds()
        if now_ts - self.start_ts > current_period:
            # new sample is available
            self.start_ts += current_period
            self.idx += 1
            if not self.repeat and self.idx >= len(self.values):
                return False
            return True
        return False

    def value_good(self) -> bool:
        return True


class SimulationServer(OpcUaServerController):
    def __init__(self, config: Dict):
        super().__init__(config)

        self.simulators: Dict[str, SimulationVariable] = {}
        run_settings = config.get("RunSettings", {})
        simulation_sources = run_settings.get("SimulationSources", [])
        simulator_instances = [SimulationVariable(cfg) for cfg in simulation_sources]
        self.stop_on_full_loop = run_settings.get("StopSimulatorAfterFullLoop", False)

        for sim in simulator_instances:
            for device_name in sim.target_devices:
                for var_name in sim.target_variables:
                    simulator_key = device_name + var_name
                    self.simulators[simulator_key] = deepcopy(sim)

        self.stats: Dict[str, Dict[str, int]] = OrderedDict()

    def get_update_list(self, device: Device) -> UpdateListWithTimeStamp:
        update_list: List[Tuple[str, Any, bool]] = []
        device_name = device.name
        now_ts = time()
        for var_name in device.device_type.var_types:
            simulator_key = device_name + var_name
            sim_var = self.simulators.get(simulator_key)
            if sim_var and sim_var.new_value_ready(now_ts):
                update_list.append((var_name, sim_var.get_value(), sim_var.value_good()))

        # don't return any data if we were told to stop after a full simulation data loop
        if self.stop_on_full_loop:
            if all(sim.full_loop_completed() for _, sim in self.simulators.items()):
                self.server_running = False
                return [], datetime.now()

        # update statistics
        self.update_simulator_stats(device_name, update_list)
        return update_list, datetime.now()

    def update_simulator_stats(self, device_name: str, update_list: UpdateList):
        if device_name not in self.stats:
            self.stats[device_name] = OrderedDict()
        dev_stats = self.stats[device_name]
        for var_name, _, _ in update_list:
            if var_name not in dev_stats:
                dev_stats[var_name] = 1
            else:
                dev_stats[var_name] += 1


def main():
    def create_server(cfg: Dict[str, Any]):
        return SimulationServer(cfg)

    launch_server(create_server, relaunch_after=0.0)


if __name__ == "__main__":
    main()
