import click

from py_crap.cli.scan import scan_cmd
from py_crap.cli.version import version_cmd


@click.group()
def cli() -> None:
    """CRAP score calculator for Python projects."""


cli.add_command(scan_cmd)
cli.add_command(version_cmd)
