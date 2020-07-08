from unittest import TestCase
from unittest.mock import patch

from pyelfs import sftp_auth


class TestSftpAuth(TestCase):

    @patch.object(sftp_auth.RSAKey, "from_private_key_file", autospec=True)
    @patch.object(sftp_auth, "Transport", autospec=True)
    def test_set_transport(self, transport, rsa_key):
        inst = transport.return_value
        auth = sftp_auth.SftpAuth("elf", "localhost", 22, "~/.ssh/rsa_id", "/home/elf/.lfs-objects")
        auth.set_transport()
        inst.start_client.assert_called_with(event=None, timeout=15)

        transport.assert_called_once_with("localhost:22")
        transport.auth_publickey("elf", rsa_key.return_value)
        rsa_key.assert_called_once_with("~/.ssh/rsa_id")
