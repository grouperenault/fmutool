from setuptools import setup
import os
import re
from fmutool.version import __author__ as author, __version__ as default_version

try:
    version = os.environ["GITHUB_REF_NAME"]
except Exception as e:
    print(f"Cannot get repository status: {e}. Defaulting to {default_version}")
    version = default_version

if not re.match(r"[A-Za-z]?\d+(\.\d)+", version):
    print(f"WARNING: Version {version} does not match standard. The publication will fail !")
    version = default_version

# Create __version__.py
try:
    with open("fmutool/__version__.py", "wt") as file:
        print(f"'{version}'", file=file)
except Exception as e:
    print(f"Cannot create __version__.py: {e}")

setup(
    name="fmutool",
    version=version,
    packages=["fmutool"],
    package_data={"fmutool": ["resources/win32/client_sm.dll",
                              "resources/win32/server_sm.exe",
                              "resources/win64/client_sm.dll",
                              "resources/win64/server_sm.exe",
                              "resources/win64/container.dll",
                              "resources/linux64/client_sm.so",
                              "resources/linux64/server_sm",
                              "resources/linux32/client_sm.so",
                              "resources/linux32/server_sm",
                              "resources/license.txt",
                              "resources/*.png",
                              "resources/fmi-2.0/*.xsd",
                              ],
                  },
    entry_points={"console_scripts": ["fmutool = fmutool.cli:fmutool",
                                      "fmucontainer = fmutool.cli:fmucontainer"]},
    author=author,
    url="https://github.com/grouperenault/fmutool/",
    description="FMUTool is a python application which help to modify a Functional Mock-up Units (FMUs) "
                "without recompilation or to group them into FMU Containers",
    long_description="""FMUTool is a python application which help to modify a Functional Mock-up Units (FMUs) 
without recompilation. It mainly modifies the `modelDescription.xml` file. It is highly customizable.

Manipulating the `modelDescription.xml` can be a dangerous thing! Communicating with the FMU-developer and adapting
the way the FMU is generated, is the preferable when possible.

FMUTool also allows to group FMU's inside FMU Containers.
    """,
    install_requires=[
        "PyQt5 >= 5.15.10",
        "xmlschema >= 3.3.1",
        "elementpath >= 4.4.0",
        "colorama >= 0.4.6",
    ],
)

os.remove("fmutool/__version__.py")
