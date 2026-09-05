from dataclasses import dataclass
from decimal import Decimal

from truecart_ai.services.cart_comparison import (
    CartComparisonResult,
)


@dataclass(frozen=True)
class DecisionTrace:
    step: str
    detail: str


@dataclass(frozen=True)
class CartRecommendation:
    recommendation_type: str
    retailer: str | None
    total_price: Decimal | None
    savings: Decimal
    savings_percentage: Decimal
    retailer_count: int
    reason: str
    decision_trace: list[DecisionTrace]


class CartRecommendationService:
    """
    Decide whether a shopper should use one retailer
    or split the basket across retailers.

    The service also produces a decision trace so that
    the recommendation is explainable and auditable.
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

        trace: list[DecisionTrace] = []

        trace.append(
            DecisionTrace(
                step="basket_scope",
                detail=(
                    f"Evaluated {len(result.items)} "
                    "product(s) across available retailers."
                ),
            )
        )

        complete_total = (
            result.cheapest_complete_total
        )

        split_total = result.split_total

        if complete_total is not None:

            trace.append(
                DecisionTrace(
                    step="complete_basket",
                    detail=(
                        "A complete basket is available from "
                        f"{result.cheapest_complete_retailer} "
                        f"for ₹{complete_total:.2f}."
                    ),
                )
            )

        else:

            trace.append(
                DecisionTrace(
                    step="complete_basket",
                    detail=(
                        "No single retailer can fulfill "
                        "the complete basket."
                    ),
                )
            )

        if split_total is not None:

            trace.append(
                DecisionTrace(
                    step="split_basket",
                    detail=(
                        f"The cheapest split basket costs "
                        f"₹{split_total:.2f} across "
                        f"{result.split_retailer_count} retailer(s)."
                    ),
                )
            )

        else:

            trace.append(
                DecisionTrace(
                    step="split_basket",
                    detail=(
                        "A complete split basket could not "
                        "be constructed."
                    ),
                )
            )

        if split_total is None:

            if complete_total is not None:

                trace.append(
                    DecisionTrace(
                        step="decision",
                        detail=(
                            "Selected the complete retailer "
                            "because no valid split basket exists."
                        ),
                    )
                )

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
                    decision_trace=trace,
                )

            trace.append(
                DecisionTrace(
                    step="decision",
                    detail=(
                        "No recommendation is possible because "
                        "the basket cannot currently be fulfilled."
                    ),
                )
            )

            return CartRecommendation(
                recommendation_type="unavailable",
                retailer=None,
                total_price=None,
                savings=Decimal("0.00"),
                savings_percentage=Decimal("0.00"),
                retailer_count=0,
                reason=(
                    "The basket cannot be fulfilled with "
                    "the available retailer offers."
                ),
                decision_trace=trace,
            )

        if complete_total is None:

            trace.append(
                DecisionTrace(
                    step="decision",
                    detail=(
                        "Selected split basket because no "
                        "single retailer has every product."
                    ),
                )
            )

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
                    "No single retailer has every product, "
                    "so the basket should be split."
                ),
                decision_trace=trace,
            )

        savings = (
            complete_total - split_total
        )

        trace.append(
            DecisionTrace(
                step="savings_analysis",
                detail=(
                    f"Splitting changes the total by "
                    f"₹{savings:.2f} compared with the "
                    "cheapest complete retailer."
                ),
            )
        )

        if savings <= 0:

            trace.append(
                DecisionTrace(
                    step="decision",
                    detail=(
                        "Selected the single retailer because "
                        "splitting does not reduce checkout cost."
                    ),
                )
            )

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
                decision_trace=trace,
            )

        savings_percentage = (
            savings / complete_total
            * Decimal("100")
        )

        trace.append(
            DecisionTrace(
                step="threshold_check",
                detail=(
                    f"Required split saving: "
                    f"₹{self.minimum_split_savings:.2f}. "
                    f"Calculated saving: ₹{savings:.2f}."
                ),
            )
        )

        if savings <= self.minimum_split_savings:

            trace.append(
                DecisionTrace(
                    step="decision",
                    detail=(
                        "Selected the single retailer because "
                        "the split saving does not exceed the "
                        "minimum savings threshold."
                    ),
                )
            )

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
                    "The split basket does not provide enough "
                    "savings to justify an additional checkout."
                ),
                decision_trace=trace,
            )

        trace.append(
            DecisionTrace(
                step="decision",
                detail=(
                    "Selected the split basket because the "
                    "savings exceed the configured threshold."
                ),
            )
        )

        return CartRecommendation(
            recommendation_type="split_basket",
            retailer=None,
            total_price=split_total,
            savings=savings,
            savings_percentage=savings_percentage,
            retailer_count=(
                result.split_retailer_count
            ),
            reason=(
                f"Splitting the basket saves "
                f"₹{savings:.2f} compared with the "
                "cheapest complete retailer."
            ),
            decision_trace=trace,
        )