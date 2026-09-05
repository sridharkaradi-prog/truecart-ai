from dataclasses import dataclass
from decimal import Decimal

from truecart_ai.domain.models import ComparisonResult, Product
from truecart_ai.services.checkout_pricing import (
    CheckoutPricingService,
)


@dataclass(frozen=True)
class CartItemResult:
    product: Product
    comparison: ComparisonResult


@dataclass(frozen=True)
class RetailerCartOption:
    retailer: str
    total_price: Decimal
    available_items: int
    missing_items: int


@dataclass(frozen=True)
class SplitCartItem:
    product: Product
    retailer: str
    final_price: Decimal


@dataclass(frozen=True)
class CartComparisonResult:
    items: list[CartItemResult]
    retailer_options: list[RetailerCartOption]
    cheapest_complete_retailer: str | None
    cheapest_complete_total: Decimal | None
    split_cart: list[SplitCartItem]
    split_total: Decimal | None
    split_retailer_count: int


class CartComparisonService:
    """
    Compare a basket across retailers.

    Retailer delivery and handling fees are charged once per
    retailer order rather than once per individual product.
    """

    def __init__(
        self,
        checkout_pricing: CheckoutPricingService | None = None,
    ) -> None:
        self.checkout_pricing = (
            checkout_pricing or CheckoutPricingService()
        )

    def compare(
        self,
        products: list[Product],
        comparisons: list[ComparisonResult],
    ) -> CartComparisonResult:

        if len(products) != len(comparisons):
            raise ValueError(
                "Each product must have exactly one comparison result."
            )

        items = [
            CartItemResult(
                product=product,
                comparison=comparison,
            )
            for product, comparison in zip(
                products,
                comparisons,
                strict=True,
            )
        ]

        retailer_names = sorted(
            {
                result.retailer
                for comparison in comparisons
                for result in comparison.retailer_results
            }
        )

        retailer_options: list[RetailerCartOption] = []

        for retailer in retailer_names:

            item_total = Decimal("0.00")
            available_items = 0
            missing_items = 0

            for comparison in comparisons:

                retailer_result = next(
                    (
                        result
                        for result in comparison.retailer_results
                        if result.retailer == retailer
                    ),
                    None,
                )

                if (
                    retailer_result is not None
                    and retailer_result.offer is not None
                    and retailer_result.offer.available
                ):
                    item_total += (
                        retailer_result.offer.price.amount
                    )
                    available_items += 1

                else:
                    missing_items += 1

            if available_items > 0:
                order_total = (
                    self.checkout_pricing.calculate_order(
                        retailer=retailer,
                        item_total=item_total,
                    )
                )

                total_price = order_total.final_price

            else:
                total_price = Decimal("0.00")

            retailer_options.append(
                RetailerCartOption(
                    retailer=retailer,
                    total_price=total_price,
                    available_items=available_items,
                    missing_items=missing_items,
                )
            )

        retailer_options.sort(
            key=lambda option: (
                option.missing_items,
                option.total_price,
                option.retailer,
            )
        )

        complete_options = [
            option
            for option in retailer_options
            if option.missing_items == 0
        ]

        if complete_options:

            best_complete = min(
                complete_options,
                key=lambda option: option.total_price,
            )

            cheapest_complete_retailer = (
                best_complete.retailer
            )

            cheapest_complete_total = (
                best_complete.total_price
            )

        else:

            cheapest_complete_retailer = None
            cheapest_complete_total = None

        split_cart: list[SplitCartItem] = []

        for item in items:

            available_offers = [
                result
                for result in item.comparison.retailer_results
                if (
                    result.offer is not None
                    and result.offer.available
                )
            ]

            if not available_offers:
                continue

            best_result = min(
                available_offers,
                key=lambda result: (
                    result.offer.price.amount
                ),
            )

            split_cart.append(
                SplitCartItem(
                    product=item.product,
                    retailer=best_result.retailer,
                    final_price=(
                        best_result.offer.price.amount
                    ),
                )
            )

        if len(split_cart) == len(items) and split_cart:

            item_totals_by_retailer: dict[
                str,
                Decimal,
            ] = {}

            for item in split_cart:

                item_totals_by_retailer[
                    item.retailer
                ] = (
                    item_totals_by_retailer.get(
                        item.retailer,
                        Decimal("0.00"),
                    )
                    + item.final_price
                )

            split_total = Decimal("0.00")

            for retailer, item_total in (
                item_totals_by_retailer.items()
            ):

                order_total = (
                    self.checkout_pricing.calculate_order(
                        retailer=retailer,
                        item_total=item_total,
                    )
                )

                split_total += order_total.final_price

            split_retailer_count = len(
                item_totals_by_retailer
            )

        else:

            split_total = None
            split_retailer_count = 0

        return CartComparisonResult(
            items=items,
            retailer_options=retailer_options,
            cheapest_complete_retailer=(
                cheapest_complete_retailer
            ),
            cheapest_complete_total=(
                cheapest_complete_total
            ),
            split_cart=split_cart,
            split_total=split_total,
            split_retailer_count=split_retailer_count,
        )