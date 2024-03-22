from __future__ import annotations  # for Python 3.7-3.9

from typing import Literal, List, Any, Dict
from typing_extensions import NotRequired, TypedDict  # for Python <3.11 with (Not)Required

# pylint: disable=too-few-public-methods


LogLevelType = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class VarTypeConfig(TypedDict):
    """
    Device's variable definition
    """

    Name: str
    """Name of the device variable"""

    Type: Literal[
        "Boolean",
        "SByte",
        "Byte",
        "Int16",
        "UInt16",
        "Int32",
        "UInt32",
        "Int64",
        "UInt64",
        "Float",
        "Double",
        "String",
        "DateTime",
    ]
    """Type of the device variable"""

    Value: Any
    """Initial value of the variable when the device type is instantiated"""

    Writable: NotRequired[bool]
    """If true, make the OPCUA variable writable. Default is False"""


class ServerConfig(TypedDict):
    # TODO(someone): this is the perfect place to add options such
    # as server certificates, username and password, etc.

    Name: NotRequired[str]
    """
    Name of the OPCUA server
    Default: "An OPC UA server"
    """

    Endpoint: NotRequired[str]
    """
    Endpoint for the OPCUA server
    Default: "opc.tcp://0.0.0.0:4840"
    """

    CustomNamespace: NotRequired[str]
    """
    Namespace for the device type and instance nodes added
    Default: "http://microsoft.com/Opc/Simulator/"
    """


class DeviceTypeConfig(TypedDict):
    """
    Defines a device type (see https://reference.opcfoundation.org/DI/v102/docs/)
    """

    DeviceType: str
    """Name of this device type (e.g. "Thermostat") """

    Variables: List[VarTypeConfig]
    """List of parameters (OPCUA variables) this device type defines
    At least one variable should be defined for a device type to be valid"""


class DeviceConfig(TypedDict):
    """
    Defines a device instance
    """

    Name: str
    """Name of this device instance"""

    DeviceType: str
    """Name of the device type to instantiate (should be defined in the configuration)"""

    Properties: NotRequired[List[VarTypeConfig]]
    """(Optional) Device properties to set
    For example, "[{ "Name": "SerialNumber", "Value": "C3PO", "Type": "String" }]
    will set the "SerialNumber" attribute of this device to "C3PO"
    """


class SimulationSource(TypedDict):
    """
    Defines a simulation source to target one or more variables in one or more devices
    """

    TargetDevices: List[str]
    """List of device instances (by name) this simulation source is applied to"""

    TargetVariables: List[str]
    """List of variable names this device simulation source is applied to"""

    ValueSequence: List[Any]
    """List of values the variable(s) will be updated with.
    Values are cycled through multiple times unless `RepeatForever` is set to False.
    """

    UpdatePeriodSeconds: List[float]
    """List of update periods to update the variable attached to this simulation source
    For example, [0.5, 1.0] means that ValueSequence[0] will be set, and 0.5 seconds later
    ValueSequence[1]  will be set and 1.0 seconds later ValueSequence[2] will be set,
    and 0.5 seconds later ValueSequence[3] will be set and so on. That is, update periods
    are cycled over and over just like the value sequence.
    """

    RepeatForever: NotRequired[bool]
    """
    If set to False, the simulation source stops updating the variable(s) after all values
    in the sequence have been used. By default it is set to true, meaning
    cycle the value sequence and update periods until the server is stopped"""


class RunSettings(TypedDict):
    PollIntervalSeconds: NotRequired[float]
    """
    Polling interval in seconds (i.e. controls how often to check for variable updates)
    Using zero or a negative value means poll for variable updates as fast as possible (i.e.)
    Default: 0.1 => poll at 10Hz
    """

    ReportUsageIntervalSeconds: NotRequired[float]
    """
    Controls how may seconds to report poll period utilization or polling rate
    (if the polling interval is a positive value or not) in the command line log
    Default: 5.0 => display a message every 5 seconds
    """

    AsyncuaLoggingLevel: NotRequired[LogLevelType]
    """
    Logging level for the asyncua (Python's OPCUA implementation) logger
    Default: "WARNING"
    """

    StopSimulatorAfterFullLoop: NotRequired[bool]
    """
    Stop the server simulation loop after all value sequences has been played at least once
    Default: False => Runs the OPCUA server until it is stopped by the user
    """

    SimulationSources: NotRequired[List[SimulationSource]]
    """
    List of simulation sources that will generate data for devices' variables
    Default: [] => No data will change when running in simulatio mode
    """


class PLCSettings(TypedDict):
    """Configuration options to use the OPCUA server to exponse PLC tag data
    A configuration is created on the fly mapping PLC tags to OPCUA server variables
    Currently the PLC is exposed as ONE OPCUA device with all tags shown as a variable
    in the device's `ParameterSet` node.
    """

    IPAddress: str
    """IP Address of the PLC to connect to"""

    DeviceTypeName: str
    """Name of the device type (display name of the OPCUA node
    representing the device type)"""

    DeviceInstanceName: str
    """Name of the device instance (display name of the OPCUA node
    representing the device instance)"""

    DumpDeviceConfigFilePath: NotRequired[str]
    """If specified, the on-the-fly configuration can be dumped to file
    This is useful if you want to collect real-time data and later replay using the simulator
    """

    WritableTags: NotRequired[List[str]]
    """
    Specify which tags are writable (from the OPCUA server to the PLC)
    """

    TagPlcToOpcuaMapping: Dict[str, str]
    """Mapping from PLC tag name to OPCUA variable name"""


class AppConfiguration(TypedDict):
    """
    Application configuration object
    """

    DeviceTypes: List[DeviceTypeConfig]
    """List of device types the OPCUA server will expose"""

    Devices: List[DeviceConfig]
    """List of device instances the OPCUA server will expose"""

    Server: NotRequired[ServerConfig]
    """Configuration settings for the OPCUA server such as endpoint, namespace, etc."""

    RunSettings: NotRequired[RunSettings]
    """Run settings to control how device variables are updated"""

    PLCSettings: NotRequired[PLCSettings]
    """If exposing data from a Rockwell PLC, configuration on how to map PLC tags to
    the OPCUA information model"""


# pylint: enable=too-few-public-methods
