from truecart_ai.domain.models import Location, Product, ProductOffer
from truecart_ai.retailers.base import RetailerAdapter


class InstamartAdapter(RetailerAdapter):
    """Swiggy Instamart retailer adapter."""

    @property
    def retailer_name(self) -> str:
        return "instamart"

    def search_product(
        self,
        product: Product,
        location: Location,
    ) -> ProductOffer | None:
        # Retrieval implementation will be added separately.
        return None