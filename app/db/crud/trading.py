from datetime import date

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.spimex_trading_result import SpimexTradingResult


def _build_filters(
    oil_id: str | None = None,
    delivery_type_id: str | None = None,
    delivery_basis_id: str | None = None,
) -> list:
    filters = []

    if oil_id is not None:
        filters.append(SpimexTradingResult.oil_id == oil_id)
    if delivery_type_id is not None:
        filters.append(SpimexTradingResult.delivery_type_id == delivery_type_id)
    if delivery_basis_id is not None:
        filters.append(SpimexTradingResult.delivery_basis_id == delivery_basis_id)

    return filters


async def get_last_trading_dates(session: AsyncSession, limit: int) -> list[date]:
    stmt = (
        select(SpimexTradingResult.date)
        .distinct()
        .order_by(desc(SpimexTradingResult.date))
        .limit(limit)
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_trading_results(
    session: AsyncSession,
    oil_id: str | None = None,
    delivery_type_id: str | None = None,
    delivery_basis_id: str | None = None,
) -> list[SpimexTradingResult]:
    filters = _build_filters(
        oil_id=oil_id,
        delivery_type_id=delivery_type_id,
        delivery_basis_id=delivery_basis_id,
    )

    max_date_stmt = select(func.max(SpimexTradingResult.date)).where(and_(*filters))
    max_date_result = await session.execute(max_date_stmt)
    latest_date = max_date_result.scalar_one_or_none()

    if latest_date is None:
        return []

    stmt = (
        select(SpimexTradingResult)
        .where(and_(SpimexTradingResult.date == latest_date, *filters))
        .order_by(SpimexTradingResult.id)
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_dynamics(
    session: AsyncSession,
    start_date: date,
    end_date: date,
    oil_id: str | None = None,
    delivery_type_id: str | None = None,
    delivery_basis_id: str | None = None,
) -> list[SpimexTradingResult]:
    filters = _build_filters(
        oil_id=oil_id,
        delivery_type_id=delivery_type_id,
        delivery_basis_id=delivery_basis_id,
    )
    filters.extend([SpimexTradingResult.date >= start_date, SpimexTradingResult.date <= end_date])

    stmt = (
        select(SpimexTradingResult)
        .where(and_(*filters))
        .order_by(desc(SpimexTradingResult.date), SpimexTradingResult.id)
    )
    result = await session.execute(stmt)
    return result.scalars().all()
