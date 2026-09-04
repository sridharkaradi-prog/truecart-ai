from abc import ABC, abstractmethod

from truecart_ai.domain.models import Location, Product, ProductOffer


class RetailerAdapter(ABC):
    """Contract that every retailer adapter must implement."""

    @property
    @abstractmethod
    def retailer_name(self) -> str:
        """Return the retailer's canonical name."""
        ...

    @abstractmethod
    def search_product(
        self,
        product: Product,
        location: Location,
    ) -> ProductOffer | None:
        """Search the retailer for a product at a location."""
        ...