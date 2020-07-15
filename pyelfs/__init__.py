__version__ = '0.1.1'

import json
from abc import ABC, abstractmethod
from logging import getLogger

from .util import stage_logger

logger = getLogger(__name__)


class CustomTransferAgent(ABC):

    @abstractmethod
    def init(self, event, operation, remote, concurrent, concurrenttransfers):
        raise NotImplementedError

    @abstractmethod
    def upload(self, event, oid, size, path, action):
        raise NotImplementedError

    @abstractmethod
    def download(self, event, oid, size, action):
        raise NotImplementedError

    @staticmethod
    @stage_logger("Terminate Stage")
    def terminate():
        yield '{"event": "terminate"}'

    @property
    def dispatcher(self):
        return {
            "init": lambda k: self.init(**k),
            "upload": lambda k: self.upload(**k),
            "download": lambda k: self.download(**k),
        }

    def main_proc(self, stream):
        for line in stream:
            logger.debug(line)
            try:
                data = json.loads(line)
            except Exception as e:
                logger.debug(e)
                continue
            for res in self.dispatcher[data["event"]](data):
                logger.debug(res)
                print(res, flush=True)
        res = next(self.terminate())
        logger.debug(res)
        print(res, flush=True)
