import os
import sys
import shutil
import json
import tempfile
from argparse import ArgumentParser
from logging import getLogger
from random import random
from time import sleep

from . import CustomTransferAgent
from .util import ERROR_CODE, handle_error

logger = getLogger(__name__)


class FileAgent(CustomTransferAgent):

    def __init__(self, lfs_dir, temp_dir):
        self.lfs_dir = lfs_dir
        self.temp_dir = temp_dir
        logger.info("Wait a little to avoid pipe broken")
        sleep(random())
        logger.info("FileAgent is initialized")

    def init(self, event, operation, remote, concurrent, concurrenttransfers):
        logger.info("Enter Start stage")
        yield "{}"
        logger.info("Exit Start stage")

    def upload(self, event, oid, size, path, action):
        logger.info("Enter Upload stage")
        yield json.dumps({
            "event": "progress",
            "oid": oid,
            "byteSoFar": 0,
            "bytesSinceLast": 0,
        })
        try:
            first = os.path.join(self.lfs_dir, oid[0:2])
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
        logger.info("Exit Upload stage")

    def download(self, event, oid, size, action):
        logger.info("Enter Download stage")

        temp_path = os.path.join(self.temp_dir, oid)
        logger.info(f"temp path is {temp_path}")
        yield json.dumps({
            "event": "progress",
            "oid": oid,
            "byteSoFar": 0,
            "bytesSinceLast": 0,
        })
        try:
            path = os.path.join(self.lfs_dir, oid[0:2], oid[2:4], oid)
            shutil.copyfile(path, temp_path)
            yield json.dumps({
                "event": "complete",
                "oid": oid,
                "path": temp_path
            })
            self.terminate()
        except Exception as e:
            handle_error(e, ERROR_CODE.DOWNLOAD)
        logger.info("Exit Download stage")

    def terminate(self):
        logger.info("Enter Terminate stage")
        logger.info("Exit Terminate stage")
        yield '{"event": "terminate"}'


def main_proc(lfs_dir, temp_dir):
    logger.info("Enter main process")
    logger.info("Wait for std input")
    for line in sys.stdin:
        file_agent = FileAgent(lfs_dir, temp_dir)
        generator_dispatcher = {
            "init": lambda k: file_agent.init(**k),
            "upload": lambda k: file_agent.upload(**k),
            "download": lambda k: file_agent.download(**k),
            "terminate": lambda _: file_agent.terminate(),
        }
        logger.debug(line)
        try:
            data = json.loads(line)
        except Exception as e:
            logger.debug(e)
            continue
        for res in generator_dispatcher[data["event"]](data):
            logger.debug(res)
            print(res, flush=True)
    logger.info("EOF")
    res = next(generator_dispatcher["terminate"](None))
    logger.debug(res)
    print(res, flush=True)


def parse_args():
    p = ArgumentParser()
    p.add_argument("--lfs-dir",
                   default="~/.lfs-miscellaneous",
                   help="path of lfs objects directory.")
    p.add_argument("--temp-dir",
                   help="path of temporary directory to download lfs objects.")
    p.add_argument("--debug-log",
                   help="debug log file.")
    return p.parse_args()


def main():
    import logging
    a = parse_args()
    if a.debug_log:
        logging.basicConfig(level=logging.DEBUG, filename=a.debug_log)
    logger.info(f"Arguments were parsed. : {str(a)}")
    try:
        if a.temp_dir:
            a.temp_dir = os.path.sep.join(str(a.temp_dir).split("/"))
        else:
            a.temp_dir = tempfile.gettempdir()

        if a.remote_dir.startswith("pyelfs://"):
            a.remote_dir = str(a.remote_dir).replace("pyelfs://", "")
    except Exception as e:
        logger.info(e)
        raise
    logger.info(f"Modifid arguments. : {str(a)}")
    main_proc(a.lfs_dir, a.tempdir)

