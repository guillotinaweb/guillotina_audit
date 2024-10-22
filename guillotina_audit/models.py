from datetime import datetime
from datetime import timezone
from pydantic import BaseModel
from pydantic import Field
from pydantic import field_serializer
from typing import Optional

import json


class AuditDocument(BaseModel):
    action: str
    path: Optional[str] = None
    uuid: Optional[str] = None
    payload: Optional[dict] = None
    creator: Optional[str] = None
    creation_date: datetime = Field(default=datetime.now(timezone.utc))
    type_name: Optional[str] = None
    metadata: Optional[dict] = None

    @field_serializer("payload")
    def serialize_payload(self, payload: dict, _info):
        return json.dumps(payload)
