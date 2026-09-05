from truecart_ai.domain.models import Location
from truecart_ai.services.product_search import (
    ProductSearchService,
    ProductSuggestion,
)


def test_product_search_returns_matching_products() -> None:
    service = ProductSearchService(
        [
            ProductSuggestion(
                name="Tata Salt 1 kg",
                brand="Tata",
                quantity="1 kg",
                retailer="blinkit",
                source="catalogue",
            ),
            ProductSuggestion(
                name="Aashirvaad Shudh Chakki Atta 5 kg",
                brand="Aashirvaad",
                quantity="5 kg",
                retailer="zepto",
                source="catalogue",
            ),
        ]
    )

    results = service.suggest(
        query="tata",
        location=Location(pincode="411028"),
    )

    assert len(results) == 1
    assert results[0].name == "Tata Salt 1 kg"
    assert results[0].retailer == "blinkit"


def test_product_search_returns_empty_for_short_query() -> None:
    service = ProductSearchService(
        [
            ProductSuggestion(
                name="Tata Salt 1 kg",
                brand="Tata",
                quantity="1 kg",
                retailer="blinkit",
                source="catalogue",
            )
        ]
    )

    results = service.suggest(
        query="t",
        location=Location(pincode="411028"),
    )

    assert results == []


def test_product_search_matches_brand() -> None:
    service = ProductSearchService(
        [
            ProductSuggestion(
                name="Tata Salt 1 kg",
                brand="Tata",
                quantity="1 kg",
                retailer="blinkit",
                source="catalogue",
            )
        ]
    )

    results = service.suggest(
        query="Tata",
        location=Location(pincode="411028"),
    )

    assert results
    assert results[0].brand == "Tata"