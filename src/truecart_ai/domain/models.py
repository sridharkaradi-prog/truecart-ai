from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class Location:
    pincode: str
    country: str = "IN"

    def __post_init__(self) -> None:
        if self.country == "IN":
            if not self.pincode.isdigit() or len(self.pincode) != 6:
                raise ValueError("Indian pincode must be exactly 6 digits.")


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


@dataclass(frozen=True)
class RetailerResult:
    retailer: str
    status: str
    offer: Optional[ProductOffer] = None
    error: Optional[str] = None


@dataclass(frozen=True)
class ComparisonResult:
    best_offer: Optional[ProductOffer]
    retailer_results: list[RetailerResult]
