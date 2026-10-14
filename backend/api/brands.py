from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.services import brand_detect as svc

class BrandIn(BaseModel):
    name: str = Field(min_length=2)
    aliases: list[str] = Field(default_factory=list)

class JobIn(BaseModel):
    asset_name: str = Field(min_length=2)
    hint_text: str = Field(min_length=2)

router = APIRouter()

@router.post("/brands")
async def create_brand(payload: BrandIn, db: AsyncSession = Depends(get_db)):
    row = await svc.upsert_brand(db, payload.name, payload.aliases)
    return {"id": row.id, "name": row.name}

@router.get("/brands")
async def brands(db: AsyncSession = Depends(get_db)):
    rows = await svc.list_brands(db)
    import json
    return {"brands": [{"id": b.id, "name": b.name, "aliases": json.loads(b.aliases_json or "[]")} for b in rows]}

@router.post("/jobs")
async def create_job(payload: JobIn, db: AsyncSession = Depends(get_db)):
    job = await svc.create_job(db, payload.asset_name, payload.hint_text)
    return {"id": job.id, "status": job.status}

@router.post("/jobs/{job_id}/run")
async def run_job(job_id: str, db: AsyncSession = Depends(get_db)):
    try:
        job = await svc.run_detection(db, job_id)
        return {"id": job.id, "status": job.status}
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc

@router.get("/jobs/{job_id}/matches")
async def matches(job_id: str, db: AsyncSession = Depends(get_db)):
    rows = await svc.list_matches(db, job_id)
    return {"matches": [{"id": m.id, "brand_id": m.brand_id, "confidence": m.confidence} for m in rows]}
