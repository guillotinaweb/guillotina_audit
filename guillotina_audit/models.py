from pydantic import BaseModel
from enum import Enum
from typing import Optional
from datetime import date

from datetime import timezone
import datetime


class Action(str, Enum):
    modified = "modified"
    added = "added"
    removed = "removed"
    moved = "moved"
    duplicated = "duplicated"

class Document(BaseModel):
    action: Action
    path: Optional[str]
    uuid: Optional[str]
    payload: Optional[dict]
    creator: Optional[str]
    creation_date: date = datetime.datetime.now(timezone.utc)
    path: Optional[str]
    type_name: str
