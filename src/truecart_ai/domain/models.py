from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class Product:
    name: str
    brand: Optional[str] = None
    quantity: Optional[str] = None


@dataclass(frozen=True)
class Price:
    amount: Decimal
    currency: str = "INR"


@dataclass(frozen=True)
class ProductOffer:
    retailer: str
    product: Product
    price: Price
    available: bool
    product_url: Optional[str] = None