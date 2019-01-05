import click
import subprocess

@click.group()
def cli():
    """Create and use encrypted environments"""

@cli.command()
@click.option("-s", "--size", default="10", help="Image size in megabytes")
@click.argument("filename", type=click.Path(dir_okay=False, writable=True,
                                            allow_dash=False))
def create(size, filename):
    """Create a new encrypted environment"""
    subprocess.check_call(["hdiutil", "create",
                           "-fs", "apfs",
                           "-megabytes", str(size),
                           filename])

if __name__ == '__main__':
    cli()
