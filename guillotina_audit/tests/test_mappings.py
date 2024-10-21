from guillotina.component import query_utility
from guillotina_audit.interfaces import IAuditUtility

import asyncio
import json
import pytest


pytestmark = pytest.mark.asyncio


async def test_mappings(guillotina_es):
    response, status = await guillotina_es(
        "POST", "/db/guillotina/@addons", data=json.dumps({"id": "audit"})
    )
    assert status == 200
    await asyncio.sleep(2)
    audit_utility = query_utility(IAuditUtility)
    await audit_utility.update_mappings()
