from guillotina_audit.migrator import Migrator
from guillotina_audit.tests.utils import setup_txn_on_container

import asyncio
import json
import pytest


pytestmark = pytest.mark.asyncio


async def test_migrator(guillotina_es):
    container, request, txn, tm = await setup_txn_on_container(guillotina_es)
    await asyncio.sleep(2)
    resp, status = await guillotina_es(
        "GET", "/db/guillotina/@audit?type_name=Container"
    )
    assert status == 200
    assert len(resp["hits"]["hits"]) == 1
    migrator = Migrator()
    utility = migrator.util
    first_index = utility.index
    await migrator.migrate()
    indices = await utility.list_indices()
    aliases = await utility.list_aliases()
    assert len(indices.body) == 1
    assert indices.body[0]["index"].startswith("audit")
    current_index = indices.body[0]["index"]
    assert first_index in aliases.body[current_index]["aliases"]
    resp, status = await guillotina_es(
        "GET", "/db/guillotina/@audit?type_name=Container"
    )
    assert status == 200
    assert len(resp["hits"]["hits"]) == 1
    await asyncio.sleep(2)
    await migrator.migrate()
    resp, status = await guillotina_es(
        "GET", "/db/guillotina/@audit?type_name=Container"
    )
    assert status == 200
    assert len(resp["hits"]["hits"]) == 1
    for i in range(100):
        resp, status = await guillotina_es(
            "POST",
            "/db/guillotina",
            data=json.dumps({"@type": "Item", "title": "Foo item"}),
        )
        assert status == 201
    await asyncio.sleep(5)
    resp, status = await guillotina_es("GET", "/db/guillotina/@audit?type_name=Item")
    assert status == 200
    assert len(resp["hits"]["hits"]) == 100
    await migrator.migrate()
    resp, status = await guillotina_es("GET", "/db/guillotina/@audit?type_name=Item")
    assert status == 200
    assert len(resp["hits"]["hits"]) == 100
