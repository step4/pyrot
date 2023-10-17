from pathlib import Path
import asyncio
import re
import json

import customtkinter
import httpx
from httpx import Response
from PIL import Image

from specs.specs import SpecKeybind


customtkinter.set_default_color_theme("dark-blue")


async def get_class_spell_icon_names(klass: str) -> list[str]:
    async with httpx.AsyncClient() as c:
        r = await c.get(f"https://www.wowhead.com/icons/name:{klass}")
    res = re.search(r"new Listview\(\s?.*data:(.*)}\s?\);", r.text)
    if not res:
        raise ValueError("No class list found in result")

    spells_list = json.loads(res.group(1))
    return [s["icon"] for s in spells_list]


async def get_spell_icons(klass: str, names: list[str], save_path: Path):
    async with httpx.AsyncClient() as c:
        results: list[Response] = await asyncio.gather(
            *[c.get(f"https://wow.zamimg.com/images/wow/icons/large/{name}.jpg") for name in names]
        )

    for res, name in zip(results, names):
        with (save_path / f"{name}.jpg").open("wb") as f:
            f.write(res.content)


async def get_klass_spell_icons(klass: str, icon_path: Path):
    klass_path = icon_path / klass
    if not klass_path.exists():
        klass_path.mkdir()

    names = await get_class_spell_icon_names(klass)
    await get_spell_icons(klass, names, klass_path)


def load_spell_icons_by_spec(
    icons_path: Path, klass: str, spec: list[SpecKeybind]
) -> list[tuple[SpecKeybind, Image.Image]]:
    spec_with_icons: list[tuple[SpecKeybind, Image.Image]] = []
    for spec_keybind in spec:
        icon = next((icons_path / klass).glob(f"ability_{klass}_{spec_keybind.spell}.jpg"), None)
        if not icon:
            raise ValueError(f"Icon for spell {spec_keybind.spell} not found in klass {klass}")
        spec_with_icons.append((spec_keybind, Image.open(icon)))

    return spec_with_icons


if __name__ == "__main__":
    asyncio.run(get_klass_spell_icons("evoker", Path("./icons")))
