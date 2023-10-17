from pathlib import Path
from pydantic import BaseModel
import yaml


class SpecKeybind(BaseModel):
    spell: str
    keybind: str
    icon_name: str = ""


class Specs(BaseModel):
    augmentation: list[SpecKeybind]


KlassesAndSpecs = dict[str, dict[str, list[SpecKeybind]]]


def get_klasses_and_specs(specs_path: Path) -> KlassesAndSpecs:
    klasses: KlassesAndSpecs = {}
    for klass_path in specs_path.glob("*.yaml"):
        klasses[klass_path.stem] = dict()
        with klass_path.open() as f:
            specs: dict[str, list] = yaml.safe_load(f)
            for spec, spell_keybinds in specs.items():
                klasses[klass_path.stem][spec] = [SpecKeybind.model_validate(s) for s in spell_keybinds]

    return klasses


def get_spec(specs_path: Path, klass: str, spec: str) -> list[SpecKeybind]:
    with (specs_path / f"{klass}.yaml").open() as f:
        specs: dict = yaml.safe_load(f)

    spec_keybinds = [SpecKeybind.model_validate(s) for s in specs[spec]]
    return spec_keybinds
