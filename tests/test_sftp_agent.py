import json
from getpass import getuser
from os.path import expanduser
from unittest import TestCase
from unittest.mock import patch

from pyelfs import sftp_agent


class TestSftpAgent(TestCase):
    agent = sftp_agent.SftpAgent("elf", "localhost", 22, "~/.ssh/id_rsa", "/home/elf/.lfs-objects")

    def test_init(self):
        stdin_init = '{ ' \
                     '"event": "init", ' \
                     '"operation": "download", ' \
                     '"remote": "origin", ' \
                     '"concurrent": true, ' \
                     '"concurrenttransfers": 8 ' \
                     '}'
        stdin_init = json.loads(stdin_init)
        for res in self.agent.init(**stdin_init):
            self.assertEqual("{}", res)

    @patch.object(sftp_agent, "SftpAuth")
    def test_upload(self, auth):
        stdin_upload = '{ ' \
                       '"event": "upload", ' \
                       '"oid": "bf3e3e2af9366a3b704ae0c31de5afa64193ebabffde2091936ad2e7510bc03a", ' \
                       '"size": 346232, ' \
                       '"path": "/path/to/file.png", ' \
                       '"action": { ' \
                       '"href": "nfs://server/path", ' \
                       '"header": { "key": "value" } ' \
                       '} ' \
                       '}'
        stdin_upload = json.loads(stdin_upload)
        generator = self.agent.upload(**stdin_upload)
        res = next(generator)
        self.assertEqual(res,
                         '{"event": "complete", "oid": "bf3e3e2af9366a3b704ae0c31de5afa64193ebabffde2091936ad2e7510bc03a"}')
        auth.assert_called_once_with("elf", "localhost", 22, "~/.ssh/id_rsa", "/home/elf/.lfs-objects")

    @patch.object(sftp_agent, "SftpAuth")
    def test_download(self, auth):
        stdin_download = '{ ' \
                         '"event": "download", ' \
                         '"oid": "22ab5f63670800cc7be06dbed816012b0dc411e774754c7579467d2536a9cf3e", ' \
                         '"size": 21245, ' \
                         '"action": { ' \
                         '"href": "nfs://server/path", ' \
                         '"header": { "key": "value" } ' \
                         '} ' \
                         '}'
        stdin_download = json.loads(stdin_download)
        generator = self.agent.download(**stdin_download)
        res = next(generator)
        self.assertEqual(res,
                         '{'
                         '"event": "complete", '
                         '"oid": "22ab5f63670800cc7be06dbed816012b0dc411e774754c7579467d2536a9cf3e", '
                         '"path": "/var/folders/nw/2kgc3k852755dtjv0mfm05z00000gn/T'
                         '/22ab5f63670800cc7be06dbed816012b0dc411e774754c7579467d2536a9cf3e"'
                         '}')
        res = next(generator)
        self.assertEqual(res, '{"event": "terminate"}')
        auth.assert_called_once_with("elf", "localhost", 22, "~/.ssh/id_rsa", "/home/elf/.lfs-objects")

    def test_terminate(self):
        for res in self.agent.terminate():
            self.assertEqual(res, '{"event": "terminate"}')


def test_parse_args(self):
    a = sftp_agent.parse_args()
    self.assertEqual(a.user, getuser())
    self.assertEqual(a.hostname, "localhost")
    self.assertEqual(a.port, 22)
    self.assertEqual(a.rsa_key, expanduser("~") + "/.ssh/rsa_id")
    self.assertEqual(a.remote_dir, "~/.lfs-miscellaneous")
    self.assertEqual(a.temp_dir, None)
    self.assertEqual(a.debug_log, None)
