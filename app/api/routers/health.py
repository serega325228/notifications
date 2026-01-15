from fastapi import APIRouter

router = APIRouter(prefix="/api/health")

@router.get("/")
async def health():
    return {"status": "ok"}