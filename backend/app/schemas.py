from datetime import datetime
from enum import Enum
from typing import Any, Literal
from uuid import UUID
from pydantic import BaseModel, Field, HttpUrl

class JobStatus(str, Enum):
    queued = "queued"; fetching = "fetching"; parsing = "parsing"; cleaning = "cleaning"; generating = "generating"; completed = "completed"; failed = "failed"
class Block(BaseModel):
    type: Literal["paragraph", "heading", "list", "quote", "table", "code"]
    text: str | None = None
    level: int | None = None
    items: list[str] = Field(default_factory=list)
    headers: list[str] = Field(default_factory=list)
    rows: list[list[str]] = Field(default_factory=list)
class Section(BaseModel):
    heading: str | None = None
    level: int = 1
    blocks: list[Block] = Field(default_factory=list)
class Statistics(BaseModel):
    word_count: int = 0; character_count: int = 0; reading_time_minutes: int = 0
class CanonicalDocument(BaseModel):
    schema_version: str = "1.0"
    id: UUID
    source_url: str
    canonical_url: str | None = None
    domain: str
    title: str | None = None
    author: str | None = None
    published_at: datetime | None = None
    fetched_at: datetime
    description: str | None = None
    language: str | None = None
    content: dict[str, list[Section]]
    links: list[str] = Field(default_factory=list)
    images: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    statistics: Statistics
    status: str = "completed"
    errors: list[dict[str, Any]] = Field(default_factory=list)
class FetchRequest(BaseModel):
    url: HttpUrl
class BatchRequest(BaseModel):
    urls: list[HttpUrl] = Field(min_length=1, max_length=10)
class JobResponse(BaseModel):
    job_id: UUID; status: JobStatus; progress: int = 0; source_url: str
class FileResponse(BaseModel):
    json: str | None = None; docx: str | None = None; pdf: str | None = None
