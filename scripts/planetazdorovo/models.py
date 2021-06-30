from dataclasses import dataclass


@dataclass
class ItemModel:
    url: str
    image_url: str
    title: str
    price: float
