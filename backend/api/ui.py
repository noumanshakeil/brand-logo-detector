from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.services import brand_detect as svc

router = APIRouter()
templates = Jinja2Templates(directory="backend/templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: AsyncSession = Depends(get_db)):
    jobs = await svc.list_jobs(db)
    return templates.TemplateResponse("index.html", {"request": request, "title": "Brand Logo Detector", "jobs": jobs})

@router.post("/ui/jobs")
async def ui_job(asset_name: str = Form(...), hint_text: str = Form(...), db: AsyncSession = Depends(get_db)):
    job = await svc.create_job(db, asset_name, hint_text)
    await svc.run_detection(db, job.id)
    return RedirectResponse("/", status_code=303)
