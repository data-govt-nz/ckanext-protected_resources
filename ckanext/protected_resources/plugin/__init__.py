# -*- coding: utf-8 -*-

import logging

import ckan.plugins as p
import ckan.plugins.toolkit as tk

try:
    p.toolkit.requires_ckan_version("2.9")
except p.toolkit.CkanVersionException:
    from ckanext.protected_resources.plugin.pylons_plugin import Mixin
else:
    from ckanext.protected_resources.plugin.flask_plugin import Mixin

from ckanext.protected_resources import helpers
from ckanext.protected_resources.logic import (
    protected_resource_lock,
    protected_resource_unlock,
    resource_delete_override,
    auth_protected_resource_lock,
    resource_delete,
    package_delete
)


log = logging.getLogger(__name__)


class Protected_ResourcesPlugin(Mixin, tk.DefaultDatasetForm):
    p.implements(p.IAuthFunctions)
    p.implements(p.IActions)
    p.implements(p.IConfigurer)
    p.implements(p.ITemplateHelpers)

    # ITemplateHelpers
    def get_helpers(self):
        return {
            'resource_has_protected_status':
                helpers.resource_has_protected_status,
            'package_has_protected_resource':
                helpers.package_has_protected_resource,
            'sysadmin_email': helpers.sysadmin_email,
            'check_ckan_version': tk.check_ckan_version,
        }

    # IConfigurer
    def update_config(self, config):
        tk.add_template_directory(config, '../templates')

    # IActions
    def get_actions(self):
        return {
            'protected_resource_lock': protected_resource_lock,
            'protected_resource_unlock': protected_resource_unlock,
            'resource_delete': resource_delete_override
        }

    # IAuthFunctions
    def get_auth_functions(self):
        return {
            'protected_resource_lock': auth_protected_resource_lock,
            'resource_delete': resource_delete,
            'package_delete': package_delete,
        }
