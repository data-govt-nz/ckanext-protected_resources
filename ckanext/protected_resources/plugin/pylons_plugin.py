# -*- coding: utf-8 -*-

import ckan.plugins as p


class Mixin(p.SinglePlugin):
    p.implements(p.IRoutes, inherit=True)

    # IRoutes
    def before_map(self, map):
        controller = \
            'ckanext.protected_resources.controllers.view:ViewController'
        map.connect(
            'protected_resource_lock',
            '/dataset/{dataset_id}/resource/{resource_id}/lock',
            controller=controller,
            action='lock')
        map.connect(
            'protected_resource_unlock',
            '/dataset/{dataset_id}/resource/{resource_id}/unlock',
            controller=controller,
            action='unlock')
        return map
