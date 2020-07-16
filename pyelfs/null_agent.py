import json
import os
from logging import getLogger

from . import CustomTransferAgent
from .util import stage_logger
from git.repo import Repo
from git.repo.base import InvalidGitRepositoryError
logger = getLogger(__name__)


class NullAgent(CustomTransferAgent):

    def __init__(self, lfs_storage, **kwargs):
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

    @classmethod
    def add_argument(cls, parser):
        default_lfs = "~/.lfs-miscellaneous"
        try:
            repo = Repo()
            default_lfs = os.path.join(repo.working_dir, ".git/lfs")
        except InvalidGitRepositoryError:
            pass
        parser.add_argument(
            "--lfs-storage",
            default=default_lfs,
            help="lfs storage"
        )
        parser.add_argument("--verbose", help="verbose log")

    @classmethod
    def rep(cls):
        return "null agent"
