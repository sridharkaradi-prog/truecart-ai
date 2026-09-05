import os
from pathlib import Path

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
)
from fastapi.responses import FileResponse

from truecart_ai.domain.models import (
    Location,
    Product,
)
from truecart_ai.retailers.demo import (
    DemoRetailerAdapter,
)
from truecart_ai.retailers.registry import (
    RetailerRegistry,
)
from truecart_ai.services.cache import (
    TTLCache,
)
from truecart_ai.services.cart_comparison import (
    CartComparisonService,
)
from truecart_ai.services.cart_recommendation import (
    CartRecommendationService,
)
from truecart_ai.services.checkout_pricing import (
    CheckoutPricingService,
)
from truecart_ai.services.orchestrator import (
    RetailerOrchestrator,
)
from truecart_ai.services.product_catalogue import (
    PRODUCT_CATALOGUE,
)
from truecart_ai.services.product_search import (
    ProductSearchService,
)


router = APIRouter()

UI_PATH = (
    Path(__file__).resolve().parent.parent
    / "ui"
    / "index.html"
)

product_search = ProductSearchService(
    PRODUCT_CATALOGUE
)

checkout_pricing = CheckoutPricingService()

cart_comparison = CartComparisonService(
    checkout_pricing
)

cart_recommendation = (
    CartRecommendationService()
)

comparison_cache = TTLCache(
    ttl_seconds=60.0
)

cart_cache = TTLCache(
    ttl_seconds=60.0
)


def get_orchestrator() -> RetailerOrchestrator:

    if (
        os.getenv(
            "TRUECART_DEMO_MODE",
            "false",
        ).lower()
        == "true"
    ):

        registry = RetailerRegistry()

        registry._adapters = [
            DemoRetailerAdapter(
                "blinkit",
                "32.00",
            ),
            DemoRetailerAdapter(
                "zepto",
                "30.00",
            ),
            DemoRetailerAdapter(
                "instamart",
                "31.00",
            ),
            DemoRetailerAdapter(
                "flipkart_minutes",
                "29.00",
            ),
            DemoRetailerAdapter(
                "bbnow",
                "30.50",
            ),
        ]

        return RetailerOrchestrator(
            registry
        )

    return RetailerOrchestrator()


@router.get("/health")
def health() -> dict[str, str]:

    return {
        "status": "ok"
    }


@router.get("/ui")
def ui() -> FileResponse:

    return FileResponse(
        UI_PATH
    )


@router.get("/suggestions")
def suggestions(
    query: str,
    pincode: str,
    limit: int = 8,
) -> dict:

    try:

        location = Location(
            pincode=pincode
        )

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

        location = Location(
            pincode=pincode
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    cache_key = (
        f"compare:{product.strip().lower()}:"
        f"{pincode}"
    )

    cached_result, cache_hit = (
        comparison_cache.get(
            cache_key
        )
    )

    if cache_hit:

        result = cached_result

    else:

        product_model = Product(
            name=product
        )

        result = get_orchestrator().compare(
            product_model,
            location,
        )

        comparison_cache.set(
            cache_key,
            result,
        )

    retailers = []

    for item in result.retailer_results:

        checkout = None

        if item.offer is not None:

            checkout = (
                checkout_pricing.calculate(
                    item.offer
                )
            )

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
                    str(
                        item.offer.price.amount
                    )
                    if item.offer
                    else None
                ),
                "delivery_fee": (
                    str(
                        checkout.delivery_fee
                    )
                    if checkout
                    else None
                ),
                "handling_fee": (
                    str(
                        checkout.handling_fee
                    )
                    if checkout
                    else None
                ),
                "final_checkout_price": (
                    str(
                        checkout.final_price
                    )
                    if checkout
                    else None
                ),
                "attempts": (
                    item.attempts
                ),
                "duration_ms": (
                    item.duration_ms
                ),
                "error": item.error,
            }
        )

    best_offer = None

    if result.best_offer is not None:

        best_checkout = (
            checkout_pricing.calculate(
                result.best_offer
            )
        )

        best_offer = {
            "retailer": (
                result.best_offer.retailer
            ),
            "product": (
                result.best_offer.product.name
            ),
            "price": str(
                result.best_offer.price.amount
            ),
            "delivery_fee": str(
                best_checkout.delivery_fee
            ),
            "handling_fee": str(
                best_checkout.handling_fee
            ),
            "final_checkout_price": str(
                best_checkout.final_price
            ),
            "currency": (
                result.best_offer.price.currency
            ),
        }

    return {
        "product": product,
        "pincode": pincode,
        "cache_hit": cache_hit,
        "best_offer": best_offer,
        "retailers": retailers,
    }


@router.get("/cart/compare")
def compare_cart(
    products: list[str] = Query(...),
    pincode: str = Query(...),
) -> dict:

    cleaned_products = [
        product.strip()
        for product in products
        if product.strip()
    ]

    if not cleaned_products:

        raise HTTPException(
            status_code=400,
            detail=(
                "At least one product is required."
            ),
        )

    if len(cleaned_products) > 10:

        raise HTTPException(
            status_code=400,
            detail=(
                "Maximum 10 products per cart."
            ),
        )

    try:

        location = Location(
            pincode=pincode
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    normalized_products = [
        product.lower()
        for product in cleaned_products
    ]

    cache_key = (
        "cart:"
        + "|".join(
            sorted(normalized_products)
        )
        + f":{pincode}"
    )

    cached_result, cache_hit = (
        cart_cache.get(
            cache_key
        )
    )

    if cache_hit:

        result, recommendation = (
            cached_result
        )

    else:

        orchestrator = (
            get_orchestrator()
        )

        product_models = [
            Product(
                name=product
            )
            for product in cleaned_products
        ]

        comparisons = [
            orchestrator.compare(
                product,
                location,
            )
            for product in product_models
        ]

        result = cart_comparison.compare(
            product_models,
            comparisons,
        )

        recommendation = (
            cart_recommendation.recommend(
                result
            )
        )

        cart_cache.set(
            cache_key,
            (
                result,
                recommendation,
            ),
        )

    retailer_options = [
        {
            "retailer": option.retailer,
            "total_price": str(
                option.total_price
            ),
            "available_items": (
                option.available_items
            ),
            "missing_items": (
                option.missing_items
            ),
        }
        for option in result.retailer_options
    ]

    split_cart = [
        {
            "product": item.product.name,
            "retailer": item.retailer,
            "final_price": str(
                item.final_price
            ),
        }
        for item in result.split_cart
    ]

    decision_trace = [
        {
            "step": trace.step,
            "detail": trace.detail,
        }
        for trace in (
            recommendation.decision_trace
        )
    ]

    return {
        "pincode": pincode,
        "products": cleaned_products,
        "cache_hit": cache_hit,
        "cheapest_complete_retailer": (
            result.cheapest_complete_retailer
        ),
        "cheapest_complete_total": (
            str(
                result.cheapest_complete_total
            )
            if (
                result.cheapest_complete_total
                is not None
            )
            else None
        ),
        "split_total": (
            str(
                result.split_total
            )
            if result.split_total is not None
            else None
        ),
        "split_retailer_count": (
            result.split_retailer_count
        ),
        "recommendation": {
            "type": (
                recommendation.recommendation_type
            ),
            "retailer": (
                recommendation.retailer
            ),
            "total_price": (
                str(
                    recommendation.total_price
                )
                if (
                    recommendation.total_price
                    is not None
                )
                else None
            ),
            "savings": str(
                recommendation.savings
            ),
            "savings_percentage": str(
                recommendation.savings_percentage
            ),
            "retailer_count": (
                recommendation.retailer_count
            ),
            "reason": (
                recommendation.reason
            ),
            "decision_trace": (
                decision_trace
            ),
        },
        "retailers": retailer_options,
        "split_cart": split_cart,
    }