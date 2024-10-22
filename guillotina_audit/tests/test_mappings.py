from guillotina.component import query_utility
from guillotina_audit.interfaces import IAuditUtility

import pytest


pytestmark = pytest.mark.asyncio


async def test_mappings(guillotina_es):
    audit_utility = query_utility(IAuditUtility)
    await audit_utility.update_settings()
    await audit_utility.update_mappings()
