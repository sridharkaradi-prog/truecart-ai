from concurrent.futures import ThreadPoolExecutor, TimeoutError

from truecart_ai.domain.models import (
    ComparisonResult,
    Location,
    Product,
    RetailerResult,
)
from truecart_ai.retailers.registry import RetailerRegistry
from truecart_ai.services.checkout_pricing import CheckoutPricingService


class RetailerOrchestrator:
    """Coordinate parallel product searches across retailers."""

    def __init__(
        self,
        registry: RetailerRegistry | None = None,
        timeout_seconds: float = 10.0,
    ) -> None:
        self.registry = registry or RetailerRegistry()
        self.checkout_pricing = CheckoutPricingService()
        self.timeout_seconds = timeout_seconds

    def compare(
        self,
        product: Product,
        location: Location,
    ) -> ComparisonResult:
        retailers = self.registry.get_all()

        with ThreadPoolExecutor(max_workers=len(retailers)) as executor:
            futures = {
                executor.submit(
                    retailer.search_product,
                    product,
                    location,
                ): retailer.retailer_name
                for retailer in retailers
            }

            results: list[RetailerResult] = []

            for future, retailer_name in futures.items():
                try:
                    offer = future.result(timeout=self.timeout_seconds)

                    results.append(
                        RetailerResult(
                            retailer=retailer_name,
                            status="success",
                            offer=offer,
                        )
                    )

                except TimeoutError:
                    results.append(
                        RetailerResult(
                            retailer=retailer_name,
                            status="timeout",
                            error="Retailer request timed out.",
                        )
                    )

                except Exception as exc:
                    results.append(
                        RetailerResult(
                            retailer=retailer_name,
                            status="failed",
                            error=str(exc),
                        )
                    )

            offers = [
                result.offer
                for result in results
                if result.offer is not None
            ]

        best_offer = None
        best_checkout_price = None

        for offer in offers:
            checkout_price = self.checkout_pricing.calculate(offer)

            if (
                best_checkout_price is None
                or checkout_price.final_price < best_checkout_price
            ):
                best_offer = offer
                best_checkout_price = checkout_price.final_price

        return ComparisonResult(
            best_offer=best_offer,
            retailer_results=results,
        )