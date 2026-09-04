from truecart_ai.domain.models import Product
from truecart_ai.retailers.blinkit import BlinkitAdapter


def test_blinkit_adapter_contract() -> None:
    adapter = BlinkitAdapter()

    assert adapter.retailer_name == "blinkit"

    product = Product(
        name="Tata Salt",
        brand="Tata",
        quantity="1 kg",
    )

    result = adapter.search_product(product)

    assert result is None