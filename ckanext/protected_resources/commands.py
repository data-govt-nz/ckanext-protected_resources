from ckan.lib.cli import CkanCommand
import sys

class AdminCommand(CkanCommand):
    '''
    Usage: paster --plugin=ckanext-protected_resources admin <command> -c <path to config file>

        command:
        help - prints this help
        setup-protected-resources - setup the db table for protected resources
    '''
    summary = __doc__.split('\n')[0]
    usage = __doc__


    def help(self):
        print self.__doc__

    def command(self):
        # load pylons config
        self._load_config()
        options = {
            'setup-protected-resources-table': self.setup_protected_resources,
            'help': self.help,
        }

        try:
            cmd = self.args[0]
            options[cmd](*self.args[1:])
        except (KeyError, IndexError):
            self.help()
            sys.exit(1)

    def setup_protected_resources(self, **kwargs):
        from pprint import pformat
        print("args to this are....")
        print(pformat(kwargs))