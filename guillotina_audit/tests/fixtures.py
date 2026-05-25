from guillotina import testing
from guillotina.component import query_utility
from guillotina.tests.fixtures import _update_from_pytest_markers
from guillotina_audit.interfaces import IAuditUtility

import asyncio
import json
import os
import pytest
import pytest_asyncio


ELASTICSEARCH = os.environ.get("ELASTICSEARCH", "True")

annotations = {"elasticsearch": {"host": "localhost:9200"}}


def base_settings_configurator(settings):
    if "applications" not in settings:
        settings["applications"] = []
    settings["applications"].append("guillotina")
    settings["applications"].append("guillotina_audit")
    settings["applications"].append("guillotina_audit.tests.test_package")
    settings["audit"] = {
        "connection_settings": {
            "hosts": [f"http://{annotations['elasticsearch']['host']}"],
            "request_timeout": 30,
        }
    }
    settings["load_utilities"] = {
        "audit": {
            "provides": "guillotina_audit.interfaces.IAuditUtility",
            "factory": "guillotina_audit.utility.AuditUtility",
            "settings": {"index_name": "audit", "save_payload": True},
        }
    }


testing.configure_with(base_settings_configurator)


async def wait_for_elasticsearch(audit_utility, index=None):
    deadline = 60
    retry_wait = 1
    for _ in range(deadline):
        try:
            await audit_utility.async_es.cluster.health(
                index=index, wait_for_status="yellow", timeout="5s"
            )
            return
        except Exception:
            await asyncio.sleep(retry_wait)
    await audit_utility.async_es.cluster.health(
        index=index, wait_for_status="yellow", timeout="60s"
    )


async def cleanup_audit_indices(audit_utility):
    indices = await audit_utility.async_es.indices.get(
        index=f"{audit_utility.index}*", ignore_unavailable=True
    )
    for index_name in indices.keys():
        await audit_utility.async_es.indices.delete(
            index=index_name, ignore_unavailable=True
        )


@pytest.fixture(scope="function")
def elasticsearch_fixture(es):
    settings = testing.get_settings()
    host, port = es
    settings = _update_from_pytest_markers(settings, None)
    testing.configure_with(base_settings_configurator)
    annotations["elasticsearch"]["host"] = f"{host}:{port}"
    testing.configure_with(base_settings_configurator)
    yield host, port


@pytest_asyncio.fixture(scope="function")
async def guillotina_es(elasticsearch_fixture, guillotina):
    audit_utility = query_utility(IAuditUtility)
    await wait_for_elasticsearch(audit_utility)
    await cleanup_audit_indices(audit_utility)
    await audit_utility.create_index()
    await wait_for_elasticsearch(audit_utility, index=audit_utility.index)
    response, status = await guillotina(
        "POST", "/db/", data=json.dumps({"@type": "Container", "id": "guillotina"})
    )
    assert status == 200
    yield guillotina
    await cleanup_audit_indices(audit_utility)
