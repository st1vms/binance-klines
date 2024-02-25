"""setup.py"""

from os import getenv
from os.path import dirname, join, abspath
from setuptools import setup, find_packages

__DESCRIPTION = """Binance Klines getter"""
__PROJECT_NAME = "binance-klines"
__MIN_PY_VERSION = "3.10"

with open(
    join(abspath(dirname(__file__)), "README.md"),
    "r",
    encoding="utf-8",
    errors="ignore",
) as fp:
    __LONG_DESCRIPTION = fp.read().lstrip().rstrip()

# Get the Scripts folder from path environment variable
path_env = getenv("PATH")
path_dirs = list(filter(bool, map(str.strip, path_env.split(";"))))
for d in path_dirs:
    if d.find("Scripts") != -1:
        break

setup(
    name=__PROJECT_NAME,
    version="0.1.0",
    author="st1vms",
    author_email="stefano.maria.salvatore@gmail.com",
    description=__DESCRIPTION,
    long_description=__LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url=f"https://github.com/st1vms/{__PROJECT_NAME}",
    packages=find_packages(),
    classifiers=[
        f"Programming Language :: Python :: {__MIN_PY_VERSION}",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={"console_scripts": ["binance-klines=binance_klines.cli.cli:main"]},
    python_requires=f">={__MIN_PY_VERSION}",
    install_requires=[
        "colorlog",
    ],
)
