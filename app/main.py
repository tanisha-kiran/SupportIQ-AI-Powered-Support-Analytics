from fastapi import FastAPI

from app.api.routes import router


app = FastAPI(
    title="DOTMappers AI Support Analytics",
    description=(
        "Natural-language customer support analytics "
        "using LLM-generated SQL and deterministic anomaly detection."
    ),
    version="1.0.0",
)


app.include_router(router)