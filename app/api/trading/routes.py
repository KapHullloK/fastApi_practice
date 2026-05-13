from fastapi import APIRouter, HTTPException, Query

from app.cache import api_cache_key_builder, cache_until_reset
from app.api.dependencies import TradingRepositoryDep
from app.api.trading.schemas import (
    LastTradingDatesResponse,
    TradingDynamicsRequest,
    TradingDynamicsResponse,
    TradingFiltersRequest,
    TradingResultItem,
    TradingResultsResponse,
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
@cache_until_reset(key_builder=api_cache_key_builder)
async def get_last_trading_dates(
    trading_rep: TradingRepositoryDep,
    limit: int = Query(5, ge=1, le=365, description="Number of last trading dates"),
) -> LastTradingDatesResponse:
    dates = await trading_rep.get_last_trading_dates(limit=limit)
    return LastTradingDatesResponse(dates=dates)


@router.post(
    "/trading-results",
    response_model=TradingResultsResponse,
    description="Returns latest trading results with optional filters",
)
@cache_until_reset(key_builder=api_cache_key_builder)
async def get_trading_repesults(
    payload: TradingFiltersRequest,
    trading_rep: TradingRepositoryDep,
) -> TradingResultsResponse:
    rows = await trading_rep.get_trading_repesults(
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
@cache_until_reset(key_builder=api_cache_key_builder)
async def get_dynamics(
    payload: TradingDynamicsRequest,
    trading_rep: TradingRepositoryDep,
) -> TradingDynamicsResponse:
    if payload.start_date > payload.end_date:
        raise HTTPException(status_code=400, detail="start_date must be less than or equal to end_date")

    rows = await trading_rep.get_dynamics(
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
