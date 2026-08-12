from datetime import datetime, timezone

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check() -> dict:
    """Report basic service liveness.

    Returns:
        A dict with ``status`` set to ``"ok"``, a ``responseCode`` of
        ``"RC-001"``, and the current UTC ``timestamp`` in ISO 8601
        format.

        [VERIFY]: ``responseCode`` is always the literal ``"RC-001"``
        here; confirm whether other response codes are ever expected.

    Example:
        ``GET /health`` returns ``200`` with
        ``{"status": "ok", "responseCode": "RC-001", "timestamp": "..."}``.
    """
    return {
        "status": "ok",
        "responseCode":"RC-001",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }