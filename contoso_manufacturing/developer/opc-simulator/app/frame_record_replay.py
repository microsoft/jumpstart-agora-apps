import datetime
import os
import struct
from typing import List, Tuple, Dict

from asyncua import ua

try:
    from .config_types import DeviceTypeConfig
    from .type_definitions import UpdateList
    from .di_opcua_server import Device
except ImportError:
    from config_types import DeviceTypeConfig
    from type_definitions import UpdateList
    from di_opcua_server import Device


class DataFrameRecordReplay:
    def __init__(
        self,
        record_data_file_path: str,
        replay_data_file_path: str,
        device_types: List[DeviceTypeConfig],
        replay_in_a_loop: bool,
    ):
        self.var_types: Dict[str, Dict[str, Tuple(str, ua.VariantType)]] = {}
        self.var_names: Dict[str, Dict[int, str]] = {}

        for dev in device_types:
            dev_type_name = dev["DeviceType"]
            self.var_types[dev_type_name] = {}
            self.var_names[dev_type_name] = {}

            var_idx = 0
            for var in dev["Variables"]:
                var_name = var["Name"]
                var_type = ua.VariantType[var["Type"]]
                self.var_types[dev_type_name][var_name] = (var_type, var_idx)
                self.var_names[dev_type_name][var_idx] = var_name
                var_idx += 1

        self.record = bool(record_data_file_path)
        self.replay = bool(replay_data_file_path)

        # pylint: disable=R1732
        if self.record:
            self.record_fp = open(record_data_file_path, "wb")

        if self.replay:
            self.replay_fp = open(replay_data_file_path, "rb")
            self.replay_fp.seek(0, os.SEEK_END)
            self.replay_data_file_size = self.replay_fp.tell()
            self.replay_fp.seek(0, os.SEEK_SET)
        # pylint: enable=R1732

        self.replay_completed = False
        self.replay_in_a_loop = replay_in_a_loop
        self.num_frames_read = 0
        self.num_frames_write = 0

    def read_int(self, num_bytes, signed=True):
        return int.from_bytes(self.replay_fp.read(num_bytes), "big", signed=signed)

    def write_int(self, val: int, num_bytes, signed=True):
        bin_val = val.to_bytes(num_bytes, "big", signed=signed)
        self.record_fp.write(bin_val)

    def read_frame(self, device: Device) -> UpdateList:
        # pylint: disable=R0912
        if not self.replay:
            return []

        dev_var_names = self.var_names[device.device_type.name]

        num_vars_in_frame = self.read_int(2)

        update_list = []
        for _ in range(num_vars_in_frame):
            var_idx = self.read_int(2, signed=False)
            var_type = ua.VariantType(self.read_int(1, False))
            var_good = self.read_int(1, False)
            var_name = dev_var_names[var_idx]

            if var_type == ua.VariantType.Boolean:
                var_val = bool(self.read_int(1))
            elif var_type == ua.VariantType.SByte:
                var_val = self.read_int(1, True)
            elif var_type == ua.VariantType.Byte:
                var_val = self.read_int(1, False)
            elif var_type == ua.VariantType.Int16:
                var_val = self.read_int(2, True)
            elif var_type == ua.VariantType.UInt16:
                var_val = self.read_int(2, False)
            elif var_type == ua.VariantType.Int32:
                var_val = self.read_int(4, True)
            elif var_type == ua.VariantType.UInt32:
                var_val = self.read_int(4, False)
            elif var_type == ua.VariantType.Int64:
                var_val = self.read_int(8, True)
            elif var_type == ua.VariantType.UInt64:
                var_val = self.read_int(8, False)
            elif var_type == ua.VariantType.Float:
                var_val = struct.unpack(">f", self.replay_fp.read(4))[0]
            elif var_type == ua.VariantType.Double:
                var_val = struct.unpack(">d", self.replay_fp.read(8))[0]
            elif var_type == ua.VariantType.String:
                str_len = self.read_int(4, False)
                var_val = self.replay_fp.read(str_len).decode("utf-8")
            elif var_type == ua.VariantType.DateTime:
                str_len = self.read_int(1, False)
                var_val = datetime.datetime.fromisoformat(
                    self.replay_fp.read(str_len).decode("utf-8")
                )
            update_list.append((var_name, var_val, var_good))

        if self.replay_fp.tell() == self.replay_data_file_size:
            if not self.replay_in_a_loop:
                self.replay_completed = True
            else:  # reset to the beginning of the file to replay in an infinite loop
                self.record_fp.seek(0)

        self.num_frames_read += 1
        return update_list
        # pylint: enable=R0912

    def record_frame(self, update_list: UpdateList, device: Device):
        # pylint: disable=R0912
        if not self.record:
            return

        num_vars_in_frame = len(update_list)
        self.write_int(num_vars_in_frame, 2, False)

        dev_var_types = self.var_types[device.device_type.name]
        for var_name, var_val, var_good in update_list:
            var_type, var_idx = dev_var_types[var_name]

            self.write_int(var_idx, 2, False)
            self.write_int(var_type.value, 1, False)
            self.write_int(var_good, 1, False)

            if var_type == ua.VariantType.Boolean:
                self.write_int(var_val, 1, False)
            elif var_type == ua.VariantType.SByte:
                self.write_int(var_val, 1, True)
            elif var_type == ua.VariantType.Byte:
                self.write_int(var_val, 1, False)
            elif var_type == ua.VariantType.Int16:
                self.write_int(var_val, 2, True)
            elif var_type == ua.VariantType.UInt16:
                self.write_int(var_val, 2, False)
            elif var_type == ua.VariantType.Int32:
                self.write_int(var_val, 4, True)
            elif var_type == ua.VariantType.UInt32:
                self.write_int(var_val, 4, False)
            elif var_type == ua.VariantType.Int64:
                self.write_int(var_val, 8, True)
            elif var_type == ua.VariantType.UInt64:
                self.write_int(var_val, 8, False)
            elif var_type == ua.VariantType.Float:
                self.record_fp.write(struct.pack(">f", var_val))
            elif var_type == ua.VariantType.Double:
                self.record_fp.write(struct.pack(">d", var_val))
            elif var_type == ua.VariantType.String:
                bin_val = var_val.encode("utf-8")
                self.write_int(bin_val, 4, False)
                self.record_fp.write(bin_val)
            elif var_type == ua.VariantType.DateTime:
                bin_val = var_val.isoformat().encode("utf-8")
                self.write_int(bin_val, 1, False)
                self.record_fp.write(bin_val)
        self.record_fp.flush()
        self.num_frames_write += 1
        # pylint: enable=R0912
