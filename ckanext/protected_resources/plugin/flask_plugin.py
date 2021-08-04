# -*- coding: utf-8 -*-

from six import text_type
from logging import getLogger

import ckan.plugins as p
import ckanext.protected_resources.views as views
import ckanext.protected_resources.cli as cli


log = getLogger(__name__)


class Mixin(p.SingletonPlugin):
    p.implements(p.IClick)
    p.implements(p.IBlueprint)

    # ICLick
    def get_commands(self):
        commands = cli.get_commands()
        log.info("Registering commands %s", text_type(commands[0].commands))
        return commands

    # IBlueprint
    def get_blueprint(self):
        return views.get_blueprints()
