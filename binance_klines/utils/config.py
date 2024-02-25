"""Configuration module, also a wrapper for configparser"""

from os import path as ospath
from os import getcwd
from abc import ABC
from typing import TypeVar, Annotated
from configparser import ConfigParser
from dataclasses import dataclass, fields, field

# Config loader utility function

CONFIG_PARSER = ConfigParser(allow_no_value=True)


@dataclass
class ConfigObject(ABC):
    """Base configuration object type to extend"""

    config_file_path: str = field(
        init=False,
        repr=False,
        compare=False,
        default=ospath.join(getcwd(), "config.ini"),
    )
    section: str = field(init=False, repr=False, compare=False)

    def __post_init__(self):
        self.load_configuration()

    __ConfigObjectT = TypeVar(
        "__ConfigObjectT", bound=Annotated[dataclass, "ConfigObject"]
    )

    def load_configuration(self: __ConfigObjectT) -> __ConfigObjectT:
        """Retrieves configuration object from config.ini file"""

        section = getattr(self, "section")
        if not section or not isinstance(section, str):
            raise ValueError(
                f"{self.__class__.__name__} does not have a section string property!"
            )

        if ospath.exists(self.config_file_path):
            CONFIG_PARSER.read(self.config_file_path, encoding="utf-8")
            if not CONFIG_PARSER.sections():
                return

        args = {}
        for f in fields(self):
            if f.name in {"section", "config_file_path"}:
                continue

            if f.type == int:
                args[f.name] = CONFIG_PARSER.getint(section, f.name, fallback=f.default)
            elif f.type == float:
                args[f.name] = CONFIG_PARSER.getfloat(
                    section, f.name, fallback=f.default
                )
            elif f.type == str:
                args[f.name] = CONFIG_PARSER.get(section, f.name, fallback=f.default)
            elif f.type == bool:
                args[f.name] = CONFIG_PARSER.getboolean(
                    section, f.name, fallback=f.default
                )
            elif issubclass(f.type, ConfigObject):
                args[f.name] = f.type()

        for k, v in args.items():
            setattr(self, k, v)
