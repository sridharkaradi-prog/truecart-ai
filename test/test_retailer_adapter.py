from truecart_ai.domain.models import Location, Product
from truecart_ai.retailers.blinkit import BlinkitAdapter


def test_blinkit_adapter_contract() -> None:
    adapter = BlinkitAdapter()

    assert adapter.retailer_name == "blinkit"

    product = Product(
        name="Tata Salt",
        brand="Tata",
        quantity="1 kg",
    )

    location = Location(
        pincode="411028",
    )

    result = adapter.search_product(product, location)

    assert result is None