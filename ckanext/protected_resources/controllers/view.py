# -*- coding: utf-8 -*-

from ckan.lib.base import BaseController

import ckanext.protected_resources.utils as utils


class ViewController(BaseController):

    def unlock(self, dataset_id, resource_id):
        utils.unlock(dataset_id, resource_id)

    def lock(self, dataset_id, resource_id):
        utils.lock(dataset_id, resource_id)
