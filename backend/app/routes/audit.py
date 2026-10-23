
from fastapi import APIRouter

router = APIRouter(
    prefix="/audit",
    tags=["Audit Logs"],
)


@router.get("/health")
def audit_health():
    return {"message": "Audit routes are ready"}
