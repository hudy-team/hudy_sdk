"""Type definitions for the Hudy SDK."""

from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field, field_validator


class Holiday(BaseModel):
    """A public or custom holiday."""

    id: str = Field(..., description="Holiday ID")
    name: str = Field(..., description="Holiday name")
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    year: int = Field(..., description="Year")
    month: int = Field(..., description="Month (1-12)")
    day: int = Field(..., description="Day of month")
    day_of_week: str = Field(..., description="Day of week name")
    type: Literal["public", "custom"] = Field(..., description="Holiday type")

    @property
    def is_public(self) -> bool:
        """Check if this is a public holiday."""
        return self.type == "public"

    @property
    def is_custom(self) -> bool:
        """Check if this is a custom holiday."""
        return self.type == "custom"

    @field_validator("date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """Validate date is in YYYY-MM-DD format."""
        try:
            parts = v.split("-")
            if len(parts) != 3:
                raise ValueError
            year, month, day = map(int, parts)
            # Basic validation
            if not (1900 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31):
                raise ValueError
            return v
        except (ValueError, AttributeError):
            raise ValueError(f"Date must be in YYYY-MM-DD format, got: {v}")


class ApiSuccessResponse(BaseModel):
    """Successful API response envelope."""

    result: Literal[True]
    data: List[Holiday]
    # Backend does not return meta field


class ApiErrorResponse(BaseModel):
    """Error API response envelope."""

    result: Literal[False]
    error: Dict[str, str]


ApiResponse = Union[ApiSuccessResponse, ApiErrorResponse]


class CacheOptions(BaseModel):
    """Cache configuration options."""

    enabled: bool = True
    ttl: Optional[int] = None  # seconds, None means auto (year-based)


class RetryOptions(BaseModel):
    """Retry configuration options."""

    enabled: bool = True
    max_retries: int = 3
    initial_delay: float = 1.0  # seconds
    max_delay: float = 10.0  # seconds
    backoff_factor: float = 2.0


class ClientOptions(BaseModel):
    """Hudy client configuration options."""

    api_key: str = Field(..., description="API key (must start with hd_live_)")
    base_url: str = Field(default="https://api.hudy.co.kr", description="API base URL")
    timeout: float = Field(default=10.0, description="Request timeout in seconds")
    cache: CacheOptions = Field(default_factory=CacheOptions)
    retry: RetryOptions = Field(default_factory=RetryOptions)

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate API key format."""
        if not v.startswith("hd_live_"):
            raise ValueError("API key must start with hd_live_")
        return v


class CacheStats(BaseModel):
    """Cache statistics."""

    hits: int = 0
    misses: int = 0
    size: int = 0
    entries: List[Dict[str, Any]] = Field(default_factory=list)
