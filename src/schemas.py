from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, allow_inf_nan=False)


class Credentials(StrictModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    # Do not strip passwords: spaces may be intentional.
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=False)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower() if isinstance(value, str) else value


class UserOut(BaseModel):
    id: int
    email: str
    created_at: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TicketInput(StrictModel):
    message: str = Field(min_length=5, max_length=5000)
    order_value_inr: float | None = Field(default=None, ge=0, le=10_000_000)
    days_since_delivery: int | None = Field(default=None, ge=0, le=3650, strict=True)
    days_since_dispatch: int | None = Field(default=None, ge=0, le=3650, strict=True)
    product_type: Literal["food", "non_food", "mixed", "unknown"] = "unknown"
    opened_status: Literal["opened", "unopened", "unknown"] = "unknown"
    order_status: Literal["processing", "not_dispatched", "dispatched", "delivered", "unknown"] = "unknown"


class Action(StrEnum):
    REQUEST_PHOTOS = "REQUEST_PHOTOS"
    APPROVE_REFUND_OR_REPLACEMENT = "APPROVE_REFUND_OR_REPLACEMENT"
    APPROVE_RETURN = "APPROVE_RETURN"
    OPEN_SHIPPING_INVESTIGATION = "OPEN_SHIPPING_INVESTIGATION"
    REPLACE_CORRECT_ITEM = "REPLACE_CORRECT_ITEM"
    NEEDS_MORE_INFORMATION = "NEEDS_MORE_INFORMATION"
    REQUEST_DEFECT_EVIDENCE = "REQUEST_DEFECT_EVIDENCE"
    APPROVE_REPLACEMENT = "APPROVE_REPLACEMENT"
    CANNOT_CANCEL_AFTER_DISPATCH = "CANNOT_CANCEL_AFTER_DISPATCH"
    CANCEL_AND_REFUND = "CANCEL_AND_REFUND"
    REJECT_OUTSIDE_WINDOW = "REJECT_OUTSIDE_WINDOW"
    WAIT_AND_TRACK = "WAIT_AND_TRACK"
    REJECT_FOOD_RETURN = "REJECT_FOOD_RETURN"
    OFFER_REPLACEMENT_OR_REFUND = "OFFER_REPLACEMENT_OR_REFUND"
    REJECT_OPENED_ITEM = "REJECT_OPENED_ITEM"
    APPROVE_REFUND = "APPROVE_REFUND"


class Evidence(StrictModel):
    chunk_id: str = Field(min_length=1)
    quote: str = Field(min_length=10, max_length=1000)


class DecisionOutput(StrictModel):
    action: Action
    confidence: float = Field(ge=0, le=1, strict=True)
    reason: str = Field(min_length=15, max_length=2500)
    sources: list[str] = Field(max_length=6)
    evidence: list[Evidence] = Field(max_length=10)
    missing_information: list[str] = Field(max_length=8)

    @model_validator(mode="after")
    def require_support(self):
        if self.action != Action.NEEDS_MORE_INFORMATION:
            if not self.sources or not self.evidence:
                raise ValueError("A substantive decision requires policy evidence.")
            if self.missing_information:
                raise ValueError("Unresolved required facts must produce NEEDS_MORE_INFORMATION.")
        elif not self.missing_information:
            raise ValueError("Ask specific questions when information is insufficient.")
        if len(set(self.sources)) != len(self.sources):
            raise ValueError("Sources must be unique.")
        return self


class RetrievedChunk(BaseModel):
    chunk_id: str
    source: str
    text: str
    similarity: float


class DecisionRecord(DecisionOutput):
    id: int
    ticket_id: int
    created_at: str
    model: str
    policy_version: str
    latency_ms: int
    retrieved_context: list[RetrievedChunk]


class TicketOut(TicketInput):
    id: int
    user_id: int
    created_at: str
    decision: DecisionRecord


class HistoryPage(BaseModel):
    items: list[TicketOut]
    total: int
    limit: int
    offset: int
