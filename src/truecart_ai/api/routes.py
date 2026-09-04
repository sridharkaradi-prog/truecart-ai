from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

from truecart_ai.domain.models import Location, Product
from truecart_ai.retailers.demo import DemoRetailerAdapter
from truecart_ai.retailers.registry import RetailerRegistry
from truecart_ai.services.orchestrator import RetailerOrchestrator

router = APIRouter()

UI_PATH = Path(__file__).resolve().parent.parent / "ui" / "index.html"


def get_orchestrator() -> RetailerOrchestrator:
    """Build the orchestrator using demo data when DEMO mode is enabled."""

    import os

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
