"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
from datetime import datetime


class URLShortenRequest(BaseModel):
    """Request schema for URL shortening."""
    url: str = Field(..., description="The long URL to shorten", min_length=1)


class URLShortenResponse(BaseModel):
    """Response schema for URL shortening."""
    short_url: str = Field(..., description="The generated short URL")
    original_url: str = Field(..., description="The original long URL")
    short_code: str = Field(..., description="The short code")
    created_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "short_url": "http://localhost:8000/a1b2c3",
                "original_url": "https://example.com/very/long/url",
                "short_code": "a1b2c3",
                "created_at": "2024-01-01T12:00:00"
            }
        }


class ErrorResponse(BaseModel):
    """Error response schema."""
    detail: str = Field(..., description="Error message")

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Invalid URL format"
            }
        }

