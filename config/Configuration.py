from pathlib import Path
from pydantic import field_serializer

import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuration(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    icons_path: Path = Path("./icons")
    specs_path: Path = Path("./specs")
    looker_size: int = 56
    looker_x: int = 0
    looker_y: int = 0
    klass: str = ""
    spec: str = ""
    toggle_keybind: str = "ctrl+alt+m"

    @field_serializer("icons_path")
    def serialize_icons_path(self, icons_path: Path, _info):
        return str(icons_path)

    @field_serializer("specs_path")
    def serialize_specs_path(self, specs_path: Path, _info):
        return str(specs_path)


def get_config(config_path: Path) -> Configuration:
    with config_path.open() as f:
        c = yaml.safe_load(f)
    return Configuration(**c)


def write_config(config: Configuration, config_path: Path):
    dumped = config.model_dump()
    with config_path.open("w") as f:
        yaml.safe_dump(dumped, f)
