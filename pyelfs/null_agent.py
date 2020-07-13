import json
import os
import sys
from argparse import ArgumentParser
from logging import getLogger

from . import CustomTransferAgent
from .util import stage_logger

logger = getLogger(__name__)


class NullAgent(CustomTransferAgent):

    def __init__(self, lfs_storage):
        self.lfs_storage = lfs_storage
        logger.info("NullAgent is initialized")

    @stage_logger("Init Stage")
    def init(self, event, operation, remote, concurrent, concurrenttransfers):
        yield "{}"

    @stage_logger("Upload Stage")
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

    @stage_logger("Download Stage")
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
    agent = NullAgent(a.lfs_storage)
    agent.main_proc(sys.stdin)
