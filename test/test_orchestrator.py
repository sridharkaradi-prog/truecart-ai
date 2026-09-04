from truecart_ai.domain.models import Location, Product
from truecart_ai.retailers.registry import RetailerRegistry
from truecart_ai.services.orchestrator import RetailerOrchestrator


def test_orchestrator_returns_retailer_results() -> None:
    product = Product(
        name="Tata Salt",
        brand="Tata",
        quantity="1 kg",
    )

    location = Location(pincode="411028")

    result = RetailerOrchestrator(
        RetailerRegistry()
    ).compare(product, location)

    assert result.best_offer is None
    assert len(result.retailer_results) == 5

    assert all(
        item.status == "success"
        for item in result.retailer_results
    )
