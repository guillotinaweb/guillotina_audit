from guillotina.async_util import IAsyncUtility
from guillotina.catalog.types import BasicParsedQueryInfo

import typing


class IAuditUtility(IAsyncUtility):
    pass


class ParsedQueryInfo(BasicParsedQueryInfo):
    query: typing.Dict
