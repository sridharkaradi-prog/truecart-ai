from concurrent.futures import ThreadPoolExecutor, TimeoutError

from truecart_ai.domain.models import (
    ComparisonResult,
    Location,
    Product,
    RetailerResult,
)
from truecart_ai.retailers.registry import RetailerRegistry
from truecart_ai.services.comparison import ComparisonService


class RetailerOrchestrator:
    """Coordinate parallel product searches across retailers."""

    def __init__(
        self,
        registry: RetailerRegistry | None = None,
        timeout_seconds: float = 10.0,
    ) -> None:
        self.registry = registry or RetailerRegistry()
        self.comparison = ComparisonService()
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

        best_offer = self.comparison.find_best_offer(offers)

        return ComparisonResult(
            best_offer=best_offer,
            retailer_results=results,
        )
