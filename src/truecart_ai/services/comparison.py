from truecart_ai.domain.models import ProductOffer


class ComparisonService:
    """Compare retailer offers and identify the best price."""

    def find_best_offer(
        self,
        offers: list[ProductOffer],
    ) -> ProductOffer | None:
        available_offers = [
            offer for offer in offers
            if offer.available
        ]

        if not available_offers:
            return None

        return min(
            available_offers,
            key=lambda offer: offer.price.amount,
        )
