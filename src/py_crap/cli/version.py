from __future__ import annotations

import click

from py_crap.version import VERSION, splash


@click.command()
@click.option(
    "--simple", "-s",
    is_flag=True,
    default=False,
    help="Prints only the version, useful for scripting",
)
def version_cmd(simple: bool) -> None:
    """Shows py-crap version."""
    if simple:
        click.echo(VERSION)
    else:
        click.echo(splash())
