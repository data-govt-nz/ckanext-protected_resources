from six import text_type
from ckan.common import config
from ckan import model


def sysadmin_email():
    return text_type(config.get('smtp.mail_from', ''))


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
    A helper function for checking if a package dict contains a protected
    resource.
    :param package_dict:
    :return:
    """
    resource_ids = tuple([r['id'] for r in package_dict.get('resources', [])])
    if len(resource_ids) == 0:
        return False

    query = """
        SELECT resource_id
        FROM resource_protected WHERE resource_id in :ids"""
    result = model.Session.execute(query, {'ids': resource_ids})
    return result.rowcount > 0
