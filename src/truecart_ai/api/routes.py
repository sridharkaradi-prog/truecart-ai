from pathlib import Path
import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from truecart_ai.domain.models import Location, Product
from truecart_ai.retailers.demo import DemoRetailerAdapter
from truecart_ai.retailers.registry import RetailerRegistry
from truecart_ai.services.orchestrator import RetailerOrchestrator
from truecart_ai.services.product_catalogue import PRODUCT_CATALOGUE
from truecart_ai.services.product_search import ProductSearchService

router = APIRouter()

UI_PATH = Path(__file__).resolve().parent.parent / "ui" / "index.html"

product_search = ProductSearchService(PRODUCT_CATALOGUE)


def get_orchestrator() -> RetailerOrchestrator:
    if os.getenv("TRUECART_DEMO_MODE", "false").lower() == "true":
        registry = RetailerRegistry()

        registry._adapters = [
            DemoRetailerAdapter("blinkit", "32.00"),
            DemoRetailerAdapter("zepto", "30.00"),
            DemoRetailerAdapter("instamart", "31.00"),
            DemoRetailerAdapter("flipkart_minutes", "29.00"),
            DemoRetailerAdapter("bbnow", "30.50"),
        ]

        return RetailerOrchestrator(registry)

    return RetailerOrchestrator()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ui")
def ui() -> FileResponse:
    return FileResponse(UI_PATH)


@router.get("/suggestions")
def suggestions(
    query: str,
    pincode: str,
    limit: int = 8,
) -> dict:
    try:
        location = Location(pincode=pincode)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    matches = product_search.suggest(
        query=query,
        location=location,
        limit=limit,
    )

    return {
        "query": query,
        "pincode": pincode,
        "suggestions": [
            {
                "name": item.name,
                "brand": item.brand,
                "quantity": item.quantity,
                "retailer": item.retailer,
                "source": item.source,
            }
            for item in matches
        ],
    }


@router.get("/compare")
def compare_product(
    product: str,
    pincode: str,
) -> dict:
    product_model = Product(name=product)
    location = Location(pincode=pincode)

    result = get_orchestrator().compare(
        product_model,
        location,
    )

    return {
        "product": product,
        "pincode": pincode,
        "best_offer": (
            {
                "retailer": result.best_offer.retailer,
                "product": result.best_offer.product.name,
                "price": str(result.best_offer.price.amount),
                "currency": result.best_offer.price.currency,
            }
            if result.best_offer
            else None
        ),
        "retailers": [
            {
                "retailer": item.retailer,
                "status": item.status,
                "product": (
                    item.offer.product.name
                    if item.offer
                    else None
                ),
                "price": (
                    str(item.offer.price.amount)
                    if item.offer
                    else None
                ),
                "error": item.error,
            }
            for item in result.retailer_results
        ],
    }
