from truecart_ai.domain.models import Product, ProductOffer
from truecart_ai.retailers.base import RetailerAdapter


class BlinkitAdapter(RetailerAdapter):
    """Blinkit retailer adapter."""

    @property
    def retailer_name(self) -> str:
        return "blinkit"

    def search_product(self, product: Product) -> ProductOffer | None:
        # Retrieval implementation will be added separately.
        # This keeps retailer access isolated from the domain layer.
        return None