from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["docs"])


@router.get("/api-docs", response_class=HTMLResponse)
async def api_documentation():
    from pathlib import Path

    html_path = Path(__file__).parent / "templates" / "api_docs.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))
