from datetime import date
from datetime import datetime
from datetime import timedelta
from guillotina.component import query_utility
from guillotina_audit.interfaces import IAuditUtility
from guillotina_audit.models import AuditDocument

import asyncio
import json
import pytest


pytestmark = pytest.mark.asyncio


@pytest.mark.app_settings({"search_parser": "audit"})
async def test_audit_basic(guillotina_es):
    # Let's check the index has been created
    audit_utility = query_utility(IAuditUtility)
    resp = await audit_utility.async_es.indices.get_alias()
    assert "audit" in resp
    resp = await audit_utility.async_es.indices.get_mapping(index="audit")
    assert "path" in resp["audit"]["mappings"]["properties"]
    response, status = await guillotina_es(
        "POST",
        "/db/guillotina/",
        data=json.dumps({"@type": "Item", "id": "foo_item", "title": "Foo Item"}),
    )
    assert status == 201
    await asyncio.sleep(2)
    resp, status = await guillotina_es(
        "GET", "/db/guillotina/@audit?type_name=Container"
    )
    assert status == 200
    assert len(resp["hits"]["hits"]) == 1
    assert resp["hits"]["hits"][0]["_source"]["action"] == "added"
    assert resp["hits"]["hits"][0]["_source"]["type_name"] == "Container"
    assert resp["hits"]["hits"][0]["_source"]["creator"] == "root"
    assert "title" in resp["hits"]["hits"][0]["_source"]["payload"]

    resp, status = await guillotina_es("GET", "/db/guillotina/@audit?type_name=Item")
    assert status == 200

    assert resp["hits"]["hits"][0]["_source"]["action"] == "added"
    assert resp["hits"]["hits"][0]["_source"]["type_name"] == "Item"
    assert resp["hits"]["hits"][0]["_source"]["creator"] == "root"
    assert "title" in resp["hits"]["hits"][0]["_source"]["payload"]

    response, status = await guillotina_es("DELETE", "/db/guillotina/foo_item")
    await asyncio.sleep(2)
    resp, status = await guillotina_es("GET", "/db/guillotina/@audit")
    assert status == 200
    assert len(resp["hits"]["hits"]) == 3
    resp, status = await guillotina_es("GET", "/db/guillotina/@audit?action=removed")
    assert status == 200
    assert len(resp["hits"]["hits"]) == 1
    resp, status = await guillotina_es(
        "GET", "/db/guillotina/@audit?action=removed&type_name=Item"
    )
    assert status == 200
    assert len(resp["hits"]["hits"]) == 1
    resp, status = await guillotina_es(
        "GET", "/db/guillotina/@audit?action=added&type_name=Item"
    )
    assert status == 200
    assert len(resp["hits"]["hits"]) == 1
    assert resp["hits"]["hits"][0]["_source"]["type_name"] == "Item"
    resp, status = await guillotina_es(
        "GET", "/db/guillotina/@audit?action=added&type_name=Container"
    )
    assert status == 200
    assert len(resp["hits"]["hits"]) == 1
    assert resp["hits"]["hits"][0]["_source"]["type_name"] == "Container"
    creation_date = resp["hits"]["hits"][0]["_source"]["creation_date"]
    datetime_obj = datetime.strptime(creation_date, "%Y-%m-%dT%H:%M:%S.%f%z")
    new_creation_date = datetime_obj - timedelta(seconds=1)
    new_creation_date = new_creation_date.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
    resp, status = await guillotina_es(
        "GET",
        f"/db/guillotina/@audit?action=added&type_name=Container&creation_date__gte={new_creation_date}",
    )  # noqa
    assert status == 200
    assert len(resp["hits"]["hits"]) == 1
    resp, status = await guillotina_es(
        "GET",
        f"/db/guillotina/@audit?action=added&type_name=Container&creation_date__lte={new_creation_date}",
    )  # noqa
    assert len(resp["hits"]["hits"]) == 0
    assert status == 200

    response, status = await guillotina_es(
        "POST",
        "/db/guillotina/",
        data=json.dumps(
            {"@type": "Folder", "id": "foo_folder1", "title": "Foo Folder"}
        ),
    )
    assert status == 201

    response, status = await guillotina_es(
        "POST",
        "/db/guillotina/foo_folder1/@duplicate",
        data=json.dumps({"destination": "/", "new_id": "foo_folder2"}),
    )
    assert status == 200

    await asyncio.sleep(2)
    resp, status = await guillotina_es(
        "GET",
        "/db/guillotina/@audit?action=duplicated",
    )  # noqa
    assert len(resp["hits"]["hits"]) == 1
    assert status == 200

    response, status = await guillotina_es(
        "POST",
        "/db/guillotina/foo_folder2/@move",
        data=json.dumps({"destination": "/foo_folder1"}),
    )
    assert status == 200
    await asyncio.sleep(2)

    resp, status = await guillotina_es(
        "GET",
        "/db/guillotina/@audit?action=moved",
    )  # noqa
    assert len(resp["hits"]["hits"]) == 1
    assert status == 200

    response, status = await guillotina_es(
        "POST",
        "/db/guillotina/",
        data=json.dumps(
            {
                "@type": "Item",
                "id": "foo_item",
                "title": "Foo Item",
                "guillotina.behaviors.dublincore.IDublinCore": {
                    "effective_date": "2023-01-01"
                },
            }
        ),
    )
    assert status == 201
    await asyncio.sleep(2)
    resp, status = await guillotina_es("GET", "/db/guillotina/@audit")


@pytest.mark.app_settings({"search_parser": "audit"})
async def test_audit_wildcard(guillotina_es):
    audit_utility = query_utility(IAuditUtility)

    payload = AuditDocument(action="added", type_name="Fullscreen")
    audit_utility.log_wildcard(payload)
    await asyncio.sleep(2)

    resp, status = await guillotina_es(
        "GET",
        "/db/guillotina/@audit?action=added&type_name=Fullscreen",
    )  # noqa
    assert status == 200
    assert len(resp["hits"]["hits"]) == 1

    payload = AuditDocument(
        action="added",
        type_name="Click",
        path="/foopath",
        payload={"hola": "hola"},
        creator="creator",
        uuid="12345",
    )
    audit_utility.log_wildcard(payload)
    await asyncio.sleep(2)

    resp, status = await guillotina_es(
        "GET",
        "/db/guillotina/@audit?action=added&type_name=Click",
    )  # noqa
    assert status == 200
    assert len(resp["hits"]["hits"]) == 1

    payload = AuditDocument(action="CustomAction")
    audit_utility.log_wildcard(payload)
    await asyncio.sleep(2)

    resp, status = await guillotina_es(
        "GET",
        "/db/guillotina/@audit?action=CustomAction",
    )  # noqa
    assert status == 200
    assert len(resp["hits"]["hits"]) == 1
    assert "creation_date" in resp["hits"]["hits"][0]["_source"]

    payload = AuditDocument(
        action="added",
        creation_date="2023-05-12T21:45:32",
        type_name="AnotherFullscreen",
    )
    audit_utility.log_wildcard(payload)
    await asyncio.sleep(2)

    resp, status = await guillotina_es(
        "GET",
        "/db/guillotina/@audit?type_name=AnotherFullscreen",
    )  # noqa
    assert status == 200
    assert len(resp["hits"]["hits"]) == 1
    assert resp["hits"]["hits"][0]["_source"]["creation_date"].startswith(
        "2023-05-12T21:45:32"
    )


async def test_json_dumps(guillotina_es):
    audit_utility = query_utility(IAuditUtility)
    json.dumps(
        {"datetime": datetime.now(), "date": date.today()},
        default=audit_utility._custom_serializer,
    )


@pytest.mark.app_settings({"search_parser": "audit"})
async def test_permissions_modified_without_indexing(guillotina_es):
    response, status = await guillotina_es(
        "POST",
        "/db/guillotina/",
        data=json.dumps({"@type": "Item", "id": "foo_item", "title": "Foo Item"}),
    )
    assert status == 201
    await asyncio.sleep(2)
    resp, status = await guillotina_es("GET", "/db/guillotina/@audit")
    assert status == 200
    assert len(resp["hits"]["hits"]) == 2

    response, status = await guillotina_es(
        "POST",
        "/db/guillotina/foo_item/@sharing",
        data=json.dumps(
            {
                "prinperm": [
                    {
                        "principal": "foobar",
                        "permission": "guillotina.ModifyContent",
                        "setting": "Allow",
                    }
                ]
            }
        ),
    )
    assert status == 200
    await asyncio.sleep(2)
    resp, status = await guillotina_es("GET", "/db/guillotina/@audit")
    assert status == 200
    # There should be the same number of documents since indexing_permission_changes is False
    assert len(resp["hits"]["hits"]) == 2
    response, status = await guillotina_es(
        "PATCH", "/db/guillotina/foo_item", data=json.dumps({"title": "Another title"})
    )
    assert status == 204
    await asyncio.sleep(2)
    # Let's make sure ObjectModifiedEvent adds a document
    resp, status = await guillotina_es("GET", "/db/guillotina/@audit")
    assert status == 200
    assert len(resp["hits"]["hits"]) == 3


@pytest.mark.app_settings(
    {
        "search_parser": "audit",
        "load_utilities": {
            "audit": {
                "provides": "guillotina_audit.interfaces.IAuditUtility",
                "factory": "guillotina_audit.utility.AuditUtility",
                "settings": {
                    "index_name": "audit",
                    "save_payload": False,
                    "index_permission_changes": True,
                },
            }
        },
    }
)
async def test_permissions_modified_with_indexing(guillotina_es):
    response, status = await guillotina_es(
        "POST",
        "/db/guillotina/",
        data=json.dumps({"@type": "Item", "id": "foo_item", "title": "Foo Item"}),
    )
    assert status == 201
    await asyncio.sleep(2)
    resp, status = await guillotina_es("GET", "/db/guillotina/@audit")
    assert status == 200
    assert len(resp["hits"]["hits"]) == 2

    response, status = await guillotina_es(
        "POST",
        "/db/guillotina/foo_item/@sharing",
        data=json.dumps(
            {
                "prinperm": [
                    {
                        "principal": "foobar",
                        "permission": "guillotina.ModifyContent",
                        "setting": "Allow",
                    }
                ]
            }
        ),
    )
    assert status == 200
    await asyncio.sleep(3)
    resp, status = await guillotina_es("GET", "/db/guillotina/@audit")
    assert status == 200
    # There should be one more document since indexing_permission_changes is True
    assert len(resp["hits"]["hits"]) == 3
    assert resp["hits"]["hits"][-1]["_source"]["action"] == "permissions_changed"


@pytest.mark.app_settings({"search_parser": "audit"})
async def test_metadata_field(guillotina_es):
    audit_utility = query_utility(IAuditUtility)
    payload = AuditDocument(
        action="CreatingMetadata",
        metadata={
            "foo_number": 120,
            "foo_string": "foo_string",
            "foo_boolean": True,
            "foo_list": [1, 2, 3, 4],
            "foo_dict": {
                "foo_number": 100,
                "foo_string": "foo_string",
                "foo_dict": {"foo_key": "foo_value"},
            },
            "foo_decimal": 1.234,
        },
    )
    audit_utility.log_wildcard(payload)
    # Let's check the index has been created
    resp = await audit_utility.async_es.indices.get_alias()
    await asyncio.sleep(2)
    resp, status = await guillotina_es(
        "GET",
        "/db/guillotina/@audit?action=CreatingMetadata",
    )
    assert resp["hits"]["hits"][0]["_source"]["action"] == "CreatingMetadata"
    assert resp["hits"]["hits"][0]["_source"]["metadata"] == {
        "foo_boolean": True,
        "foo_dict": {
            "foo_dict": {"foo_key": "foo_value"},
            "foo_number": 100,
            "foo_string": "foo_string",
        },
        "foo_list": [1, 2, 3, 4],
        "foo_number": 120,
        "foo_string": "foo_string",
        "foo_decimal": 1.234,
    }
