from __future__ import annotations
import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models import Brand, DetectionJob, MatchCandidate
from backend.repositories import audit
from backend.utils.ids import short_id
from backend.utils.similarity import jaccard

async def upsert_brand(session: AsyncSession, name: str, aliases: list[str]) -> Brand:
    stmt = select(Brand).where(Brand.name == name)
    existing = (await session.execute(stmt)).scalar_one_or_none()
    if existing:
        existing.aliases_json = json.dumps(aliases)
        await session.commit()
        await session.refresh(existing)
        return existing
    row = Brand(id=short_id(), name=name[:120], aliases_json=json.dumps(aliases))
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row

async def list_brands(session: AsyncSession) -> list[Brand]:
    return list((await session.execute(select(Brand).order_by(Brand.name))).scalars())

async def create_job(session: AsyncSession, asset_name: str, hint_text: str) -> DetectionJob:
    job = DetectionJob(id=short_id(), asset_name=asset_name[:200], hint_text=hint_text, status="queued")
    session.add(job)
    await session.commit()
    await session.refresh(job)
    audit.record("detection_job_created", job.id)
    return job

async def run_detection(session: AsyncSession, job_id: str) -> DetectionJob:
    job = await session.get(DetectionJob, job_id)
    if not job:
        raise ValueError("job not found")
    job.status = "running"
    await session.commit()
    brands = await list_brands(session)
    blob = job.hint_text.lower()
    scored: list[tuple[Brand, float]] = []
    for b in brands:
        aliases = json.loads(b.aliases_json or "[]")
        terms = [b.name.lower(), *[a.lower() for a in aliases]]
        conf = max(jaccard(blob, t) for t in terms) if terms else 0.0
        if conf > 0.05:
            scored.append((b, conf))
    scored.sort(key=lambda x: x[1], reverse=True)
    for b, conf in scored[:5]:
        session.add(
            MatchCandidate(
                id=short_id(),
                job_id=job_id,
                brand_id=b.id,
                confidence=round(min(conf + 0.35, 0.99), 3),
            )
        )
    job.status = "done"
    await session.commit()
    await session.refresh(job)
    return job

async def list_jobs(session: AsyncSession) -> list[DetectionJob]:
    return list((await session.execute(select(DetectionJob).order_by(DetectionJob.created_at.desc()))).scalars())

async def list_matches(session: AsyncSession, job_id: str) -> list[MatchCandidate]:
    stmt = select(MatchCandidate).where(MatchCandidate.job_id == job_id).order_by(MatchCandidate.confidence.desc())
    return list((await session.execute(stmt)).scalars())
