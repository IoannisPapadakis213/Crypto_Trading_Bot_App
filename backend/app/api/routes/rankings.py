"""GET /rankings — the most recent top-N ranking snapshot."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.models.repository import get_latest_rankings
from app.schemas.rankings import RankingEntryOut, RankingsResponse

router = APIRouter()


@router.get("/rankings", response_model=RankingsResponse)
async def get_rankings(session: AsyncSession = Depends(get_session)) -> RankingsResponse:  # noqa: B008
    rows = await get_latest_rankings(session)
    if not rows:
        raise HTTPException(status_code=503, detail="No ranking run has completed yet")
    return RankingsResponse(
        run_at=rows[0].run_at,
        entries=[RankingEntryOut.model_validate(row) for row in rows],
    )
