from unittest import mock
import subprocess

import pytest

from sxope_nbinstaller import misc


def test_fake_run():
    with mock.patch("subprocess.check_output") as mck:
        subprocess.check_output(["hello", "world"], encoding="utf-8")
        assert len(mck.mock_calls) == 1
        assert mck.mock_calls[0].args == (
            [
                "hello",
                "world",
            ],
        )


def test_task(capsys):
    @misc.task("hello world")
    def hello(x):
        if x == 1:
            return
        elif x == 3:
            print("xxx")
            raise RuntimeError("BOOO")
        print(f"HELLO {x}")

    hello(1)
    assert capsys.readouterr().out.strip() == "👉 hello world .. ✅"

    hello(misc.RunMode.DRYRUN, 1)
    assert (
        capsys.readouterr().out.strip()
        == """
👉 hello world .. ✅
   | (dry-run) hello(**{'x': 1})
""".strip()
    )

    hello(misc.RunMode.NOABORT, 3)
    assert (
        capsys.readouterr().out.strip()[:27]
        == """
👉 hello world .. ❌
   | xxx
""".strip()
    )

    pytest.raises(RuntimeError, hello, 3)
    capsys.readouterr()
