import click
import subprocess
import plistlib
import os

def format_hdiutil_passphrase_stdin(string):
    # XXX: don't assume UTF-8
    ret = bytes(string, 'utf8')
    ret += b'\0'
    return ret

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

    output = subprocess.check_output(["hdiutil", "create",
                                      "-plist",
                                      "-encryption",
                                      "-stdinpass",
                                      "-fs", "apfs",
                                      "-volname", "cryptenv",
                                      "-megabytes", str(size),
                                      filename],
                                     input=format_hdiutil_passphrase_stdin(passphrase))
    structured_out = plistlib.loads(output)
    created_file = structured_out[0]
    click.echo("Created encrypted environment: {}".format(created_file))

@cli.command()
@click.argument("filename", type=click.Path(exists=True, dir_okay=False,
                                            readable=True, allow_dash=False))
def mount(filename):
    """Mount an encrypted environment without entering it"""
    passphrase = click.prompt("Passphrase for encrypted environment",
                              hide_input=True)

    output = subprocess.check_output(["hdiutil", "attach",
                                      "-plist",
                                      "-stdinpass",
                                      filename],
                                     input=format_hdiutil_passphrase_stdin(passphrase))
    structured_out = plistlib.loads(output)
    mount_point = None
    for elem in structured_out['system-entities']:
        if 'mount-point' in elem:
            mount_point = elem['mount-point']
            break

    click.echo("Mounted encrypted environment at {}".format(mount_point))

    return mount_point

def find_disk(mount_point):
    output = subprocess.check_output(["hdiutil", "info", "-plist"])
    structured_out = plistlib.loads(output)
    disk = None
    for images in structured_out['images']:
        for image in images['system-entities']:
            if 'mount-point' in image and image['mount-point'] == mount_point:
                disk = image['dev-entry']
                break

    return disk

def do_unmount(disk):
    output = subprocess.check_call(["hdiutil", "detach", disk])

@cli.command()
@click.argument("mount_point", type=click.Path(exists=True, dir_okay=True,
                                               file_okay=False, allow_dash=False))
def unmount(mount_point):
    """Unmount an encrypted environment"""
    disk = find_disk(mount_point)
    do_unmount(disk)

@cli.command()
@click.argument("filename", type=click.Path(exists=True, dir_okay=False,
                                            readable=True, allow_dash=False))
@click.pass_context
def shell(ctx, filename):
    """Mount an encrypted environment and start a shell in it. Unmount the environment when the shell exits"""
    mount_point = ctx.forward(mount)
    # XXX: don't assume the mount point
    subprocess.call(["/bin/bash", "--rcfile", "/Volumes/cryptenv/bashrc", "-i"])
    cryptenv_logout_file = "/Volumes/cryptenv/cryptenv_logout"
    if os.path.exists(cryptenv_logout_file):
        subprocess.call(["/bin/bash", cryptenv_logout_file])
    ctx.invoke(unmount, mount_point=mount_point)

if __name__ == '__main__':
    cli()
