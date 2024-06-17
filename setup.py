from setuptools import setup
import os
from fmutool.version import __author__ as author, __version__ as default_version

try:
    version = os.environ["GITHUB_REF_NAME"]
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
)

# Create __version__.py
try:
    with open("build/fmutool/__version__.py", "wt") as file:
        print(f"'{version}'", file=file)
except Exception as e:
    print(f"Cannot create __version__.py: {e}")
