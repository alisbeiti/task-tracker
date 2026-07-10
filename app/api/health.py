from datetime import datetime, timezone

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check() -> dict:
    """
    Simple liveness check endpoint.

    Returns HTTP 200 with a JSON body indicating service status
    and the current UTC timestamp in ISO 8601 format.
    """
    return {
        "status": "ok",
        "responseCode":"RC-001",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }