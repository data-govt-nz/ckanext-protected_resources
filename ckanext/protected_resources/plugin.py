import logging
import uuid

import ckan.plugins as p
import ckan.plugins.toolkit as tk
import ckan.logic as logic
from ckan.logic.auth import get_resource_object, get_package_object
from ckan.logic.action.delete import resource_delete as resource_delete_core
from ckan import model



log = logging.getLogger(__name__)

def resource_delete(context, data_dict):
    """Auth function override of ckan.logic.auth.delete.resource_delete function
    Re-implement the resource_delete auth function so that we check the protected status of a function before allowing
    deletion.

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
        if resource_has_protected_status(resource['id']):
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
        is_protected = package_has_protected_resource(pkg)
        if is_protected:
            msg = {
                'success': False,
                'msg': "A package with a protected resource can't be deleted"
            }
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

    if resource_has_protected_status(data_dict['resource_id']):
        raise p.toolkit.ValidationError(['This resource is already locked'])
    else:
        qry = "INSERT INTO resource_protected VALUES (:id, :resource_id)"
        model.Session.execute(qry, {
            'id': str(uuid.uuid4()),
            'resource_id': data_dict['resource_id']
        })
        model.Session.commit()

    return resource

def protected_resource_unlock(context, data_dict):
    """Protect a resource from deletion

        Removes the resource from the resource_protected table

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

    if not resource_has_protected_status(data_dict['resource_id']):
        raise p.toolkit.ValidationError(['This resource is already unlocked'])
    else:
        log.error("WE're on the right track my dude")
        qry = "DELETE FROM resource_protected WHERE resource_id = :resource_id"
        model.Session.execute(qry, {
            'resource_id': data_dict['resource_id']
        })
        model.Session.commit()

    updated_resource = p.toolkit.get_action('resource_update')(context, resource)
    return updated_resource


def auth_protected_resource_lock(context, data_dict=None):
    user = context.get('auth_user_obj', None)
    if user and not user.sysadmin:
        return {'success': False, 'msg': 'Only a sysadmin can protect resources'}
    else:
        return {'success': True}

def resource_has_protected_status(resource_id):
    """
    A helper to check if the resource is protected
    :param resource_id: string
    :return: boolean
    """
    qry = """
      SELECT resource_id FROM resource_protected WHERE resource_id=:resource_id
    """
    is_protected = model.Session.execute(qry, {'resource_id': resource_id})
    return is_protected.rowcount > 0

def package_has_protected_resource(package_dict):
    """
    A helper function for checking if a package dict contains a protected resource
    :param package_dict:
    :return:
    """
    resource_ids = tuple([r['id'] for r in package_dict.get('resources', [])])
    if len(resource_ids) == 0:
        return False

    query = 'SELECT resource_id FROM resource_protected WHERE resource_id in :ids'
    result = model.Session.execute(query, {'ids': resource_ids})
    return result.rowcount > 0

def resource_delete_override(context, data_dict):

    resource = p.toolkit.get_action('resource_show')(context, data_dict)

    if resource_has_protected_status(resource['id']):
        raise p.toolkit.ValidationError(['A protected resource can never be deleted'])
    return resource_delete_core(context, data_dict)


class Protected_ResourcesPlugin(p.SingletonPlugin, tk.DefaultDatasetForm):
    p.implements(p.IAuthFunctions)
    p.implements(p.IActions)
    p.implements(p.IConfigurer)
    p.implements(p.IRoutes, inherit=True)
    p.implements(p.ITemplateHelpers)

    def sysadmin_email(self):
        return self.mail_from
    # ITemplateHelpers
    def get_helpers(self):
        return {
            'resource_has_protected_status': resource_has_protected_status,
            'package_has_protected_resource': package_has_protected_resource,
            'sysadmin_email': self.sysadmin_email
        }

    # IConfigurer
    def update_config(self, config):
        tk.add_template_directory(config, 'templates')
        if 'smtp.mail_from' in config:
            self.mail_from = config['smtp.mail_from']

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

    # IRoutes
    def before_map(self, map):
        controller = 'ckanext.protected_resources.controllers:ProtectedResourceController'
        map.connect('protected_resource_lock', '/dataset/{dataset_id}/resource/{resource_id}/lock', controller=controller, action='lock')
        map.connect('protected_resource_unlock', '/dataset/{dataset_id}/resource/{resource_id}/unlock', controller=controller, action='unlock')
        return map
