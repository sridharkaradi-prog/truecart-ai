from decimal import Decimal

from truecart_ai.domain.models import Price, Product, ProductOffer
from truecart_ai.services.checkout_pricing import (
    CheckoutPricingService,
)


def test_checkout_price_calculates_total() -> None:

    service = CheckoutPricingService()

    offer = ProductOffer(
        retailer="zepto",
        product=Product(name="Tata Salt 1 kg"),
        price=Price(
            amount=Decimal("30.00")
        ),
        available=True,
    )

    result = service.calculate(offer)

    assert result.item_price == Decimal("30.00")
    assert result.delivery_fee == Decimal("8.00")
    assert result.handling_fee == Decimal("3.00")
    assert result.final_price == Decimal("41.00")


def test_checkout_pricing_differs_by_retailer() -> None:

    service = CheckoutPricingService()

    blinkit_offer = ProductOffer(
        retailer="blinkit",
        product=Product(name="Tata Salt 1 kg"),
        price=Price(
            amount=Decimal("32.00")
        ),
        available=True,
    )

    zepto_offer = ProductOffer(
        retailer="zepto",
        product=Product(name="Tata Salt 1 kg"),
        price=Price(
            amount=Decimal("30.00")
        ),
        available=True,
    )

    blinkit = service.calculate(
        blinkit_offer
    )

    zepto = service.calculate(
        zepto_offer
    )

    assert blinkit.final_price == Decimal("46.00")
    assert zepto.final_price == Decimal("41.00")


def test_order_checkout_charges_fees_once() -> None:

    service = CheckoutPricingService()

    result = service.calculate_order(
        retailer="zepto",
        item_total=Decimal("85.00"),
    )

    assert result.item_total == Decimal("85.00")
    assert result.delivery_fee == Decimal("8.00")
    assert result.handling_fee == Decimal("3.00")
    assert result.final_price == Decimal("96.00")