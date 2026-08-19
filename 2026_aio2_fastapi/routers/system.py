from fastapi import APIRouter

router = APIRouter(tags=["System"])


@router.get("/", summary="Root")
def read_root():
    return {"message": "FastAPI first server"}


@router.get("/health", summary="check status")
def health():
    return {"status": "ok"}


@router.get("/info", summary="infomation")
def info():
    return {"name": "도서 관리 API", "version": "1.0.0"}