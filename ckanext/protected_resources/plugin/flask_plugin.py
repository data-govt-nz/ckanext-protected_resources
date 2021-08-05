# -*- coding: utf-8 -*-

import ckan.plugins as p
import ckanext.protected_resources.views as views
import ckanext.protected_resources.cli as cli


class Mixin(p.SingletonPlugin):
    p.implements(p.IClick)
    p.implements(p.IBlueprint)

    # ICLick
    def get_commands(self):
        return cli.get_commands()

    # IBlueprint
    def get_blueprint(self):
        return views.get_blueprints()
