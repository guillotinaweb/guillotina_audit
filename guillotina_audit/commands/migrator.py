from guillotina.commands import Command
from guillotina_audit.migrator import Migrator


class MigratorCommand(Command):
    description = "Migrate index"
    migrator = None
    reindexer = None

    def get_parser(self):
        parser = super(MigratorCommand, self).get_parser()
        return parser

    async def run(self, arguments, settings, app):
        migrator = Migrator()
        await migrator.migrate()
