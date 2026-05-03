from datetime import date

from sqlalchemy import Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models import Base


class SpimexTradingResult(Base):
    __tablename__ = "spimex_trading_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    exchange_product_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    exchange_product_name: Mapped[str] = mapped_column(String(500), nullable=False)

    oil_id: Mapped[str] = mapped_column(String(4), nullable=False)
    delivery_basis_id: Mapped[str] = mapped_column(String(3), nullable=False)
    delivery_basis_name: Mapped[str] = mapped_column(String(255), nullable=False)
    delivery_type_id: Mapped[str] = mapped_column(String(1), nullable=False)

    volume: Mapped[int] = mapped_column(Integer, nullable=False)
    total: Mapped[int] = mapped_column(Integer, nullable=False)
    count: Mapped[int] = mapped_column(Integer, nullable=False)

    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
