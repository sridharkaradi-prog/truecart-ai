from dataclasses import dataclass
from decimal import Decimal

from truecart_ai.domain.models import ProductOffer


@dataclass(frozen=True)
class CheckoutPrice:
    item_price: Decimal
    delivery_fee: Decimal
    handling_fee: Decimal

    @property
    def final_price(self) -> Decimal:
        return (
            self.item_price
            + self.delivery_fee
            + self.handling_fee
        )


class CheckoutPricingService:
    """
    Calculate actual checkout cost for a retailer offer.

    Fees are deterministic demo values for the MVP.
    The service boundary allows live retailer-specific fee logic later.
    """

    DELIVERY_FEES: dict[str, Decimal] = {
        "blinkit": Decimal("10.00"),
        "zepto": Decimal("8.00"),
        "instamart": Decimal("12.00"),
        "flipkart_minutes": Decimal("5.00"),
        "bbnow": Decimal("10.00"),
    }

    HANDLING_FEES: dict[str, Decimal] = {
        "blinkit": Decimal("4.00"),
        "zepto": Decimal("3.00"),
        "instamart": Decimal("5.00"),
        "flipkart_minutes": Decimal("2.00"),
        "bbnow": Decimal("4.00"),
    }

    def calculate(self, offer: ProductOffer) -> CheckoutPrice:
        retailer = offer.retailer.lower()

        delivery_fee = self.DELIVERY_FEES.get(
            retailer,
            Decimal("10.00"),
        )

        handling_fee = self.HANDLING_FEES.get(
            retailer,
            Decimal("4.00"),
        )

        return CheckoutPrice(
            item_price=offer.price.amount,
            delivery_fee=delivery_fee,
            handling_fee=handling_fee,
        )