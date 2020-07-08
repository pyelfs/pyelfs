__version__ = '0.0.1'

from abc import ABCMeta, abstractmethod


class CustomTransferAgent(metaclass=ABCMeta):

    @abstractmethod
    def init(self, event, operation, remote, concurrent, concurrenttransfers):
        pass

    @abstractmethod
    def upload(self, event, oid, size, path, action):
        pass

    @abstractmethod
    def download(self, event, oid, size, action):
        pass

    @abstractmethod
    def terminate(self):
        pass
