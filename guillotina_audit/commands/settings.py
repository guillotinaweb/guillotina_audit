from guillotina.commands import Command
from guillotina.component import get_utility
from guillotina.interfaces import ICatalogUtility

import asyncio
import logging


logger = logging.getLogger("guillotina_audit")


class UpdateSettingsCommand(Command):
    description = "Update Settings Command"
    migrator = None
    reindexer = None

    def get_parser(self):
        parser = super(UpdateSettingsCommand, self).get_parser()
        return parser

    async def run(self, arguments, settings, app):
        search = get_utility(ICatalogUtility)
        await asyncio.sleep(1)
        await search.update_settings()
