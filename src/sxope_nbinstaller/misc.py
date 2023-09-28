import io
from unittest import mock
from pathlib import Path
import functools
import subprocess


OK = "✅"
E = "❌"
W = "🟡"


def indent(txt: str, pre=" " * 2) -> str:
    from textwrap import dedent

    while txt and txt.startswith("\n"):
        txt = txt[1:]
    while txt and txt.endswith("\n"):
        txt = txt[:-1]

    txt = dedent(txt)
    return "\n".join(f"{pre}{line}" for line in txt.split("\n"))


def printx(msg, multiline=False, tag=OK):
    if multiline:
        head, _, body = msg.partition("\n")
        print(f"{tag} {head}")
        print(indent(body, " "*len(tag) + " "))
    else:
        print(f"{tag} {msg}")


printok = functools.partial(printx, tag=OK)
printerr = functools.partial(printx, tag=E)
printwarn = functools.partial(printx, tag=W)


def task(msg):
    def _fn0(fn):
        def _fn1(*args, **kwargs):
            from inspect import getcallargs
            kwargs = getcallargs(fn, *args, **kwargs)
            print(f"{msg.format(**kwargs)} .. ", end="")
            try:
                out = ""
                with mock.patch("sys.stdout", new_callable=io.StringIO) as mck:
                    try:
                        result = fn(**kwargs)
                    finally:
                        out = mck.getvalue()
                print(OK)
                if out.strip():
                    print(indent(out, "|  "))
                return result
            except:
                print(E)
                if out.strip():
                    print(indent(out, "|  "))
                raise
        return _fn1
    return _fn0


def _fixurl(url, token="", ref=""):
    from urllib.parse import urlparse    
    o = urlparse(url)
    if token:
        o = o._replace(netloc=f"{token}@{o.netloc}")
    if ref:
        o = o._replace(path=f"{o.path}@{ref.lstrip('@')}")
    return o


@task("install package package from {url} (ref. {ref})")
def pip_install(url, token="", ref="", test=False): 
    o = _fixurl(url, token, ref)
    scheme = o.scheme
    if not scheme.startswith("git+"):
        o = o._replace(scheme=f"git+{o.scheme}")
    cmd = [
        "pip", "install",
        "--force-reinstall",
        o.geturl()
    ]
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
        printwarn(f"""\
found {destdir}
not checking out sxope-bigq
(did you mean to use the mode='dev'?)
""", multiline=True)
        return

    o = _fixurl(url, token, ref)

    cmd = [
        "git", "clone",
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


if __name__ == "__main__":
    import getpass
    token = getpass.getpass("Github token? ")
    git_clone("x", "https://github.com/antonio-cavallo/sxope-bigq.git", token=token, test=False)

