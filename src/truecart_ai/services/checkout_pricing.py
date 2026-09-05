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


@dataclass(frozen=True)
class OrderCheckoutPrice:
    item_total: Decimal
    delivery_fee: Decimal
    handling_fee: Decimal

    @property
    def final_price(self) -> Decimal:
        return (
            self.item_total
            + self.delivery_fee
            + self.handling_fee
        )


class CheckoutPricingService:
    """
    Calculate checkout costs for individual items and retailer orders.

    Item checkout pricing is used by single-product comparison.

    Order checkout pricing applies retailer delivery and handling fees
    once per retailer order, which is more realistic for basket comparison.
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

    def _fees_for_retailer(
        self,
        retailer: str,
    ) -> tuple[Decimal, Decimal]:

        retailer = retailer.lower()

        delivery_fee = self.DELIVERY_FEES.get(
            retailer,
            Decimal("10.00"),
        )

        handling_fee = self.HANDLING_FEES.get(
            retailer,
            Decimal("4.00"),
        )

        return delivery_fee, handling_fee

    def calculate(
        self,
        offer: ProductOffer,
    ) -> CheckoutPrice:

        delivery_fee, handling_fee = (
            self._fees_for_retailer(
                offer.retailer
            )
        )

        return CheckoutPrice(
            item_price=offer.price.amount,
            delivery_fee=delivery_fee,
            handling_fee=handling_fee,
        )

    def calculate_order(
        self,
        retailer: str,
        item_total: Decimal,
    ) -> OrderCheckoutPrice:

        delivery_fee, handling_fee = (
            self._fees_for_retailer(
                retailer
            )
        )

        return OrderCheckoutPrice(
            item_total=item_total,
            delivery_fee=delivery_fee,
            handling_fee=handling_fee,
        )