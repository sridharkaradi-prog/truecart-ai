from decimal import Decimal

from truecart_ai.domain.models import (
    Location,
    Price,
    Product,
    ProductOffer,
)
from truecart_ai.retailers.base import RetailerAdapter


class DemoRetailerAdapter(RetailerAdapter):
    """Deterministic demo adapter for end-to-end MVP validation."""

    def __init__(self, retailer: str, price: str) -> None:
        self._retailer = retailer
        self._price = Decimal(price)

    @property
    def retailer_name(self) -> str:
        return self._retailer

    def search_product(
        self,
        product: Product,
        location: Location,
    ) -> ProductOffer | None:
        return ProductOffer(
            retailer=self._retailer,
            product=product,
            price=Price(amount=self._price),
            available=True,
            product_url=None,
        )
