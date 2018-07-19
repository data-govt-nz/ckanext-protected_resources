import logging
import ckan.plugins as p
import ckan.plugins.toolkit as tk
import ckan.logic as logic
from ckan.logic.auth import get_resource_object, get_package_object
from ckan import model
from ckan.lib.base import BaseController, c

log = logging.getLogger(__name__)


class ProtectedResourceController(BaseController):

    def unlock(self, dataset_id, resource_id):

        try:
            context = {'model': model, 'user': c.user}
            if not tk.check_access('protected_resource_lock', context, {'resource_id': resource_id}):
                tk.abort(401, 'You are not authorized to lock resources')

            p.toolkit.get_action('protected_resource_unlock')(context, {'resource_id': resource_id})
        except p.toolkit.ObjectNotFound:
            tk.abort(404, 'Resource object not found')
        except p.toolkit.NotAuthorized:
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
            p.toolkit.get_action('protected_resource_lock')(context, {'resource_id': resource_id})
        except p.toolkit.ObjectNotFound:
            tk.abort(404, 'Resource object not found')
        except p.toolkit.NotAuthorized:
            tk.abort(401, 'You are not authorized to protect this resource')
        except Exception, e:
            msg = 'An error occured while locking your resource: [{}]'.format(str(e))
            tk.abort(500, msg)

        tk.redirect_to(controller='package', action='resource_read', id=dataset_id, resource_id=resource_id)


def resource_delete(context, data_dict):
    """Auth function override of ckan.logic.auth.delete.resource_delete function
    Re-implement the resource_delete auth function so that we check the is_protected flag on a resource. before allowing deletion

    :param context: dict
    :param data_dict: dict
    :return: success_dict: dict
    """
    model = context['model']
    resource = get_resource_object(context, data_dict).as_dict()

    # check authentication against package
    pkg = model.Package.get(resource['package_id'])
    if not pkg:
        raise logic.NotFound('No package found for this resource, cannot check auth.')

    pkg_dict = {'id': pkg.id}

    # if you can update a package then you can delete it
    can_update = tk.check_access('package_update', context, pkg_dict)
    if can_update:
        if resource.get('is_protected', None):
            return {'success': False, 'msg': 'Contact a system administrator to delete this resource'}
    else:
        return {'success': False, 'msg': 'Resource delete is not allowed'}
    return {'success': True}


def package_delete(context, data_dict):
    """Auth function override for package_delete
    :param context:
    :param data_dict:
    :return:
    """
    log.info("package_delete override called {}".format(data_dict))
    can_delete = logic.auth.delete.package_delete(context, data_dict)
    if can_delete['success']:
        pkg = get_package_object(context, data_dict).as_dict()
        for resource in pkg.get('resources', []):
            if resource.get('is_protected', None):
                msg = {
                    'success': False,
                    'msg': "A package with a protected resource can't be deleted"
                }
                log.info("package_delete is not allowed result msg: {}".format(msg))
                return msg
    return {'success': True}


def protected_resource_lock(context, data_dict):
    """Protect a resource from deletion

    This will update the resource extras field with an is_protected: True value

    See :ref:`fields` and :ref:`records` for details on how to lay out records.
    :param resource_id: resource id to lock
    :type  resource_id: string

    :return: The resource object updated
    :rtype: dict
    """
    user = context.get('auth_user_obj', None)
    if user and not user.sysadmin:
        raise p.toolkit.ValidationError(["User must be a sysadmin to protect this resource"])

    if not 'resource_id' in data_dict:
        raise p.toolkit.ValidationError(['resource_id is a required parameter'])

    resource = p.toolkit.get_action('resource_show')(context, {'id': data_dict['resource_id']})

    resource['is_protected'] = True
    updated_resource = p.toolkit.get_action('resource_update')(context, resource)

    return updated_resource

def protected_resource_unlock(context, data_dict):
    """Protect a resource from deletion

        This will delete the is_protected value

        See :ref:`fields` and :ref:`records` for details on how to lay out records.
        :param resource_id: resource id to lock
        :type  resource_id: string

        :return: The resource object updated
        :rtype: dict
        """
    user = context.get('auth_user_obj', None)
    if user and not user.sysadmin:
        raise p.toolkit.ValidationError(["User must be a sysadmin to protect this resource"])

    if not 'resource_id' in data_dict:
        raise p.toolkit.ValidationError(['resource_id is a required parameter'])

    resource = p.toolkit.get_action('resource_show')(context, {'id': data_dict['resource_id']})

    if 'is_protected' in resource:
        del resource['is_protected']

    updated_resource = p.toolkit.get_action('resource_update')(context, resource)
    return updated_resource


def auth_protected_resource_lock(context, data_dict=None):
    user = context.get('auth_user_obj', None)
    if user and not user.sysadmin:
        return {'success': False, 'msg': 'Only a sysadmin can protect resources'}
    else:
        return {'success': True}

class Protected_ResourcesPlugin(p.SingletonPlugin, tk.DefaultDatasetForm):
    p.implements(p.IAuthFunctions)
    p.implements(p.IActions)
    p.implements(p.IConfigurer)
    p.implements(p.IRoutes, inherit=True)

    def update_config(self, config):
        tk.add_template_directory(config, 'templates')

    # IActions
    def get_actions(self):
        return {
            'protected_resource_lock': protected_resource_lock,
            'protected_resource_unlock': protected_resource_unlock
        }

    # IAuthFunctions
    def get_auth_functions(self):
        return {
            'protected_resource_lock': auth_protected_resource_lock,
            'resource_delete': resource_delete,
            'package_delete': package_delete,
        }

    # IRoutes
    def before_map(self, map):
        controller = 'ckanext.protected_resources.plugin:ProtectedResourceController'
        map.connect('protected_resource_lock', '/dataset/{dataset_id}/resource/{resource_id}/lock', controller=controller, action='lock')
        map.connect('protected_resource_unlock', '/dataset/{dataset_id}/resource/{resource_id}/unlock', controller=controller, action='unlock')
        return map
