import json
import os
import sys
from argparse import ArgumentParser
from logging import getLogger

from . import CustomTransferAgent

logger = getLogger(__name__)


class NullAgent(CustomTransferAgent):

    def __init__(self, lfs_storage):
        self.lfs_storage = lfs_storage
        logger.info("NullAgent is initialized")

    def init(self, event, operation, remote, concurrent, concurrenttransfers):
        yield "{}"

    def upload(self, event, oid, size, path, action):
        yield json.dumps({
            "event": "progress",
            "oid": oid,
            "byteSoFar": 0,
            "bytesSinceLast": 0,
        })
        yield json.dumps({
            "event": "complete",
            "oid": oid,
        })

    def download(self, event, oid, size, action):
        yield json.dumps({
            "event": "progress",
            "oid": oid,
            "byteSoFar": 0,
            "bytesSinceLast": 0,
        })
        self.lfs_storage = "/".join(self.lfs_storage, oid[0:2], oid[2:4], oid)
        yield json.dumps({
            "event": "complete",
            "oid": oid,
            "path": os.path.sep.join(self.lfs_storage.split("/"))
        })
        logger.info("Exit Download stage")

    def terminate(self):
        yield '{"event": "terminate"}'


def main_proc(lfs_storage):
    logger.info("Enter main process")
    logger.info("Wait for std input")
    for line in sys.stdin:
        null_agent = NullAgent(lfs_storage)
        generator_dispatcher = {
            "init": lambda k: null_agent.init(**k),
            "upload": lambda k: null_agent.upload(**k),
            "download": lambda k: null_agent.download(**k),
            "terminate": lambda _: null_agent.terminate(),
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
    p.add_argument("--lfs-storage", help="lfs storage")
    p.add_argument("--debug-log", help="debug log file.")
    return p.parse_args()


def main():
    import logging
    a = parse_args()
    if a.debug_log:
        logging.basicConfig(level=logging.DEBUG, filename=a.debug_log)
    logger.info(f"Arguments were parsed. : {str(a)}")
    main_proc(a.lfs_storage)
