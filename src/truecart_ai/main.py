from fastapi import FastAPI

from truecart_ai.api.routes import router

app = FastAPI(
    title="TrueCart AI",
    version="0.1.0",
    description="Location-aware multi-retailer checkout price comparison.",
)

app.include_router(router)
