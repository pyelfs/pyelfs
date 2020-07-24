import json
import os
import shutil
from logging import getLogger
from random import random
from time import sleep
from tempfile import gettempdir

from . import CustomTransferAgent
from .util import ERROR_CODE, handle_error, stage_logger

logger = getLogger(__name__)


class FileAgent(CustomTransferAgent):

    def __init__(self, lfs_storage_local, temp, **kwargs):
        self.lfs_storage_local = lfs_storage_local
        self.temp_dir = temp
        logger.info("Wait a little to avoid pipe broken")
        sleep(random())
        logger.info("FileAgent is initialized")

    @stage_logger("Init Stage")
    def init(self, event, operation, remote, concurrent, concurrenttransfers, **kwargs):
        yield "{}"

    @stage_logger("Upload Stage")
    def upload(self, event, oid, size, path, action):
        yield json.dumps({
            "event": "progress",
            "oid": oid,
            "byteSoFar": 0,
            "bytesSinceLast": 0,
        })
        try:
            first = os.path.join(self.lfs_storage_local, oid[0:2])
            if not os.path.isdir(first):
                os.mkdir(first)
            second = os.path.join(first, oid[2:4])
            if not os.path.isdir(second):
                os.mkdir(second)
            shutil.copyfile(path, os.path.join(second, oid))
        except shutil.SameFileError:
            pass
        except Exception as e:
            handle_error(e, ERROR_CODE.UPLOAD)
        yield json.dumps({
            "event": "complete",
            "oid": oid,
        })

    @stage_logger("Download Stage")
    def download(self, event, oid, size, action):
        temp_path = os.path.join(self.temp_dir, oid)
        logger.info(f"temp path is {temp_path}")
        yield json.dumps({
            "event": "progress",
            "oid": oid,
            "byteSoFar": 0,
            "bytesSinceLast": 0,
        })
        try:
            path = os.path.join(self.lfs_storage_local, oid[0:2], oid[2:4], oid)
            shutil.copyfile(path, temp_path)
            yield json.dumps({
                "event": "complete",
                "oid": oid,
                "path": temp_path
            })
            self.terminate()
        except Exception as e:
            handle_error(e, ERROR_CODE.DOWNLOAD)

    @classmethod
    def add_argument(cls, parser):
        parser.add_argument("--lfs-storage-local",
                            default="~/.lfs-miscellaneous",
                            help="path of lfs objects directory.")
        parser.add_argument("--verbose", help="verbose log")
        parser.add_argument("--temp",
                            default=f"{gettempdir()}",
                            help="temporary directory to download lfs objects.")

    @classmethod
    def rep(cls):
        return "file agent"
