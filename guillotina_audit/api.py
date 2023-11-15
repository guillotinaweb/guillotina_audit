from guillotina import configure
from guillotina.api.service import Service
from guillotina.component import query_utility
from guillotina.interfaces import IContainer
from guillotina_audit.interfaces import IAuditUtility


@configure.service(
    context=IContainer,
    method="GET",
    permission="audit.AccessContent",
    name="@audit",
    summary="Get the audit entry logs",
    responses={
        "200": {"description": "Get the audit entry logs", "schema": {"properties": {}}}
    },
)
class AuditGET(Service):
    async def __call__(self):
        audit_utility = query_utility(IAuditUtility)
        return await audit_utility.query_audit(self.request.query)
