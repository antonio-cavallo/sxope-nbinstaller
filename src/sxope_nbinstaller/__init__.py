import io
import sys
import os
import getpass

import subprocess
from pathlib import Path
from unittest import mock

REF = "beta/0.0.0"  # bigq reference to install for prod

W = "🟡"
E = "❌"
OK = "✅"


def indent(txt: str, pre=" " * 2) -> str:
    from textwrap import dedent

    while txt and txt.startswith("\n"):
        txt = txt[1:]
    while txt and txt.endswith("\n"):
        txt = txt[:-1]

    txt = dedent(txt)
    return "\n".join(f"{pre}{line}" for line in txt.split("\n"))


def task(msg):
    def _fn0(fn):
        def _fn1(*args, **kwargs):
            from inspect import getcallargs
            kwargs = getcallargs(fn, *args, **kwargs)
            print(f"{msg.format(**kwargs)} .. ", end="")
            try:
                with mock.patch("sys.stdout", new_callable=io.StringIO) as mck:
                    result = fn(**kwargs)
                print("✅")
                out = mck.getvalue()
                if out.strip():
                    print(indent(out, "|  "))
                return result
            except:
                print("❌")
                out = mck.getvalue()
                if out.strip():
                    print(indent(out, "|  "))
                raise
        return _fn1
    return _fn0


@task("install bigq package (ref. {ref})")
def install(token, ref=""):
    cmd = [
        "pip", "install",
        "--force-reinstall",
        f"git+https://{token}@github.com/antonio-cavallo/sxope-bigq{ref}"
    ]
    run = subprocess.check_output([str(c) for c in cmd], encoding="utf-8")
    print(f"installed sxope-bigq package")
    if run.strip():
        print(run)


@task("checkout source code for sxope-bigq in '{destdir}'")
def checkout(token, destdir):
    if destdir.exists():
        print(f"""\
{W} {destdir} is present, not checking out sxope-bigq
  (did you mean to use the mode='dev'?)
""")
        return
    
    cmd = [
        "git", "clone",
        f"https://{token}@github.com/antonio-cavallo/sxope-bigq.git",
        destdir
    ]

    run = subprocess.check_output([str(c) for c in cmd], encoding="utf-8")
    print(f"check out sxope-bigq.git in {destdir}")
    if run.strip():
        print(run)


@task("mounting gdrive under '{mountpoint}' (readonly? {readonly})")
def mount(mountpoint: Path, readonly: bool = True) -> Path:
    from google.colab import drive
    with mock.patch('sys.stdout', new_callable=io.StringIO) as mck:
        drive.mount(str(mountpoint), force_remount=True, readonly=readonly)
    print(f"drive mounted under {mountpoint}")
    return Path(mountpoint)


@task("adding '{path}' to PYTHONPATH")
def add_pypath(path):
  sys.path.insert(0, str(path))


def setup(
    mode="dev",
    mountpoint=None,
    destdir=None,
):
    """setup the notebook

    In prod mode it will install the sxope-bigq library.
    In dev mode it will:
        mount the user's GDrive under mount point (readonly)
        set the PYTHONPATH to destdir / src

    In dev-install it will:
        mount the user's GDrive under mount point (writeable)
        checkout sxope-bigq project under destdir
        set the PYTHONPATH to destdir / src
        
    NOTE: dev-install is a useful one-off command, once the
          source code id checked out under destdir you don't want
          to re-run it.!

    Examples:

        sxope_nbinstaller.install("dev-install",
            mountpoint="/content/GDrive",
            destdir="{mountpoint}/MyDrive/Projects/sxope-bigq"
        )
    """
    assert mode in { "prod", "dev-install", "dev" }

    if mode == "prod":
        token = getpass.getpass("Please provide the token for sxope-bigq: ")
        install(token, "beta/0.0.0")
        from bigq.nb.utils import check_notebook
        return check_notebook()

    if mode in { "dev", "dev-install" } and not (mountpoint and destdir):
        print(f'''\
❌ In dev mode you need the mountpoint/destdir args:

    sxope_nbinstaller.install("{mode}", mountpoint=..., destdir=...)
''')
        return

    destdir = Path(destdir.format(mountpoint=mountpoint))
    mountpoint = Path(mountpoint)

    # mount the GDrive
    mount(mountpoint, readonly=True if mode == "dev" else False)
    
    if mode == "dev-install":
        token = None
        if not destdir.exists():
            token = getpass.getpass("Please provide the token for sxope-bigq: ")
        checkout(token, destdir)

    add_pypath(destdir / "src")

    # moment of truth
    from bigq.nb.utils import check_notebook
    print("Verify system:")
    return check_notebook()
