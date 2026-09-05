from dataclasses import dataclass
import re

from truecart_ai.domain.models import Location


@dataclass(frozen=True)
class ProductSuggestion:
    name: str
    brand: str | None = None
    quantity: str | None = None
    retailer: str = ""
    source: str = ""


class ProductSearchService:
    """
    Product discovery abstraction.

    The service is intentionally separated from price comparison.
    Retailer-specific live search adapters can be connected later
    without changing the API or UI contract.
    """

    def __init__(
        self,
        catalogue: list[ProductSuggestion] | None = None,
    ) -> None:
        self.catalogue = catalogue or []

    @staticmethod
    def _tokens(value: str) -> list[str]:
        return re.findall(r"[a-z0-9]+", value.lower())

    def suggest(
        self,
        query: str,
        location: Location,
        limit: int = 8,
    ) -> list[ProductSuggestion]:
        """
        Return products whose names/brands match the user's query.

        Location is part of the contract because real retailer search
        will be location-aware.
        """
        del location

        query = query.strip()

        if len(query) < 2:
            return []

        query_tokens = self._tokens(query)

        if not query_tokens:
            return []

        ranked: list[tuple[int, ProductSuggestion]] = []

        for product in self.catalogue:
            searchable = " ".join(
                part
                for part in [
                    product.name,
                    product.brand or "",
                    product.quantity or "",
                ]
                if part
            )

            product_tokens = self._tokens(searchable)

            score = 0

            for token in query_tokens:
                if token in product_tokens:
                    score += 10
                elif any(
                    candidate.startswith(token)
                    for candidate in product_tokens
                ):
                    score += 5

            if product.name.lower().startswith(query.lower()):
                score += 10

            if score > 0:
                ranked.append((score, product))

        ranked.sort(
            key=lambda item: (
                -item[0],
                item[1].name.lower(),
                item[1].retailer.lower(),
            )
        )

        return [
            product
            for _, product in ranked[: max(1, min(limit, 20))]
        ]
