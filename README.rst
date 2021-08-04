===========================
ckanext-protected_resources
===========================

protected_resources is a simple plugin for allowing system administrators the capability to stop deletes from happening.

- When a resource is protected, all users will not be allwed to delete the resource
- A dataset with a protected resource will not be able to be deleted.
- Only a sysadmin can update the protected status of a resource.
- A protected resource can still have it's description/data updated

------------
Requirements
------------

1. Tested and developed for anything newer than CKAN 2.7.


------------
Installation
------------

.. Add any additional install steps to the list below.
   For example installing any non-Python dependencies or adding any required
   config settings.

To install ckanext-protected_resources:

1. Activate your CKAN virtual environment, for example::

     . /usr/lib/ckan/default/bin/activate

2. Install the ckanext-protected_resources Python package into your virtual environment::

     pip install ckanext-protected_resources

3. Add ``protected_resources`` to the ``ckan.plugins`` setting in your CKAN
   config file (by default the config file is located at
   ``/etc/ckan/default/production.ini``).

4. Add the resource_protected table to your ckan database::

      # ckan >= 2.9
      ckan -c /PATH_TO_YOUR_INI_FILE/FILENAME.ini protected-resources setup-protected-resources | \
               sudo -u postgres pql --set ON_ERROR_STOP=1

     # ckan < 2.9
     paster --plugin=ckanext-protected_resources admin setup-protected-resources | \
          sudo -u postgres pql --set ON_ERROR_STOP=1

5. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu::

     sudo service apache2 reload

