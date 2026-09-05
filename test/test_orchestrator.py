from decimal import Decimal

from truecart_ai.domain.models import (
    Location,
    Price,
    Product,
    ProductOffer,
)
from truecart_ai.retailers.registry import RetailerRegistry
from truecart_ai.services.orchestrator import (
    RetailerOrchestrator,
)


def test_orchestrator_returns_retailer_results() -> None:

    product = Product(
        name="Tata Salt",
        brand="Tata",
        quantity="1 kg",
    )

    location = Location(
        pincode="411028"
    )

    result = RetailerOrchestrator(
        RetailerRegistry()
    ).compare(
        product,
        location,
    )

    assert result.best_offer is None
    assert len(
        result.retailer_results
    ) == 5

    assert all(
        item.status == "success"
        for item in result.retailer_results
    )

    assert all(
        item.attempts == 1
        for item in result.retailer_results
    )

    assert all(
        item.duration_ms is not None
        for item in result.retailer_results
    )


def test_orchestrator_finds_best_checkout_offer() -> None:

    product = Product(
        name="Tata Salt"
    )

    location = Location(
        pincode="411028"
    )

    result = RetailerOrchestrator(
        RetailerRegistry()
    ).compare(
        product,
        location,
    )

    assert result.best_offer is None


def test_orchestrator_supports_configured_retries() -> None:

    class FailingRetailer:
        retailer_name = "test_retailer"

        def __init__(self) -> None:
            self.calls = 0

        def search_product(
            self,
            product: Product,
            location: Location,
        ):
            self.calls += 1

            raise RuntimeError(
                "temporary retailer failure"
            )

    class SingleRetailerRegistry:
        def __init__(self, retailer) -> None:
            self.retailer = retailer

        def get_all(self):
            return [self.retailer]

    retailer = FailingRetailer()

    orchestrator = RetailerOrchestrator(
        registry=SingleRetailerRegistry(
            retailer
        ),
        max_retries=2,
    )

    result = orchestrator.compare(
        Product(name="Tata Salt"),
        Location(pincode="411028"),
    )

    assert retailer.calls == 3

    assert (
        result.retailer_results[0].status
        == "failed"
    )

    assert (
        result.retailer_results[0].attempts
        == 3
    )

    assert (
        result.retailer_results[0].error
        == "temporary retailer failure"
    )


def test_orchestrator_succeeds_after_retry() -> None:

    class FlakyRetailer:
        retailer_name = "test_retailer"

        def __init__(self) -> None:
            self.calls = 0

        def search_product(
            self,
            product: Product,
            location: Location,
        ):
            self.calls += 1

            if self.calls < 2:
                raise RuntimeError(
                    "temporary failure"
                )

            return ProductOffer(
                retailer="test_retailer",
                product=product,
                price=Price(
                    amount=Decimal("25.00")
                ),
                available=True,
            )

    class SingleRetailerRegistry:
        def __init__(self, retailer) -> None:
            self.retailer = retailer

        def get_all(self):
            return [self.retailer]

    retailer = FlakyRetailer()

    orchestrator = RetailerOrchestrator(
        registry=SingleRetailerRegistry(
            retailer
        ),
        max_retries=2,
    )

    result = orchestrator.compare(
        Product(name="Tata Salt"),
        Location(pincode="411028"),
    )

    retailer_result = (
        result.retailer_results[0]
    )

    assert retailer.calls == 2
    assert retailer_result.status == "success"
    assert retailer_result.attempts == 2
    assert retailer_result.offer is not None
    assert result.best_offer is not None