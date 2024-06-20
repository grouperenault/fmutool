from setuptools import setup
import os
import sys
import re
from fmutool.version import __author__ as author, __version__ as default_version

try:
    version = os.environ["GITHUB_REF_NAME"]
except Exception as e:
    print(f"Cannot get repository status: {e}. Defaulting to {default_version}")
    version = default_version

if not re.match(r"[A-Za-z]?\d+(\.\d)+", version):
    print(f"Version {version} does not match standard. ABORT.")
    sys.exit(-1)

# Create __version__.py
try:
    with open("fmutool/__version__.py", "wt") as file:
        print(f"'{version}'", file=file)
except Exception as e:
    print(f"Cannot create __version__.py: {e}")

setup(
    name="fmutool",
    version=version,
    packages=["fmutool",
              ],
    package_data={"fmutool": ["remoting/win32/client_sm.dll",
                              "remoting/win32/server_sm.exe",
                              "remoting/win64/client_sm.dll",
                              "remoting/win64/server_sm.exe",
                              "remoting/linux64/client_sm.so",
                              "remoting/linux64/server_sm",
                              "remoting/linux32/client_sm.so",
                              "remoting/linux32/server_sm",
                              "remoting/license.txt",
                              "resources/*.png"],
                  },
    entry_points={"console_scripts": ["fmutool = fmutool.__main__:main"]},
    author=author,
    url="https://github.com/grouperenault/fmutool/",
    long_description="""FMUTool is a python application which help to modify a FMU without recompilation.
It mainly modifies the `modelDescription.xml` file. It is highly customizable.

Manipulating the `modelDescription.xml` can be a dangerous thing! Communicating with the FMU-developer and adapting
the way the FMU is generated, is the preferable when possible.
    """,
)

os.remove("fmutool/__version__.py")
