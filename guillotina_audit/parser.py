# https://docs.google.com/document/d/1xooubzJKBnUzVlsa2f0GSwvuE1oir9hUdWUf1SU9S6E/edit
from guillotina import configure
from guillotina.catalog.parser import BaseParser
from guillotina.interfaces import IResource
from guillotina.interfaces import ISearchParser
from guillotina_audit.interfaces import IAuditUtility
from guillotina_audit.interfaces import ParsedQueryInfo

import typing


@configure.adapter(
    for_=(IAuditUtility, IResource), provides=ISearchParser, name="audit"
)
class Parser(BaseParser):
    def __call__(self, params: typing.Dict) -> ParsedQueryInfo:
        if params == {}:
            query = {"query": {"match_all": {}}}
        else:
            query = {"query": {"bool": {"must": []}}}
            for field, value in params.items():
                if (
                    field.endswith("__gte")
                    or field.endswith("__lte")
                    or field.endswith("__gt")
                    or field.endswith("__lt")
                ):
                    field_parsed = field.split("__")[0]
                    operator = field.split("__")[1]
                    query["query"]["bool"]["must"].append(
                        {"range": {field_parsed: {operator: value}}}
                    )
                else:
                    query["query"]["bool"]["must"].append({"match": {field: value}})
        return typing.cast(ParsedQueryInfo, query)
