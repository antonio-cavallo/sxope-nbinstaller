import io
from unittest import mock
import functools


OK = "✅"
E = "❌"
W = "🟡"
RA = "👉"


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
        print(indent(body, " " * len(tag) + " "))
    else:
        print(f"{tag} {msg}")


printok = functools.partial(printx, tag=OK)
printerr = functools.partial(printx, tag=E)
printwarn = functools.partial(printx, tag=W)
printtask = functools.partial(printx, tag=RA)


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


def urlfixer(url, token="", ref=""):
    from urllib.parse import urlparse

    o = urlparse(url)
    if token:
        o = o._replace(netloc=f"{token}@{o.netloc}")
    if ref:
        o = o._replace(path=f"{o.path}@{ref.lstrip('@')}")
    return o
