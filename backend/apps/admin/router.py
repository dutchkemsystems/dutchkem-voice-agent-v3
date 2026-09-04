from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/", response_class=HTMLResponse)
async def admin_dashboard():
    from pathlib import Path

    html_path = Path(__file__).parent / "templates" / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))
