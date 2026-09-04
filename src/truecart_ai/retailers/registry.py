from truecart_ai.retailers.base import RetailerAdapter
from truecart_ai.retailers.blinkit import BlinkitAdapter
from truecart_ai.retailers.bbnow import BBNowAdapter
from truecart_ai.retailers.flipkart_minutes import FlipkartMinutesAdapter
from truecart_ai.retailers.instamart import InstamartAdapter
from truecart_ai.retailers.zepto import ZeptoAdapter


class RetailerRegistry:
    """Registry of available retailer adapters."""

    def __init__(self) -> None:
        self._adapters: list[RetailerAdapter] = [
            BlinkitAdapter(),
            ZeptoAdapter(),
            InstamartAdapter(),
            FlipkartMinutesAdapter(),
            BBNowAdapter(),
        ]

    def get_all(self) -> list[RetailerAdapter]:
        """Return all registered retailer adapters."""
        return list(self._adapters)

    def get(self, retailer_name: str) -> RetailerAdapter | None:
        """Return a retailer adapter by name."""
        normalized_name = retailer_name.strip().lower()

        for adapter in self._adapters:
            if adapter.retailer_name == normalized_name:
                return adapter

        return None
