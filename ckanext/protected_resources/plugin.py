import logging
import ckan.plugins as p
import ckan.plugins.toolkit as tk
import ckan.logic as logic
import ckan.authz as authz
from ckan.logic.auth import get_resource_object
from ckan.logic.validators import Invalid

log = logging.getLogger(__name__)


# DONE can_delete is turned off if the resource is protected
# DONE (I can not update if I'm not protected) hide field if the person is not a sysadmin
# DONE extended to include a field for blocking deletion
# DONE only admin can update the protected status

# TODO consider A better design
# 1. resource_protect action
# 2. auth function for resource_protect
# 3. a template is expanded to support the


def resource_delete(context, data_dict):
    """
    Calls the core resource delete and then checks if it is a protected resource
    :param context: dict
    :param data_dict: dict
    :return: success_dict: dict
    """
    can_delete = logic.auth.delete.resource_delete(context, data_dict)
    log.warning('Resource plugin hook %s and data %s' % (can_delete, data_dict))
    if can_delete.get('success', None):
        resource = get_resource_object(context, data_dict)
        if resource.extras.get('is_protected', None):
            return {'success': False, 'msg': 'Not able to delete a protected resource'}
        return can_delete
    return {'succes': True}


def protected_sysadmin_only(value, context):
    """
    A Validator that throws invalid if a non sysadmin is change the field

    When called in a 'new' then default to False
    """
    user = context.get('auth_user_obj', None)
    from pprint import pformat
    log.warning('TRYING TO UPDATE BUT SHOULD DEFAULT OUTT\n%s' % pformat(context))
    if user and user.sysadmin:
        return value
    elif not context.get('for_edit', False): # default to false for creation requests
        return False
    else:
        raise Invalid('Only a sysadmin can update this field')

def boolean_to_string(value):
    if value:
        return 'True'
    else:
        return 'False'

class Protected_ResourcesPlugin(p.SingletonPlugin):
    p.implements(p.IResourceController)
    p.implements(p.IAuthFunctions)
    p.implements(p.IValidators)

    def get_validators(self):
        return {
            'protected_sysadmin_only': protected_sysadmin_only,
            'boolean_to_string': boolean_to_string,
        }

    def get_auth_functions(self):
        return {
            'resource_delete': resource_delete
        }

    def before_create(self, context, resource):
        pass

    def after_create(self, context, resource):
        pass

    def before_update(self, context, current, resource):
        pass

    def after_update(self, context, resource):
        pass

    def before_delete(self, context, resource, resources):
        # log.warning("Checking resource to see if we should block deletion: %s" % resource)
        #
        # raise Exception('This should block all deletes!')
        pass

    def after_delete(self, context, resources):
        pass

    def before_show(self, resource_dict):
        return resource_dict