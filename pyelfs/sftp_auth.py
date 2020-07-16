from logging import getLogger
from paramiko import SFTPClient, Transport, RSAKey
from .util import handle_error, ERROR_CODE

logger = getLogger(__name__)


class SftpAuth:

    def __init__(self, user, hostname, port, rsa_key, remote_dir):
        self.user = user
        self.hostname = hostname
        self.port = port
        self.rsa_key = rsa_key
        self.remote_dir = remote_dir
        logger.info(self.__repr__())

    def __repr__(self):
        return "The sftp instance was initialized. " \
               "user={}, hostname={}, port={}, rsa_key={}, remote_dir={}"\
            .format(self.user, self.hostname, self.port, self.rsa_key, self.remote_dir)

    def set_transport(self):
        logger.debug("Try to initialize transport.")
        try:
            self.transport = Transport(f"{self.hostname}:{self.port}")
            self.transport.start_client(event=None, timeout=15)
            self.transport.get_remote_server_key()
            rsa_key = RSAKey.from_private_key_file(self.rsa_key)
            self.transport.auth_publickey(self.user, rsa_key)
        except Exception as e:
            handle_error(e, ERROR_CODE.SFTP_AUTH)
            raise

        logger.info("Transport was initialized.")

    def __enter__(self):
        self.set_transport()
        self.sftp = SFTPClient.from_transport(self.transport)
        try:
            logger.info("Try to make a directory")
            self.sftp.mkdir(self.remote_dir)
        except Exception as e:
            logger.info(e)
        logger.info(f"Change the current directory into {self.remote_dir}")
        self.sftp.chdir(self.remote_dir)
        return self.sftp

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.transport.close()
        self.sftp.close()
