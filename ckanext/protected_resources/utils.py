# -*- coding: utf-8 -*-
from __future__ import print_function

from six import text_type
import os

import ckan.plugins.toolkit as tk
from ckan import model

try:
    tk.requires_ckan_version("2.9")
except tk.CkanVersionException:
    from ckan.lib.cli import parse_db_config
else:
    from ckan.model import parse_db_config


def _redirect_to_resource(dataset_id, resource_id):
    return tk.redirect_to(
        controller='resource' if tk.check_ckan_version('2.9') else 'package',
        action='read' if tk.check_ckan_version('2.9') else 'resource_read',
        id=dataset_id,
        resource_id=resource_id)


def unlock(dataset_id, resource_id):
    try:
        context = {'model': model, 'user': tk.c.user}
        access = tk.check_access(
            'protected_resource_lock',
            context,
            {'resource_id': resource_id})
        if not access:
            tk.abort(401, 'You are not authorized to unlock resources')

        tk.get_action('protected_resource_unlock')(
            context, {'resource_id': resource_id})
    except tk.ObjectNotFound:
        tk.abort(404, 'Resource object not found')
    except tk.NotAuthorized:
        tk.abort(401, 'You are not authorized to protect this resource')
    except Exception as e:
        msg = 'An error occured while unlocking your resource: [{}]'.format(
            text_type(e))
        tk.abort(500, msg)

    return _redirect_to_resource(dataset_id, resource_id)


def lock(dataset_id, resource_id):
    try:
        context = {'model': model, 'user': tk.c.user}
        if not tk.check_access('protected_resource_lock', context):
            tk.abort(401, 'You are not authorized to lock resources')
        tk.get_action('protected_resource_lock')(
            context, {'resource_id': resource_id})
    except tk.ObjectNotFound:
        tk.abort(404, 'Resource object not found')
    except tk.NotAuthorized:
        tk.abort(401, 'You are not authorized to lock resources')
    except Exception as e:
        msg = 'An error occured while locking your resource: [{}]'.format(
            str(e))
        tk.abort(500, msg)

    return _redirect_to_resource(dataset_id, resource_id)


def setup_protected_resources(**kwargs):
    template_filename = os.path.join(os.path.dirname(__file__),
                                     u'set_protected_resource_table.sql')
    with open(template_filename) as f:
        content = f.read()
        print(content.format(**parse_db_config()))
