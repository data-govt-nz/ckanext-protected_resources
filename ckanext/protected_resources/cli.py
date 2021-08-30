# -*- coding: utf-8 -*-

import click
import ckanext.protected_resources.utils as utils


def get_commands():
    return [protected_resources]


@click.group(short_help=u"Sets up the protected resource plugin")
def protected_resources():
    pass


@protected_resources.command()
def setup_protected_resources():
    """Creates the necessary tables in the database."""
    utils.setup_protected_resources()
