import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class QuoteModel(Base):
    __tablename__ = "quotes"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    applied_rate: Mapped[float] = mapped_column(Float, nullable=False)
    broker_fee: Mapped[float] = mapped_column(Float, nullable=False)
    calculated_premium: Mapped[float] = mapped_column(Float, nullable=False)
    car_make: Mapped[str] = mapped_column(String(100), nullable=False)
    car_model: Mapped[str] = mapped_column(String(100), nullable=False)
    car_value: Mapped[float] = mapped_column(Float, nullable=False)
    car_year: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    deductible_percentage: Mapped[float] = mapped_column(Float, nullable=False)
    deductible_value: Mapped[float] = mapped_column(Float, nullable=False)
    policy_limit: Mapped[float] = mapped_column(Float, nullable=False)
