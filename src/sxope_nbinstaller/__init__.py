import io
import sys
import os
import getpass

from pathlib import Path
from unittest import mock


def task(msg):
    def _fn0(fn):
        def _fn1(*args, **kwargs):
            print(f"{msg.format(**kwargs)} .. ", end="")
            try:
                result = fn(*args, **kwargs)
                print("✅")
                return result
            except:
                print("❌")
                raise
        return _fn1
    return _fn0


# @task("authorizing colab")
# def auth():
#   from google.colab import auth
#   auth.authenticate_user()  # to un-mount: drive.flush_and_unmount()
#   
#   #from google.cloud import bigquery
#   #client = bigquery.Client(project="pp-import-staging")
# 
# 
# @task("mounting gdrive under {mountpoint}")
# def mount(mountpoint):
#   from google.colab import drive
#   with mock.patch('sys.stdout', new_callable=io.StringIO) as mck:
#     drive.mount(mountpoint, force_remount=True, readonly=True)
#   return Path(mountpoint)
# 
# 
# @task("setup bigq")
# def setup(bigqdir):
#   sys.path.insert(0, str(bigqdir / "src"))
#   from bigq.nb.utils import check_notebook
# 
# 
# def run(bigqdir, mountpoint=Path("/content/GDrive")):
#   auth()
#   mount(mountpoint)
#   setup(mountpoint / "MyDrive/Projects/sxope-bigq")
#   from bigq.nb.utils import check_notebook
#   return check_notebook()


def install(mode="prod"):
    assert mode in { "prod", "dev" }
    getpass.getpass("Give me a token! ")


