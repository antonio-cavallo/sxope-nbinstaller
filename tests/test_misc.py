from unittest import mock
from sxope_nbinstaller import misc
import subprocess


def test_fake_run():
    with mock.patch("subprocess.check_output") as mck:
        subprocess.check_output(["hello", "world"], encoding="utf-8")
        assert len(mck.mock_calls) == 1
        assert mck.mock_calls[0].args == (["hello", "world",],)


def test_git_clone():
    url = "https://github.com/antonio-cavallo/sxope-bigq.git"
    with mock.patch("subprocess.check_output") as mck:
        misc.git_clone("abc", url)
        misc.git_clone("abc", url, token="123")
        
        calls = [ c for c in mck.mock_calls if c.args ]
        assert len(calls) == 2
    
        assert calls[0].args[0][2] == url
        assert calls[1].args[0][2] == "https://123@github.com/antonio-cavallo/sxope-bigq.git"
