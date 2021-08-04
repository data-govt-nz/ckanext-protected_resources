from __future__ import print_function

import sys
from ckan.lib.cli import CkanCommand

import ckanext.protected_resources.utils as utils


class Admin(CkanCommand):
    '''Sets up the protected resource plugin

    Usage:

      admin help
        - prints this help

      admin setup-protected-resources
        - setup the db table for protected resources
    '''
    summary = __doc__.split('\n')[0]
    usage = __doc__

    def help(self):
        print(self.__doc__)

    def command(self):
        # load pylons config
        self._load_config()
        options = {
            'setup-protected-resources': self.setup_protected_resources,
            'help': self.help,
        }

        try:
            cmd = self.args[0]
            options[cmd](*self.args[1:])
        except (KeyError, IndexError):
            self.help()
            sys.exit(1)

    def setup_protected_resources(self, **kwargs):
        utils.setup_protected_resources(**kwargs)
