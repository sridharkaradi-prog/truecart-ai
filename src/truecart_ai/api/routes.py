import os
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from truecart_ai.domain.models import Location, Product
from truecart_ai.retailers.demo import DemoRetailerAdapter
from truecart_ai.retailers.registry import RetailerRegistry
from truecart_ai.services.checkout_pricing import CheckoutPricingService
from truecart_ai.services.orchestrator import RetailerOrchestrator
from truecart_ai.services.product_catalogue import PRODUCT_CATALOGUE
from truecart_ai.services.product_search import ProductSearchService


router = APIRouter()

UI_PATH = Path(__file__).resolve().parent.parent / "ui" / "index.html"

product_search = ProductSearchService(PRODUCT_CATALOGUE)
checkout_pricing = CheckoutPricingService()


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
    try:
        location = Location(pincode=pincode)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    product_model = Product(name=product)

    result = get_orchestrator().compare(
        product_model,
        location,
    )

    retailers = []

    for item in result.retailer_results:
        checkout = None

        if item.offer is not None:
            checkout = checkout_pricing.calculate(item.offer)

        retailers.append(
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
                "delivery_fee": (
                    str(checkout.delivery_fee)
                    if checkout
                    else None
                ),
                "handling_fee": (
                    str(checkout.handling_fee)
                    if checkout
                    else None
                ),
                "final_checkout_price": (
                    str(checkout.final_price)
                    if checkout
                    else None
                ),
                "error": item.error,
            }
        )

    best_offer = None

    if result.best_offer is not None:
        best_checkout = checkout_pricing.calculate(result.best_offer)

        best_offer = {
            "retailer": result.best_offer.retailer,
            "product": result.best_offer.product.name,
            "price": str(result.best_offer.price.amount),
            "delivery_fee": str(best_checkout.delivery_fee),
            "handling_fee": str(best_checkout.handling_fee),
            "final_checkout_price": str(best_checkout.final_price),
            "currency": result.best_offer.price.currency,
        }

    return {
        "product": product,
        "pincode": pincode,
        "best_offer": best_offer,
        "retailers": retailers,
    }