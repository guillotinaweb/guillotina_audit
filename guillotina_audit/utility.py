# -*- coding: utf-8 -*-
from datetime import timezone
from elasticsearch import AsyncElasticsearch
from elasticsearch import BadRequestError
from elasticsearch.exceptions import RequestError
from guillotina import app_settings
from guillotina.catalog.utils import parse_query
from guillotina.interfaces import IObjectAddedEvent
from guillotina.interfaces import IObjectDuplicatedEvent
from guillotina.interfaces import IObjectModifiedEvent
from guillotina.interfaces import IObjectMovedEvent
from guillotina.interfaces import IObjectPermissionsModifiedEvent
from guillotina.interfaces import IObjectRemovedEvent
from guillotina.utils import get_current_container
from guillotina.utils.auth import get_authenticated_user
from guillotina.utils.content import get_content_path
from guillotina_audit.models import AuditDocument

import asyncio
import datetime
import json
import logging


logger = logging.getLogger("guillotina_audit")


class AuditUtility:
    def __init__(self, settings=None, loop=None):
        self._settings = settings
        self.index = self._settings.get("index_name", "audit")
        self.loop = loop

    async def initialize(self, app):
        self.async_es = AsyncElasticsearch(
            **app_settings.get("audit", {}).get("connection_settings")
        )

    def _custom_serializer(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        raise TypeError("Object of type %s is not JSON serializable" % type(obj))

    async def update_settings(self):
        await self.async_es.indices.close(index=self.index)
        try:
            await self.async_es.indices.put_settings(
                body=self.default_settings(), index=self.index
            )
            logger.info(f"Updating mappings {self.default_settings()}")
        except Exception:
            logger.error("Error updating settings", exc_info=True)
        finally:
            await self.async_es.indices.open(index=self.index)

    async def update_mappings(self):
        await self.async_es.indices.put_mapping(
            body=self.default_mappings(), index=self.index
        )
        logger.info(f"Updating mappings {self.default_mappings()}")

    async def create_index(self):
        try:
            await self.async_es.indices.create(
                index=self.index,
                settings=self.default_settings(),
                mappings=self.default_mappings(),
            )
        except RequestError:
            logger.error("An exception occurred when creating index", exc_info=True)
        except BadRequestError:
            logger.error("An exception occurred when creating index", exc_info=True)

    def settings(self):
        return {
            "settings": {
                "analysis": {
                    "analyzer": {
                        "my_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["lowercase"],
                        },
                        "my_stop_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["lowercase", "english_stop"],
                        },
                    },
                    "filter": {
                        "english_stop": {"type": "stop", "stopwords": "_english_"}
                    },
                }
            }
        }

    def default_settings(self):
        return {
            "analysis": {
                "analyzer": {
                    "path_analyzer": {  # Custom analyzer definition
                        "type": "custom",
                        "tokenizer": "path_tokenizer",
                    }
                },
                "tokenizer": {
                    "path_tokenizer": {  # Custom tokenizer definition
                        "type": "path_hierarchy",
                        "delimiter": "/",
                    }
                },
            }
        }

    def default_mappings(self):
        return {
            "dynamic": False,
            "properties": {
                "path": {"type": "text", "store": True, "analyzer": "path_analyzer"},
                "type_name": {"type": "keyword", "store": True},
                "uuid": {"type": "keyword", "store": True},
                "action": {"type": "keyword", "store": True},
                "creator": {"type": "keyword"},
                "creation_date": {"type": "date", "store": True},
                "payload": {"type": "text", "store": True},
                "metadata": {"type": "object", "dynamic": True},
            },
        }

    def log_wildcard(self, payload: AuditDocument):
        coroutine = self.async_es.index(
            index=self.index, body=payload.dict(exclude_none=True)
        )
        asyncio.create_task(coroutine)

    def log_entry(self, obj, event):
        document = {}
        user = get_authenticated_user()

        if IObjectDuplicatedEvent.providedBy(event):
            document["action"] = "duplicated"
            document["creation_date"] = datetime.datetime.now(timezone.utc)
        elif IObjectMovedEvent.providedBy(event):
            document["action"] = "moved"
            document["creation_date"] = datetime.datetime.now(timezone.utc)
        elif IObjectPermissionsModifiedEvent.providedBy(event):
            document["action"] = "permissions_changed"
            document["creation_date"] = datetime.datetime.now(timezone.utc)
        elif IObjectModifiedEvent.providedBy(event):
            document["action"] = "modified"
            document["creation_date"] = obj.modification_date
            if self._settings.get("save_payload", False) is True:
                document["payload"] = json.dumps(
                    event.payload, default=self._custom_serializer
                )
        elif IObjectAddedEvent.providedBy(event):
            document["action"] = "added"
            document["creation_date"] = obj.creation_date
            if self._settings.get("save_payload", False) is True:
                document["payload"] = json.dumps(
                    event.payload, default=self._custom_serializer
                )
        elif IObjectRemovedEvent.providedBy(event):
            document["action"] = "removed"
            document["creation_date"] = datetime.datetime.now(timezone.utc)
        document["path"] = get_content_path(obj)
        document["creator"] = user.id
        document["type_name"] = obj.type_name
        document["uuid"] = obj.uuid
        coroutine = self.async_es.index(index=self.index, body=document)
        asyncio.create_task(coroutine)

    async def query_audit(self, query):
        container = get_current_container()
        query = parse_query(container, query, self)
        result = await self.async_es.search(index=self.index, body=query)
        return result.body

    async def close(self):
        if self.loop is not None:
            asyncio.run_coroutine_threadsafe(self.async_es.close(), self.loop)
        else:
            await self.async_es.close()

    async def finalize(self, app):
        await self.close()
