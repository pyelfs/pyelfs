from unittest import TestCase, mock
from argparse import ArgumentParser
from pyelfs.cli import Cli, SubCommands
import sys


class TestCli(TestCase):

    @mock.patch.object(sys, "platform")
    @mock.patch.object(sys, "stdin")
    def test_main_proc(self, stdin, platform):
        cli = Cli(**{"agent": None, "help": mock.MagicMock()})
        cli.main_proc(stdin)
        stdin.assert_not_called()

        cli = Cli(**{"agent": "test"})
        cli.main_proc(stdin)
        platform.startswith.assert_called_with("win")
        stdin.assert_not_called()

    def test_add_argument(self):
        p = ArgumentParser()
        Cli.add_argument(p)

        for subcommand in SubCommands:
            if subcommand.name == "init":
                continue
            a = p.parse_args([subcommand.name])
            self.assertEqual(subcommand.name, a.agent)
