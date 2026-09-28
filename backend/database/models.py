from typing import Optional
from datetime import date
from pydantic import BaseModel, ConfigDict, Field, field_validator

class FinanceEntry(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra='allow')

    id: Optional[str] = Field(None, alias='_id', max_length=200)
    rev: Optional[str] = Field(None, alias='_rev', max_length=200)
    type: str = Field(min_length=1, max_length=40)
    amount: float = Field(gt=-1_000_000_000, lt=1_000_000_000)
    currency: str = Field(default='INR', min_length=3, max_length=3)
    date: str = Field(min_length=8, max_length=40)
    category: Optional[str] = Field(default=None, max_length=120)
    notes: Optional[str] = Field(default=None, max_length=2000)

    @field_validator('currency')
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        return value.upper()

    @field_validator('date')
    @classmethod
    def validate_date(cls, value: str) -> str:
        raw = value.strip()
        try:
            date.fromisoformat(raw[:10])
        except ValueError as exc:
            raise ValueError('date must start with a valid YYYY-MM-DD date') from exc
        return raw
