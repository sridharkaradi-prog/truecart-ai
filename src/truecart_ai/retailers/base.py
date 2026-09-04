from abc import ABC, abstractmethod

from truecart_ai.domain.models import Product, ProductOffer


class RetailerAdapter(ABC):
    """Contract that every retailer adapter must implement."""

    @property
    @abstractmethod
    def retailer_name(self) -> str:
        """Return the retailer's canonical name."""
        ...

    @abstractmethod
    def search_product(self, product: Product) -> ProductOffer | None:
        """Search the retailer and return a normalized offer."""
        ...