from ckan.lib.base import BaseController, c
from ckan import model
import ckan.plugins.toolkit as tk

class ProtectedResourceController(BaseController):

    def unlock(self, dataset_id, resource_id):
        try:
            context = {'model': model, 'user': c.user}
            if not tk.check_access('protected_resource_lock', context, {'resource_id': resource_id}):
                tk.abort(401, 'You are not authorized to unlock resources')

            tk.get_action('protected_resource_unlock')(context, {'resource_id': resource_id})
        except tk.ObjectNotFound:
            tk.abort(404, 'Resource object not found')
        except tk.NotAuthorized:
            tk.abort(401, 'You are not authorized to protect this resource')
        except Exception, e:
            msg = 'An error occured while unlocking your resource: [{}]'.format(str(e))
            tk.abort(500, msg)
        tk.redirect_to(controller='package', action='resource_read', id=dataset_id, resource_id=resource_id)

    def lock(self, dataset_id, resource_id):
        try:
            context = {'model': model, 'user': c.user}
            if not tk.check_access('protected_resource_lock', context):
                tk.abort(401, 'You are not authorized to lock resources')
            tk.get_action('protected_resource_lock')(context, {'resource_id': resource_id})
        except tk.ObjectNotFound:
            tk.abort(404, 'Resource object not found')
        except tk.NotAuthorized:
            tk.abort(401, 'You are not authorized to lock resources')
        except Exception, e:
            msg = 'An error occured while locking your resource: [{}]'.format(str(e))
            tk.abort(500, msg)

        tk.redirect_to(controller='package', action='resource_read', id=dataset_id, resource_id=resource_id)

