import json
import os
import sys
import tempfile
from argparse import ArgumentParser
from getpass import getuser
from logging import getLogger
from os.path import expanduser
from time import sleep
from random import random

from . import CustomTransferAgent
from .sftp_auth import SftpAuth
from .util import ERROR_CODE, handle_error

logger = getLogger(__name__)


class SftpAgent(CustomTransferAgent):

    def __init__(self, user, hostname, port, rsa_key, remote_dir, temp_dir):
        self.user = user
        self.hostname = hostname
        self.port = port
        self.rsa_key = rsa_key
        self.remote_dir = remote_dir
        self.temp_dir = temp_dir
        logger.info("Wait a little to avoid pipe broken")
        sleep(random())
        logger.info("SftpAgent is initialized")

    def init(self, event, operation, remote, concurrent, concurrenttransfers):
        logger.info("Enter Start stage")
        yield "{}"
        logger.info("Exit Start stage")

    def upload(self, event, oid, size, path, action):
        logger.info("Enter Upload stage")
        with SftpAuth(self.user, self.hostname, self.port, self.rsa_key, self.remote_dir) as sftp:
            progress = self.Progress(oid)
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
        logger.info("Exit Upload stage")

    def download(self, event, oid, size, action):
        logger.info("Enter Download stage")
        with SftpAuth(self.user, self.hostname, self.port, self.rsa_key, self.remote_dir) as sftp:
            progress = self.Progress(oid)
            temp_path = os.path.join(self.temp_dir, oid)
            logger.info(f"temp path is {temp_path}")
            try:
                sftp.chdir(oid[0:2])
                sftp.chdir(oid[2:4])
                sftp.get(oid, temp_path, callback=progress.progress_callback)
                yield json.dumps({
                    "event": "complete",
                    "oid": oid,
                    "path": temp_path
                })
            except Exception as e:
                handle_error(e, ERROR_CODE.DOWNLOAD)
        logger.info("Exit Download stage")

    def terminate(self):
        logger.info("Enter Terminate stage")
        logger.info("Exit Terminate stage")
        yield '{"event": "terminate"}'

    class Progress:
        byte_so_far = 0
        oid = None
        i = 0.0

        def __init__(self, oid):
            logger.info("Progress is initialized")
            self.oid = oid

        def progress_callback(self, byte_so_far, size):
            if byte_so_far / size < self.i:
                return
            self.i += 0.1
            bytes_since_last = byte_so_far - self.byte_so_far
            self.byte_so_far = byte_so_far
            res = json.dumps({
                "event": "progress",
                "oid": self.oid,
                "byteSoFar": byte_so_far,
                "bytesSinceLast": bytes_since_last,
            })
            logger.debug(res)
            print(res, flush=True)  # Tried, but couldn't return by yield in a callback.


def main_proc(user=None, hostname=None, port=None, rsa_key=None, remote_dir=None, temp_dir = None):
    logger.info("Enter main process")
    logger.info("Wait for std input")
    for line in sys.stdin:
        sftp_agent = SftpAgent(user, hostname, port, rsa_key, remote_dir, temp_dir)
        generator_dispatcher = {
            "init": lambda k: sftp_agent.init(**k),
            "upload": lambda k: sftp_agent.upload(**k),
            "download": lambda k: sftp_agent.download(**k),
            "terminate": lambda _: sftp_agent.terminate(),
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
    p.add_argument("--user",
                   default=getuser(),
                   help="username for sftp server.")
    p.add_argument("--hostname",
                   default="localhost",
                   help="hostname or ip address of sftp server.")
    p.add_argument("--port",
                   default=22,
                   help="port of sftp server.")
    p.add_argument("--rsa-key",
                   default=expanduser("~") + "/.ssh/id_rsa",
                   help="rsa key path.")
    p.add_argument("--remote-dir",
                   default="~/.lfs-miscellaneous",
                   help="absolute path of lfs objects directory. "
                        "In Windows OS, "
                        "in order to avoid unintentional path expansion by git-lfs "
                        "Please add 'pyelfs://'. e.g. pyelfs:///home/user/lfs-objects")
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
    main_proc(user=a.user,
              hostname=a.hostname,
              port=a.port,
              rsa_key=a.rsa_key,
              remote_dir=a.remote_dir,
              temp_dir = a.temp_dir)
