from guillotina import configure
from guillotina.content import Resource
from guillotina.interfaces import IContainer
from guillotina.interfaces import IResource
from guillotina.schema import Datetime
from zope.interface import implementer


class IFooContent(IResource):
    foo_datetime = Datetime(title="Foo Datetime")


@implementer(IFooContent)
class FooContent(Resource):
    pass


configure.register_configuration(
    FooContent,
    dict(
        context=IContainer,
        schema=IFooContent,
        type_name="FooContent",
        behaviors=["guillotina.behaviors.dublincore.IDublinCore"],
    ),
    "contenttype",
)
