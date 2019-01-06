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
    passphrase = click.prompt("Passphrase for encrypted environment",
                              hide_input=True,
                              confirmation_prompt=True)

    # XXX: don't assume UTF-8
    passphrase = bytes(passphrase, 'utf8')
    passphrase += b'\0'

    output = subprocess.check_output(["hdiutil", "create",
                                      "-plist",
                                      "-encryption",
                                      "-stdinpass",
                                      "-fs", "apfs",
                                      "-volname", "cryptenv",
                                      "-megabytes", str(size),
                                      filename],
                                     input=passphrase)
    structured_out = plistlib.loads(output)
    created_file = structured_out[0]
    click.echo("Created encrypted environment: {}".format(created_file))

@cli.command()
@click.argument("filename", type=click.Path(exists=True, dir_okay=False,
                                            readable=True, allow_dash=False))
def mount(filename):
    """Mount an encrypted environment without entering it"""
    output = subprocess.check_output(["hdiutil", "attach",
                                      "-plist",
                                      filename])
    structured_out = plistlib.loads(output)
    mountpoint = None
    for elem in structured_out['system-entities']:
        if "mount-point" in elem:
            mountpoint = elem['mount-point']
            break

    click.echo("Mounted encrypted environment at {}".format(mountpoint))

if __name__ == '__main__':
    cli()
