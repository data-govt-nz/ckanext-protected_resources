# -*- coding: utf-8 -*-
from flask import Blueprint

import ckanext.protected_resources.utils as utils


protected_resource = Blueprint("protected_resource", __name__)


def unlock(dataset_id, resource_id):
    return utils.unlock(dataset_id, resource_id)


def lock(dataset_id, resource_id):
    return utils.lock(dataset_id, resource_id)


protected_resource.add_url_rule(
    "/dataset/<dataset_id>/resource/<resource_id>/lock",
    view_func=lock
)

protected_resource.add_url_rule(
    "/dataset/<dataset_id>/resource/<resource_id>/unlock",
    view_func=unlock
)


def get_blueprints():
    return [protected_resource]
