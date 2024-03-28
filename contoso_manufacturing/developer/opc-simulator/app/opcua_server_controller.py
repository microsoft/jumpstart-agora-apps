from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from math import ceil
from time import time
from threading import Event


from typing import Dict

try:
    from .type_definitions import UpdateListWithTimeStamp
    from .di_opcua_server import Device, DiOpcUaServer
    from .frame_record_replay import DataFrameRecordReplay
except ImportError:
    from type_definitions import UpdateListWithTimeStamp
    from di_opcua_server import Device, DiOpcUaServer
    from frame_record_replay import DataFrameRecordReplay


class OpcUaServerController:
    """
    Instantiates an OPCUA server and runs the update loop
    """

    def __init__(self, config: Dict):
        self.config = config
        run_settings = self.config.get("RunSettings", {})
        self.poll_interval = run_settings.get("PollIntervalSeconds", 0.1)
        self.report_usage_interval = run_settings.get("ReportUsageIntervalSeconds", 5.0)
        self.delay_start_seconds = run_settings.get("DelayStartSeconds", 0.0)
        self.num_data_polls = 0
        self.var_types = {}  # OPCUA var types per device type
        self.started_event = Event()

        asyncua_logging_level = run_settings.get("AsyncuaLoggingLevel", "WARNING")
        # pylint: disable=E1103
        for name in logging.root.manager.loggerDict:
            if name.startswith("asyncua"):
                logging.getLogger(name).setLevel(asyncua_logging_level)
        # pylint: enable=E1103

        # Record/Replay data frame setup (if specified)
        record_file_path = run_settings.get("RecordDataFrameFilePath")
        replay_file_path = run_settings.get("ReplayDataFrameFilePath")
        replay_in_a_loop = run_settings.get("ReplayInALoop", True)
        device_types_cfg = config.get("DeviceTypes", [])
        self.record_replay = DataFrameRecordReplay(
            record_file_path,
            replay_file_path,
            device_types_cfg,
            replay_in_a_loop,
        )

        self.server_running = False

    def get_update_list(self, device: Device) -> UpdateListWithTimeStamp:
        update_list = self.record_replay.read_frame(device)
        if self.record_replay.replay_completed:
            self.stop()
        return update_list, datetime.now()

    async def on_server_created(self, _: DiOpcUaServer):
        await asyncio.sleep(0)

    async def start(self):
        num_report_poll_cycles = (
            int(ceil(self.report_usage_interval / self.poll_interval))
            if self.poll_interval > 0
            else 1
        )
        self.server_running = True
        logging.info("Instantiating OPCUA server ...")
        try:
            async with DiOpcUaServer(self.config) as server:
                await self.on_server_created(server)
                self.started_event.set()

                if self.delay_start_seconds > 0:
                    logging.info("Delaying polling start by %f seconds", self.delay_start_seconds)
                    await asyncio.sleep(self.delay_start_seconds)

                report_frame_count = 0
                acc_remaining_cycle = 0.0
                poll_start_ts = time()
                next_report_ts = poll_start_ts + self.report_usage_interval
                logging.info("Starting polling loop ...")
                while self.server_running:
                    futures = []
                    for _, device in server.devices.items():
                        update_list, ts = self.get_update_list(device)
                        self.record_replay.record_frame(update_list, device)
                        for var_name, new_val, is_good in update_list:
                            fut = device.update_variable(var_name, new_val, is_good, ts)
                            futures.append(fut)
                    await asyncio.gather(*futures)

                    report_frame_count += 1
                    self.num_data_polls += 1

                    # report period utilization
                    if time() > next_report_ts and self.report_usage_interval > 0.0:
                        if self.poll_interval > 0:  # running at a target frame rate
                            ave_remaining = acc_remaining_cycle / num_report_poll_cycles
                            utilization_pct = (
                                100.0 * (self.poll_interval - ave_remaining) / self.poll_interval
                            )
                            logging.info(
                                "Polling period utilization %f%%",
                                round(utilization_pct),
                            )
                        else:
                            rate_hz = report_frame_count / self.report_usage_interval
                            logging.info("Polling data at %f Hz", rate_hz)
                        report_frame_count = 0
                        acc_remaining_cycle = 0.0
                        next_report_ts += self.report_usage_interval

                    next_time_point = poll_start_ts + (self.num_data_polls * self.poll_interval)
                    remaining_cycle_secs = max(next_time_point - time(), 0)
                    acc_remaining_cycle += remaining_cycle_secs
                    if remaining_cycle_secs > 0:
                        await asyncio.sleep(remaining_cycle_secs)
        except:  # pylint: disable=W0702
            logging.exception("Server internal error")
        logging.info("OPCUA server has been stopped")
        self.server_running = False

    def stop(self):
        logging.info("Stopping OPCUA server ... please wait")
        self.server_running = False
