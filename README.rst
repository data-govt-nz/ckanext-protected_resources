
=============
ckanext-protected_resources
=============

protected_resources is a simple plugin for allowing system administrators the capability to stop deletes from happening.

- When a resource is protected, all users will not be allwed to delete the resource
- A dataset with a protected resource will not be able to be deleted.
- Only a sysadmin can update the protected status of a resource.
- A protected resource can still have it's description/data updated

------------
Requirements
------------

1. Tested and developed for anything newer than CKAN 2.7.
2. Requires the scheming plugin.


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

5. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu::

     sudo service apache2 reload


---------------------------------
Registering ckanext-protected_resources on PyPI
---------------------------------

ckanext-protected_resources should be availabe on PyPI as
https://pypi.python.org/pypi/ckanext-protected_resources. If that link doesn't work, then
you can register the project on PyPI for the first time by following these
steps:

1. Create a source distribution of the project::

     python setup.py sdist

2. Register the project::

     python setup.py register

3. Upload the source distribution to PyPI::

     python setup.py sdist upload

4. Tag the first release of the project on GitHub with the version number from
   the ``setup.py`` file. For example if the version number in ``setup.py`` is
   0.0.1 then do::

       git tag 0.0.1
       git push --tags


----------------------------------------
Releasing a New Version of ckanext-protected_resources
----------------------------------------

ckanext-protected_resources is availabe on PyPI as https://pypi.python.org/pypi/ckanext-protected_resources.
To publish a new version to PyPI follow these steps:

1. Update the version number in the ``setup.py`` file.
   See `PEP 440 <http://legacy.python.org/dev/peps/pep-0440/#public-version-identifiers>`_
   for how to choose version numbers.

2. Create a source distribution of the new version::

     python setup.py sdist

3. Upload the source distribution to PyPI::

     python setup.py sdist upload

4. Tag the new release of the project on GitHub with the version number from
   the ``setup.py`` file. For example if the version number in ``setup.py`` is
   0.0.2 then do::

       git tag 0.0.2
       git push --tags
