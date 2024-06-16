from setuptools import setup
import os
from fmutool.version import __author__ as author, __version__ as default_version

try:
    version = os.environ["CI_COMMIT_REF_NAME"] + "-" + os.environ["CI_COMMIT_SHORT_SHA"]
except Exception as e:
    print(f"Cannot get repository status: {e}")
    version = default_version

setup(
    name="fmutool",
    version=version,
    packages=["fmutool",
              ],
    package_data={"fmutool": ["remoting/win32/client_sm.dll",
                              "remoting/win32/server_sm.exe",
                              "remoting/win64/client_sm.dll",
                              "remoting/win64/server_sm.exe",
                              "remoting/license.txt",
                              "resources/*.png"],
                  },
    entry_points={"console_scripts": ["fmutool = fmutool.__main__:main"]},
    author=author,
    url="https://github.com/grouperenault/fmutool/",
)

# Create __version__.py
try:
    with open("build/fmutool/__version__.py", "wt") as file:
        print(f"'{version}'", file=file)
except Exception as e:
    print(f"Cannot create __version__.py: {e}")
