from guillotina import configure
from guillotina.component import query_utility
from guillotina.interfaces import IObjectAddedEvent
from guillotina.interfaces import IObjectModifiedEvent
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
        audit = query_utility(IAuditUtility)
        audit.log_entry(obj, event)
    except Exception:
        logger.error("Error adding audit", exc_info=True)


@configure.subscriber(
    for_=(IResource, IObjectModifiedEvent), priority=1001
)  # after indexing
async def audit_object_modified(obj, event):
    try:
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
