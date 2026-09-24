from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.query_service import QueryService
from app.services.query_engine import get_summary
from app.services.anomaly_detector import detect_anomalies


router = APIRouter()

query_service = QueryService()


class QueryRequest(BaseModel):
    question: str


@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "DOTMappers AI Support Analytics"
    }


@router.get("/summary")
def summary():
    try:
        return get_summary()
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.post("/query")
def query(request: QueryRequest):
    try:
        if not request.question.strip():
            raise HTTPException(
                status_code=400,
                detail="Question cannot be empty.",
            )

        return query_service.answer(
            request.question
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.get("/anomalies")
def anomalies():
    try:
        results = detect_anomalies()

        return {
            "count": len(results),
            "anomalies": results,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )