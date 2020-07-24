import json
import os
from getpass import getuser
from logging import getLogger
from os.path import expanduser
from random import random
from time import sleep
from tempfile import gettempdir

from . import CustomTransferAgent
from .sftp_auth import SftpAuth
from .util import ERROR_CODE, handle_error, Progress, stage_logger

logger = getLogger(__name__)


class SftpAgent(CustomTransferAgent):

    def __init__(self, user, hostname, port, rsa_key, lfs_storage_remote, temp, **kwargs):
        self.user = user
        self.hostname = hostname
        self.port = port
        self.rsa_key = rsa_key
        self.lfs_storage_remote = lfs_storage_remote
        self.temp = temp
        logger.info("Wait a little to avoid pipe broken")
        sleep(random())
        logger.info("SftpAgent is initialized")

    @stage_logger("Init Stage")
    def init(self, event, operation, remote, concurrent, concurrenttransfers):
        yield "{}"

    @stage_logger("Upload Stage")
    def upload(self, event, oid, size, path, action):
        with SftpAuth(self.user, self.hostname, self.port,
                      self.rsa_key, self.lfs_storage_remote) as sftp:
            progress = Progress(oid)
            try:
                sftp.chdir(oid[0:2])
            except IOError:
                sftp.mkdir(oid[0:2])
                sftp.chdir(oid[0:2])
            except Exception as e:
                handle_error(e, ERROR_CODE.UPLOAD)
            try:
                sftp.chdir(oid[2:4])
            except IOError as e:
                sftp.mkdir(oid[2:4])
                sftp.chdir(oid[2:4])
            except Exception as e:
                handle_error(e, ERROR_CODE.UPLOAD)

            same_file_exists = False
            try:
                logger.info("Check existence of the same file.")
                target_size = sftp.stat(oid).st_size
                if size == target_size:
                    same_file_exists = True
                    logger.info("A same file exists. Skip upload.")
                    res = json.dumps({
                        "event": "progress",
                        "oid": oid,
                        "byteSoFar": size,
                        "bytesSinceLast": 0
                    })
                    logger.debug(res)
                    print(res, flush=True)
                else:
                    logger.info("A same file doesn't exist (size). Start upload.")
            except:
                logger.info("A same file doesn't exist (name). Start upload.")
            try:
                if not same_file_exists:
                    sftp.put(path, oid, callback=progress.progress_callback)
            except Exception as e:
                handle_error(e, ERROR_CODE.UPLOAD)
        yield json.dumps({
            "event": "complete",
            "oid": oid,
        })

    @stage_logger("Download Stage")
    def download(self, event, oid, size, action):
        with SftpAuth(self.user, self.hostname, self.port,
                      self.rsa_key, self.lfs_storage_remote) as sftp:
            progress = Progress(oid)
            temp_path = os.path.join(self.temp, oid)
            logger.info(f"temp path is {temp_path}")
            try:
                sftp.chdir(oid[0:2])
                sftp.chdir(oid[2:4])
                with open(temp_path, "bw") as f:
                    sftp.getfo(oid, f, callback=progress.progress_callback)
                yield json.dumps({
                    "event": "complete",
                    "oid": oid,
                    "path": temp_path
                })
            except Exception as e:
                handle_error(e, ERROR_CODE.DOWNLOAD)

    @classmethod
    def add_argument(cls, parser):
        parser.add_argument("--user",
                            default=getuser(),
                            help="username for sftp server.")
        parser.add_argument("--hostname",
                            default="localhost",
                            help="hostname or ip address of sftp server.")
        parser.add_argument("--port",
                            default=22,
                            help="port of sftp server.")
        parser.add_argument("--rsa-key",
                            default=expanduser("~") + "/.ssh/id_rsa",
                            help="rsa key.")
        parser.add_argument("--lfs-storage-remote",
                            default=f"/home/{getuser()}/lfs-objects",
                            help="remote directory for lfs object."
                                 "please add 'pyelfs://' in .git/config, "
                                 "in order to avoid unintentional path expansion by git-lfs. ")
        parser.add_argument("--verbose", help="verbose log")
        parser.add_argument("--temp",
                            default=f"{gettempdir()}",
                            help="temporary directory to download lfs objects.")

    @classmethod
    def rep(cls):
        return "sftp agent"
