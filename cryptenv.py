import click
import subprocess
import plistlib

@click.group()
def cli():
    """Create and use encrypted environments"""

@cli.command()
@click.option("-s", "--size", default="10", help="Image size in megabytes")
@click.argument("filename", type=click.Path(dir_okay=False, writable=True,
                                            allow_dash=False))
def create(size, filename):
    """Create a new encrypted environment"""
    output = subprocess.check_output(["hdiutil", "create",
                                      "-plist",
                                      "-fs", "apfs",
                                      "-volname", "cryptenv",
                                      "-megabytes", str(size),
                                      filename])
    structured_out = plistlib.loads(output)
    created_file = structured_out[0]
    click.echo("Created image: {}".format(created_file))

if __name__ == '__main__':
    cli()
