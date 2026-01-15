from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["UI"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request},
    )

@router.get("/notifications")
async def notifications_page(request: Request):
    return templates.TemplateResponse(
        "notifications.html",
        {"request": request},
    )