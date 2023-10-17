from pydantic import BaseModel
from PIL.Image import Image


class Spell(BaseModel):
    icon: Image
    key: str


class Spec(BaseModel):
    name: str
    spells: dict[str, Spell]
