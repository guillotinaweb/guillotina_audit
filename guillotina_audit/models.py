import json
import datetime

from pydantic import BaseModel, field_serializer
from enum import Enum
from typing import Optional
from datetime import date

from datetime import timezone


class Action(str, Enum):
    modified = "modified"
    added = "added"
    removed = "removed"
    moved = "moved"
    duplicated = "duplicated"

class Document(BaseModel):
    action: Action
    path: Optional[str] = None
    uuid: Optional[str] = None
    payload: Optional[dict] = None
    creator: Optional[str] = None
    creation_date: date = datetime.datetime.now(timezone.utc)
    type_name: str

    @field_serializer('payload')
    def serialize_payload(self, payload: dict, _info):
        return json.dumps(payload)
