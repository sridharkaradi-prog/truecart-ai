from concurrent.futures import (
    ThreadPoolExecutor,
    TimeoutError,
)
from time import perf_counter

from truecart_ai.domain.models import (
    ComparisonResult,
    Location,
    Product,
    ProductOffer,
    RetailerResult,
)
from truecart_ai.retailers.registry import RetailerRegistry
from truecart_ai.services.checkout_pricing import (
    CheckoutPricingService,
)


class RetailerOrchestrator:
    """
    Coordinate retailer searches with retries, timeout isolation,
    and execution metadata.
    """

    def __init__(
        self,
        registry: RetailerRegistry | None = None,
        timeout_seconds: float = 10.0,
        max_retries: int = 2,
    ) -> None:
        self.registry = registry or RetailerRegistry()
        self.checkout_pricing = CheckoutPricingService()
        self.timeout_seconds = timeout_seconds
        self.max_retries = max(0, max_retries)

    def _execute_attempt(
        self,
        retailer,
        product: Product,
        location: Location,
    ) -> ProductOffer | None:

        executor = ThreadPoolExecutor(
            max_workers=1
        )

        future = executor.submit(
            retailer.search_product,
            product,
            location,
        )

        try:

            return future.result(
                timeout=self.timeout_seconds
            )

        finally:

            executor.shutdown(
                wait=False,
                cancel_futures=True,
            )

    def _search_retailer(
        self,
        retailer,
        product: Product,
        location: Location,
    ) -> RetailerResult:

        started_at = perf_counter()

        total_attempts = self.max_retries + 1
        last_error: str | None = None

        for attempt in range(
            1,
            total_attempts + 1,
        ):

            try:

                offer = self._execute_attempt(
                    retailer,
                    product,
                    location,
                )

                duration_ms = (
                    perf_counter() - started_at
                ) * 1000

                return RetailerResult(
                    retailer=retailer.retailer_name,
                    status="success",
                    offer=offer,
                    attempts=attempt,
                    duration_ms=round(
                        duration_ms,
                        2,
                    ),
                )

            except TimeoutError:

                last_error = (
                    "Retailer request timed out."
                )

                if attempt == total_attempts:

                    duration_ms = (
                        perf_counter() - started_at
                    ) * 1000

                    return RetailerResult(
                        retailer=retailer.retailer_name,
                        status="timeout",
                        error=last_error,
                        attempts=attempt,
                        duration_ms=round(
                            duration_ms,
                            2,
                        ),
                    )

            except Exception as exc:

                last_error = str(exc)

                if attempt == total_attempts:

                    duration_ms = (
                        perf_counter() - started_at
                    ) * 1000

                    return RetailerResult(
                        retailer=retailer.retailer_name,
                        status="failed",
                        error=last_error,
                        attempts=attempt,
                        duration_ms=round(
                            duration_ms,
                            2,
                        ),
                    )

        duration_ms = (
            perf_counter() - started_at
        ) * 1000

        return RetailerResult(
            retailer=retailer.retailer_name,
            status="failed",
            error=(
                last_error
                or "Retailer request failed."
            ),
            attempts=total_attempts,
            duration_ms=round(
                duration_ms,
                2,
            ),
        )

    def compare(
        self,
        product: Product,
        location: Location,
    ) -> ComparisonResult:

        retailers = self.registry.get_all()

        with ThreadPoolExecutor(
            max_workers=len(retailers)
        ) as executor:

            futures = {
                executor.submit(
                    self._search_retailer,
                    retailer,
                    product,
                    location,
                ): retailer.retailer_name
                for retailer in retailers
            }

            results = [
                future.result()
                for future in futures
            ]

        offers = [
            result.offer
            for result in results
            if result.offer is not None
            and result.offer.available
        ]

        best_offer = None
        best_checkout_price = None

        for offer in offers:

            checkout_price = (
                self.checkout_pricing.calculate(
                    offer
                )
            )

            if (
                best_checkout_price is None
                or checkout_price.final_price
                < best_checkout_price
            ):

                best_offer = offer

                best_checkout_price = (
                    checkout_price.final_price
                )

        return ComparisonResult(
            best_offer=best_offer,
            retailer_results=results,
        )