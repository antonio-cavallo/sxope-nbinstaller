import io
import enum
import traceback
from unittest import mock
import functools


OK = "✅"
E = "❌"
W = "🟡"
RH = "👉"


class RunMode(enum.Flag):
    DRYRUN = enum.auto()
    ABORT = enum.auto()
    NOABORT = enum.auto()


RUNMODE = RunMode.ABORT


def set_runmode(mode):
    global RUNMODE
    if mode is None:
        RUNMODE = RunMode.ABORT
    else:
        RUNMODE = mode


def indent(txt: str, pre=" " * 2) -> str:
    from textwrap import dedent

    while txt and txt.startswith("\n"):
        txt = txt[1:]
    while txt and txt.endswith("\n"):
        txt = txt[:-1]

    txt = dedent(txt)
    return "\n".join(f"{pre}{line}" for line in txt.split("\n"))


def printx(msg, multiline=False, tag=OK, offset=" " * 2):
    if multiline:
        head, _, body = msg.partition("\n")
        print(f"{tag} {head}")
        print(indent(body, " " * len(tag) + offset))
    else:
        print(f"{tag} {msg}")


printok = functools.partial(printx, tag=OK)
printerr = functools.partial(printx, tag=E)
printwarn = functools.partial(printx, tag=W)
printtask = functools.partial(printx, tag=RH)


def task(msg, anyway=None):
    def _fn0(fn):
        def _fn1(*args, **kwargs):
            from inspect import getcallargs

            runmode = RUNMODE
            if args and isinstance(args[0], RunMode):
                runmode, args = args[0], args[1:]

            kwargs = getcallargs(fn, *args, **kwargs)
            print(f"{RH} {msg.format(**kwargs)} .. ", end="")
            lead = "   | "
            if (runmode & RunMode.DRYRUN) and not anyway:
                print(OK)
                print(indent(f"(dry-run) {fn.__name__}(**{kwargs})", lead))
                return

            try:
                with mock.patch("sys.stdout", new_callable=io.StringIO) as mck:
                    result = fn(**kwargs)
                print(OK)
                if (out := mck.getvalue()).strip():
                    print(indent(out, lead))
                return result
            except:  # noqa: E722
                print(E)
                out = mck.getvalue()
                out += traceback.format_exc()
                if out.strip():
                    print(indent(out, lead))
                if runmode and runmode & RunMode.ABORT:
                    raise

        _fn1.fn = fn
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
