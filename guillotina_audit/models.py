from datetime import date
from datetime import timezone
from pydantic import BaseModel
from pydantic import field_serializer
from typing import Optional

import datetime
import json


class AuditDocument(BaseModel):
    action: str
    path: Optional[str] = None
    uuid: Optional[str] = None
    payload: Optional[dict] = None
    creator: Optional[str] = None
    creation_date: date = datetime.datetime.now(timezone.utc)
    type_name: Optional[str] = None

    @field_serializer("payload")
    def serialize_payload(self, payload: dict, _info):
        return json.dumps(payload)
