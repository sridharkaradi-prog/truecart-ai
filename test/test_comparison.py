from decimal import Decimal

from truecart_ai.domain.models import Price, Product, ProductOffer
from truecart_ai.services.comparison import ComparisonService


def test_finds_cheapest_available_offer() -> None:
    product = Product(name="Tata Salt", brand="Tata", quantity="1 kg")

    offers = [
        ProductOffer("blinkit", product, Price(Decimal("32.00")), True),
        ProductOffer("zepto", product, Price(Decimal("29.00")), True),
        ProductOffer("bbnow", product, Price(Decimal("35.00")), True),
    ]

    result = ComparisonService().find_best_offer(offers)

    assert result is not None
    assert result.retailer == "zepto"
    assert result.price.amount == Decimal("29.00")


def test_ignores_unavailable_offers() -> None:
    product = Product(name="Tata Salt", brand="Tata", quantity="1 kg")

    offers = [
        ProductOffer("blinkit", product, Price(Decimal("20.00")), False),
        ProductOffer("zepto", product, Price(Decimal("29.00")), True),
    ]

    result = ComparisonService().find_best_offer(offers)

    assert result is not None
    assert result.retailer == "zepto"


def test_returns_none_when_no_offers_are_available() -> None:
    assert ComparisonService().find_best_offer([]) is None
