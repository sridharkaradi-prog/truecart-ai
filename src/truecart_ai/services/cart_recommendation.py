from dataclasses import dataclass
from decimal import Decimal

from truecart_ai.services.cart_comparison import (
    CartComparisonResult,
)


@dataclass(frozen=True)
class CartRecommendation:
    recommendation_type: str
    retailer: str | None
    total_price: Decimal | None
    savings: Decimal
    savings_percentage: Decimal
    retailer_count: int
    reason: str


class CartRecommendationService:
    """
    Decide whether a shopper should use one retailer
    or split the basket across retailers.

    The recommendation layer is intentionally separate from
    the underlying price calculations so the decision policy
    can evolve independently.
    """

    def __init__(
        self,
        minimum_split_savings: Decimal = Decimal("5.00"),
    ) -> None:
        self.minimum_split_savings = (
            minimum_split_savings
        )

    def recommend(
        self,
        result: CartComparisonResult,
    ) -> CartRecommendation:

        complete_total = (
            result.cheapest_complete_total
        )

        split_total = result.split_total

        if split_total is None:

            if complete_total is not None:

                return CartRecommendation(
                    recommendation_type="single_retailer",
                    retailer=(
                        result.cheapest_complete_retailer
                    ),
                    total_price=complete_total,
                    savings=Decimal("0.00"),
                    savings_percentage=Decimal("0.00"),
                    retailer_count=1,
                    reason=(
                        "A complete basket is available "
                        "from one retailer."
                    ),
                )

            return CartRecommendation(
                recommendation_type="unavailable",
                retailer=None,
                total_price=None,
                savings=Decimal("0.00"),
                savings_percentage=Decimal("0.00"),
                retailer_count=0,
                reason=(
                    "The basket cannot be fulfilled "
                    "with the available retailer offers."
                ),
            )

        if complete_total is None:

            return CartRecommendation(
                recommendation_type="split_basket",
                retailer=None,
                total_price=split_total,
                savings=Decimal("0.00"),
                savings_percentage=Decimal("0.00"),
                retailer_count=(
                    result.split_retailer_count
                ),
                reason=(
                    "No single retailer has every "
                    "product, so the basket should be split."
                ),
            )

        savings = (
            complete_total - split_total
        )

        if savings <= 0:

            return CartRecommendation(
                recommendation_type="single_retailer",
                retailer=(
                    result.cheapest_complete_retailer
                ),
                total_price=complete_total,
                savings=Decimal("0.00"),
                savings_percentage=Decimal("0.00"),
                retailer_count=1,
                reason=(
                    "Splitting the basket does not reduce "
                    "the total checkout cost."
                ),
            )

        savings_percentage = (
            savings / complete_total * Decimal("100")
        )

        if savings <= self.minimum_split_savings:

            return CartRecommendation(
                recommendation_type="single_retailer",
                retailer=(
                    result.cheapest_complete_retailer
                ),
                total_price=complete_total,
                savings=Decimal("0.00"),
                savings_percentage=Decimal("0.00"),
                retailer_count=1,
                reason=(
                    "The split basket saves only "
                    f"₹{savings:.2f}, which is below "
                    "the minimum savings threshold."
                ),
            )

        return CartRecommendation(
            recommendation_type="split_basket",
            retailer=None,
            total_price=split_total,
            savings=savings,
            savings_percentage=savings_percentage,
            retailer_count=result.split_retailer_count,
            reason=(
                f"Splitting the basket saves "
                f"₹{savings:.2f} compared with the "
                "cheapest complete retailer."
            ),
        )