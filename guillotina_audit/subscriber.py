from guillotina import configure
from guillotina.component import query_utility
from guillotina.interfaces import IObjectAddedEvent
from guillotina.interfaces import IObjectDuplicatedEvent
from guillotina.interfaces import IObjectModifiedEvent
from guillotina.interfaces import IObjectMovedEvent
from guillotina.interfaces import IObjectPermissionsModifiedEvent
from guillotina.interfaces import IObjectRemovedEvent
from guillotina.interfaces import IResource
from guillotina_audit.interfaces import IAuditUtility

import logging


logger = logging.getLogger("guillotina_audit")


@configure.subscriber(
    for_=(IResource, IObjectAddedEvent), priority=1001
)  # after indexing
async def audit_object_added(obj, event):
    try:
        if event.__providedBy__(IObjectDuplicatedEvent) is True:
            pass
        elif event.__providedBy__(IObjectMovedEvent) is True:
            pass
        elif event.__providedBy__(IObjectAddedEvent) is True:
            audit = query_utility(IAuditUtility)
            audit.log_entry(obj, event)
    except Exception:
        logger.error("Error adding audit", exc_info=True)


@configure.subscriber(
    for_=(IResource, IObjectModifiedEvent), priority=1001
)  # after indexing
async def audit_object_modified(obj, event):
    try:
        if event.__providedBy__(IObjectPermissionsModifiedEvent) is True:
            audit = query_utility(IAuditUtility)
            if audit._settings.get("index_permission_changes", False) is True:
                audit.log_entry(obj, event)
        elif event.__providedBy__(IObjectModifiedEvent):
            audit = query_utility(IAuditUtility)
            audit.log_entry(obj, event)
    except Exception:
        logger.error("Error adding audit", exc_info=True)


@configure.subscriber(
    for_=(IResource, IObjectRemovedEvent), priority=1001
)  # after indexing
async def audit_object_removed(obj, event):
    try:
        audit = query_utility(IAuditUtility)
        audit.log_entry(obj, event)
    except Exception:
        logger.error("Error adding audit", exc_info=True)


@configure.subscriber(
    for_=(IResource, IObjectMovedEvent), priority=1001
)  # after indexing
async def audit_object_moved(obj, event):
    try:
        audit = query_utility(IAuditUtility)
        audit.log_entry(obj, event)
    except Exception:
        logger.error("Error adding audit", exc_info=True)


@configure.subscriber(
    for_=(IResource, IObjectDuplicatedEvent), priority=1001
)  # after indexing
async def audit_object_duplicated(obj, event):
    try:
        audit = query_utility(IAuditUtility)
        audit.log_entry(obj, event)
    except Exception:
        logger.error("Error adding audit", exc_info=True)
