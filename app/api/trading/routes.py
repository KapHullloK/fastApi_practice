from fastapi import APIRouter, HTTPException, Query
from fastapi_cache.decorator import cache

from app.api.cache import api_cache_key_builder
from app.api.dependencies import SessionDep
from app.api.trading.schemas import (
    LastTradingDatesResponse,
    TradingDynamicsRequest,
    TradingDynamicsResponse,
    TradingFiltersRequest,
    TradingResultItem,
    TradingResultsResponse,
)
from app.config.settings import settings
from app.db.crud import (
    get_dynamics as get_dynamics_crud,
    get_last_trading_dates as get_last_trading_dates_crud,
    get_trading_results as get_trading_results_crud,
)

router = APIRouter(
    prefix="/trading",
    tags=["Trading"],
)


@router.get(
    "/last-trading-dates",
    response_model=LastTradingDatesResponse,
    description="Returns last unique trading dates filtered by count",
)
@cache(expire=settings.cache.default_ttl_seconds, key_builder=api_cache_key_builder)
async def get_last_trading_dates(
    session: SessionDep,
    limit: int = Query(5, ge=1, le=365, description="Number of last trading dates"),
) -> LastTradingDatesResponse:
    dates = await get_last_trading_dates_crud(session=session, limit=limit)
    return LastTradingDatesResponse(dates=dates)


@router.post(
    "/trading-results",
    response_model=TradingResultsResponse,
    description="Returns latest trading results with optional filters",
)
@cache(expire=settings.cache.default_ttl_seconds, key_builder=api_cache_key_builder)
async def get_trading_results(
    payload: TradingFiltersRequest,
    session: SessionDep,
) -> TradingResultsResponse:
    rows = await get_trading_results_crud(
        session=session,
        oil_id=payload.oil_id,
        delivery_type_id=payload.delivery_type_id,
        delivery_basis_id=payload.delivery_basis_id,
    )

    return TradingResultsResponse(
        items=[
            TradingResultItem(
                exchange_product_id=row.exchange_product_id,
                exchange_product_name=row.exchange_product_name,
                oil_id=row.oil_id,
                delivery_basis_id=row.delivery_basis_id,
                delivery_basis_name=row.delivery_basis_name,
                delivery_type_id=row.delivery_type_id,
                volume=row.volume,
                total=row.total,
                count=row.count,
                date=row.date,
            )
            for row in rows
        ]
    )


@router.post(
    "/dynamics",
    response_model=TradingDynamicsResponse,
    description="Returns trading dynamics for selected period and filters",
)
@cache(expire=settings.cache.default_ttl_seconds, key_builder=api_cache_key_builder)
async def get_dynamics(
    payload: TradingDynamicsRequest,
    session: SessionDep,
) -> TradingDynamicsResponse:
    if payload.start_date > payload.end_date:
        raise HTTPException(status_code=400, detail="start_date must be less than or equal to end_date")

    rows = await get_dynamics_crud(
        session=session,
        start_date=payload.start_date,
        end_date=payload.end_date,
        oil_id=payload.oil_id,
        delivery_type_id=payload.delivery_type_id,
        delivery_basis_id=payload.delivery_basis_id,
    )

    return TradingDynamicsResponse(
        items=[
            TradingResultItem(
                exchange_product_id=row.exchange_product_id,
                exchange_product_name=row.exchange_product_name,
                oil_id=row.oil_id,
                delivery_basis_id=row.delivery_basis_id,
                delivery_basis_name=row.delivery_basis_name,
                delivery_type_id=row.delivery_type_id,
                volume=row.volume,
                total=row.total,
                count=row.count,
                date=row.date,
            )
            for row in rows
        ]
    )
