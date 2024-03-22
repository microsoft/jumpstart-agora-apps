import re
from setuptools import setup
from pkg_resources import parse_requirements


def read_file(file_path):
    with open(file_path, encoding="utf-8") as fp:
        return fp.read()


init_content = read_file("eclipse_opcua/__init__.py")
version = re.search(r'^__version__\s*=\s*"(.*)"', init_content, re.M).group(1)
requirements = [str(ir) for ir in parse_requirements(read_file("requirements.txt"))]

setup(
    name="eclipse_opcua",
    packages=["eclipse_opcua"],
    entry_points={
        "console_scripts": [
            "plc_server = eclipse_opcua.plc_server_controller:main",
            "sim_server = eclipse_opcua.sim_server_controller:main",
            "test_harness = eclipse_opcua.test_harness:main",
        ]
    },
    install_requires=requirements,
    include_package_data=True,
    version=version,
    description="OPCUA servers with DI companion spec for IMV development",
    long_description=read_file("README.md"),
    author="Eclipse Crew",
    author_email="eclipse@microsoft.com",
    url="https://www.microsoft.com",
)
