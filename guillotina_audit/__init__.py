from guillotina import configure


app_settings = {
    "load_utilities": {
        "audit": {
            "provides": "guillotina_audit.interfaces.IAuditUtility",
            "factory": "guillotina_audit.utility.AuditUtility",
            "settings": {
                "index_name": "audit",
                "save_payload": False,
                "index_permission_changes": False,
            },
        }
    },
    "commands": {
        "audit-update-mappings": "guillotina_audit.commands.mappings.UpdateMappingsCommand",
        "audit-update-settings": "guillotina_audit.commands.settings.UpdateSettingsCommand",
    },
}


def includeme(root, settings):
    configure.scan("guillotina_audit.install")
    configure.scan("guillotina_audit.utility")
    configure.scan("guillotina_audit.subscriber")
    configure.scan("guillotina_audit.api")
    configure.scan("guillotina_audit.permissions")
    configure.scan("guillotina_audit.models")
    configure.scan("guillotina_audit.parser")
