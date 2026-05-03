from datetime import date

from pydantic import BaseModel, Field


class LastTradingDatesResponse(BaseModel):
    dates: list[date] = Field(
        default_factory=list,
        description="List of last trading dates sorted from newest to oldest",
    )


class TradingFiltersRequest(BaseModel):
    oil_id: str | None = Field(
        default=None,
        description="Oil ID filter",
        examples=["A100"],
    )
    delivery_type_id: str | None = Field(
        default=None,
        description="Delivery type ID filter",
        examples=["F"],
    )
    delivery_basis_id: str | None = Field(
        default=None,
        description="Delivery basis ID filter",
        examples=["PDK"],
    )


class TradingDynamicsRequest(TradingFiltersRequest):
    start_date: date = Field(..., description="Start date (inclusive)")
    end_date: date = Field(..., description="End date (inclusive)")


class TradingResultItem(BaseModel):
    exchange_product_id: str
    exchange_product_name: str
    oil_id: str
    delivery_basis_id: str
    delivery_basis_name: str
    delivery_type_id: str
    volume: int
    total: int
    count: int
    date: date


class TradingResultsResponse(BaseModel):
    items: list[TradingResultItem] = Field(
        default_factory=list,
        description="Latest trading results with optional filters",
    )


class TradingDynamicsResponse(BaseModel):
    items: list[TradingResultItem] = Field(
        default_factory=list,
        description="Trading results list for selected period and filters",
    )
