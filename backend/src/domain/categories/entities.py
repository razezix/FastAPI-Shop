from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Category:
    id: UUID
    name: str
    slug: str
    description: str | None
    parent_id: UUID | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
