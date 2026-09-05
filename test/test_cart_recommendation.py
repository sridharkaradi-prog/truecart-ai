from decimal import Decimal

from truecart_ai.domain.models import Product
from truecart_ai.services.cart_comparison import (
    CartComparisonResult,
    SplitCartItem,
)
from truecart_ai.services.cart_recommendation import (
    CartRecommendationService,
)


def test_recommends_single_retailer_when_split_saving_is_exactly_threshold() -> None:

    result = CartComparisonResult(
        items=[],
        retailer_options=[],
        cheapest_complete_retailer="zepto",
        cheapest_complete_total=Decimal("110.00"),
        split_cart=[
            SplitCartItem(
                product=Product(name="Tata Salt"),
                retailer="zepto",
                final_price=Decimal("41.00"),
            ),
            SplitCartItem(
                product=Product(name="Amul Butter"),
                retailer="blinkit",
                final_price=Decimal("64.00"),
            ),
        ],
        split_total=Decimal("105.00"),
        split_retailer_count=2,
    )

    service = CartRecommendationService()

    recommendation = service.recommend(result)

    assert recommendation.recommendation_type == (
        "single_retailer"
    )
    assert recommendation.retailer == "zepto"


def test_recommends_single_retailer_when_split_saving_is_small() -> None:

    result = CartComparisonResult(
        items=[],
        retailer_options=[],
        cheapest_complete_retailer="zepto",
        cheapest_complete_total=Decimal("107.00"),
        split_cart=[],
        split_total=Decimal("104.00"),
        split_retailer_count=2,
    )

    service = CartRecommendationService()

    recommendation = service.recommend(result)

    assert recommendation.recommendation_type == (
        "single_retailer"
    )
    assert recommendation.retailer == "zepto"
    assert recommendation.savings == Decimal("0.00")


def test_recommends_split_when_no_complete_basket_exists() -> None:

    result = CartComparisonResult(
        items=[],
        retailer_options=[],
        cheapest_complete_retailer=None,
        cheapest_complete_total=None,
        split_cart=[
            SplitCartItem(
                product=Product(name="Tata Salt"),
                retailer="blinkit",
                final_price=Decimal("46.00"),
            ),
        ],
        split_total=Decimal("46.00"),
        split_retailer_count=1,
    )

    service = CartRecommendationService()

    recommendation = service.recommend(result)

    assert recommendation.recommendation_type == (
        "split_basket"
    )
    assert recommendation.total_price == Decimal("46.00")