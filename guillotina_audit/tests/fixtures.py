from guillotina import testing
from guillotina.tests.fixtures import _update_from_pytest_markers

import os
import pytest
import json


ELASTICSEARCH = os.environ.get("ELASTICSEARCH", "True")

annotations = {
    "elasticsearch": {
        "host": "localhost:9200"
    }
}

def base_settings_configurator(settings):
    if "applications" not in settings:
        settings["applications"] = []
    settings["applications"].append("guillotina")
    settings["applications"].append("guillotina_audit")

    settings["audit"] = {
        "connection_settings": {"hosts": [f"{annotations['elasticsearch']['host']}"]}  # noqa
    }


testing.configure_with(base_settings_configurator)


@pytest.fixture(scope="function")
def elasticsearch_fixture(es):
    settings = testing.get_settings()
    host, port = es
    settings["audit"]["connection_settings"]["hosts"] = [f"{host}:{port}"]
    settings = _update_from_pytest_markers(settings, None)
    testing.configure_with(base_settings_configurator)
    annotations["elasticsearch"]["host"] = f"{host}:{port}"
    testing.configure_with(base_settings_configurator)
    yield host, port


@pytest.fixture(scope="function")
async def guillotina_es(elasticsearch_fixture, guillotina):
    response, status = await guillotina("POST", "/db/", data=json.dumps({"@type": "Container", "id": "guillotina"}))
    assert status == 200
    yield guillotina
