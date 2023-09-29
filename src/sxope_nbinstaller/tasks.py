import io
import sys
from unittest import mock
from pathlib import Path
import subprocess

from .misc import task, urlfixer, printwarn


@task("install package package from {url} (ref. {ref})")
def pip_install(url, token="", ref="", test=False):
    o = urlfixer(url, token, ref)
    scheme = o.scheme
    if not scheme.startswith("git+"):
        o = o._replace(scheme=f"git+{o.scheme}")
    cmd = ["pip", "install", "--force-reinstall", o.geturl()]
    if test:
        print(" ".join(str(c) for c in cmd))
        return
    run = subprocess.check_output([str(c) for c in cmd], encoding="utf-8")
    print(f"pip installed {url}")
    if run.strip():
        print(run)


@task("checkout source code in '{destdir}'")
def git_clone(destdir, url, token="", ref="", test=False):
    destdir = Path(destdir).absolute()
    if destdir.exists():
        printwarn(
            f"""\
found {destdir}
not checking out sxope-bigq
(did you mean to use the mode='dev'?)
""",
            multiline=True,
        )
        return

    o = urlfixer(url, token, ref)

    cmd = [
        "git",
        "clone",
        o.geturl(),
        destdir,
    ]
    if test:
        print(" ".join(str(c) for c in cmd))
        return
    run = subprocess.check_output([str(c) for c in cmd], encoding="utf-8")
    print(f"git cloned in {destdir}")
    if run.strip():
        print(run)


@task("adding '{path}' to PYTHONPATH")
def add_pypath(path):
    sys.path.insert(0, str(path))


@task("mounting gdrive under '{mountpoint}' (readonly? {readonly})")
def mount(mountpoint: Path, readonly: bool = True) -> Path:
    from google.colab import drive

    with mock.patch("sys.stdout", new_callable=io.StringIO):
        drive.mount(str(mountpoint), force_remount=True, readonly=readonly)
    print(f"drive mounted under {mountpoint}")
    return Path(mountpoint)


if __name__ == "__main__":
    import getpass

    token = getpass.getpass("Github token? ")
    git_clone(
        "x",
        "https://github.com/antonio-cavallo/sxope-bigq.git",
        token=token,
        test=False,
    )
