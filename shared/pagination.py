"""
Standardized pagination schemas and helpers for Ayushman Bharat API endpoints.
Provides cursor and offset pagination abstractions with total count, total pages, and navigation URLs.
"""

import math
from typing import Generic, TypeVar, List, Optional, Any
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1, description="Page number starting at 1")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page (max 100)")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class PageMetadata(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    meta: PageMetadata


def paginate(items: List[Any], total: int, page: int, page_size: int) -> dict:
    """Helper function to format pagination metadata."""
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    return {
        "items": items,
        "meta": {
            "page": page,
            "page_size": page_size,
            "total_items": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1,
        }
    }
