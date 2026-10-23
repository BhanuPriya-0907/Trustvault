
from fastapi import APIRouter

router = APIRouter(
    prefix="/permissions",
    tags=["Permissions"],
)


@router.get("/health")
def permissions_health():
    return {"message": "Permission routes are ready"}
