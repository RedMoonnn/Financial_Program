from fastapi import APIRouter

from api.middleware import APIResponse

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    return APIResponse.success(data={"status": "ok"}, message="服务正常")
