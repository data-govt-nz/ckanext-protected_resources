from six import text_type
import logging
import uuid

from ckan.logic.auth import get_resource_object, get_package_object
from ckan.logic.action.delete import resource_delete as resource_delete_core

import ckan.plugins as p
import ckan.logic as logic
import ckan.plugins.toolkit as tk
from ckan import model

import ckanext.protected_resources.helpers as helpers


log = logging.getLogger(__name__)


def resource_delete(context, data_dict):
    """Auth function override of ckan.logic.auth.delete.resource_delete function
    Re-implement the resource_delete auth function so that we check the
    protected status of a function before allowing deletion.

    :param context: dict
    :param data_dict: dict
    :return: success_dict: dict
    """
    model = context['model']
    resource = get_resource_object(context, data_dict).as_dict()

    # check authentication against package
    pkg = model.Package.get(resource['package_id'])
    if not pkg:
        raise logic.NotFound(
            'No package found for this resource, cannot check auth.')

    pkg_dict = {'id': pkg.id}

    # if you can update a package then you can delete it
    can_update = tk.check_access('package_update', context, pkg_dict)
    if can_update:
        if helpers.resource_has_protected_status(resource['id']):
            return {
                'success': False,
                'msg': 'Contact a system administrator to delete this resource'
            }
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
        is_protected = helpers.package_has_protected_resource(pkg)
        if is_protected:
            msg = {
                'success': False,
                'msg': "A package with a protected resource can't be deleted"
            }
            return msg
    return {'success': True}


def protected_resource_lock(context, data_dict):
    """Protect a resource from deletion

    This will lock a resource from deletion

    See :ref:`fields` and :ref:`records` for details on how to lay out records.
    :param resource_id: resource id to lock
    :type  resource_id: string

    :return: The resource object updated
    :rtype: dict
    """
    user = context.get('auth_user_obj', None)
    if not user or not user.sysadmin:
        raise p.toolkit.ValidationError(
            ["User must be a sysadmin to protect this resource"])

    if 'resource_id' not in data_dict:
        raise p.toolkit.ValidationError(
            ['resource_id is a required parameter'])

    resource = p.toolkit.get_action('resource_show')(
        context, {'id': data_dict['resource_id']})

    if helpers.resource_has_protected_status(data_dict['resource_id']):
        raise p.toolkit.ValidationError(['This resource is already locked'])
    else:
        qry = "INSERT INTO resource_protected VALUES (:id, :resource_id)"
        model.Session.execute(qry, {
            'id': text_type(uuid.uuid4()),
            'resource_id': data_dict['resource_id']
        })
        model.Session.commit()

    return resource


def protected_resource_unlock(context, data_dict):
    """Protect a resource from deletion

        Removes the resource from the resource_protected table

        See :ref:`fields` and :ref:`records` for details on how to lay out
        records.
        :param resource_id: resource id to lock
        :type  resource_id: string

        :return: The resource object updated
        :rtype: dict
        """
    user = context.get('auth_user_obj', None)
    if not user or not user.sysadmin:
        raise p.toolkit.ValidationError(
            ["User must be a sysadmin to protect this resource"])

    if 'resource_id' not in data_dict:
        raise p.toolkit.ValidationError(
            ['resource_id is a required parameter'])

    resource = p.toolkit.get_action('resource_show')(
        context, {'id': data_dict['resource_id']})

    if not helpers.resource_has_protected_status(data_dict['resource_id']):
        raise p.toolkit.ValidationError([
            'This resource is already unlocked'])
    else:
        qry = "DELETE FROM resource_protected WHERE resource_id = :resource_id"
        model.Session.execute(qry, {
            'resource_id': data_dict['resource_id']
        })
        model.Session.commit()

    return resource


def resource_delete_override(context, data_dict):

    resource = p.toolkit.get_action('resource_show')(context, data_dict)

    if helpers.resource_has_protected_status(resource['id']):
        raise p.toolkit.ValidationError(
            ['A protected resource can never be deleted'])
    return resource_delete_core(context, data_dict)


def auth_protected_resource_lock(context, data_dict=None):
    user = context.get('auth_user_obj', None)
    if not user or not user.sysadmin:
        return {
            'success': False,
            'msg': 'Only a sysadmin can protect resources'
        }
    else:
        return {'success': True}
