from fastapi import APIRouter

health_bp = APIRouter()


@health_bp.get("/health")
async def health():
    return {"status": "ok"}
