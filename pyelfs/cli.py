import logging
import sys
from argparse import ArgumentParser
from enum import Enum

from .file_agent import FileAgent
from .null_agent import NullAgent
from .sftp_agent import SftpAgent
from .util import exclude, include, include_pyelfs_wrapped

logger = logging.getLogger(__name__)


class Cli:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.options = {
            "subcommand": exclude(),
            "agent": exclude(),
            "func": exclude(),
            "help": exclude(),

            "verbose": include("--verbose"),
            "temp": include_pyelfs_wrapped("--temp"),

            "lfs_storage": include_pyelfs_wrapped("--lfs-storage"),
            "lfs_storage_local": include_pyelfs_wrapped("--lfs-storage-local"),
            "lfs_storage_remote": include_pyelfs_wrapped("--lfs-storage-remote"),

            "user": include("--user"),
            "hostname": include("--hostname"),
            "port": include("--port"),
            "rsa_key": include_pyelfs_wrapped("--rsa-key"),
        }

    def main_proc(self, stream):
        if self.kwargs["agent"]:
            pyelfs_args = [self.options[k](self.kwargs[k]) for k in self.kwargs]
            pyelfs_args = " ".join(sum(pyelfs_args, []))
            pyelfs_path = "pyelfs.py"
            if sys.platform.startswith('win'):
                pyelfs_path = "pyelfs.exe"

            res = f"### PyElfs\n" \
                  f"### Please execute the following commands in your git repository.\n" \
                  f"### pyelfs init {self.kwargs['agent']} -h shows more info.\n" \
                  f"\n" \
                  f"git config --add lfs.standalonetransferagent pyelfs\n" \
                  f"git config --add lfs.customtransfer.pyelfs.path {pyelfs_path}\n" \
                  f"git config --add lfs.customtransfer.pyelfs.args " \
                  f"'{self.kwargs['agent']} {pyelfs_args}'\n"
            print(res)
        else:
            self.kwargs["help"]()

    @classmethod
    def add_argument(cls, parser):
        parser_sub = parser.add_subparsers(dest="agent")
        for command in SubCommands:
            if command.name == "init":
                continue
            command.value.add_argument(parser_sub.add_parser(command.name))

    @classmethod
    def rep(cls):
        return "initialize for pyelfs in git directory."


class SubCommands(Enum):
    init = Cli
    file = FileAgent
    sftp = SftpAgent
    null = NullAgent


def main():
    p = ArgumentParser("pyelfs")

    p_subcommands = p.add_subparsers(dest="subcommand")
    for subcommand in SubCommands:
        p_subcommand = p_subcommands.add_parser(subcommand.name, help=subcommand.value.rep())
        subcommand.value.add_argument(p_subcommand)
        p_subcommand.set_defaults(func=subcommand.value, help=p_subcommand.print_help)

    a = p.parse_args()
    if not a.subcommand:
        p.print_help()
        return
    try:
        logging.basicConfig(level=logging.DEBUG, filename=a.verbose)
    except AttributeError:
        pass
    logger.info(f"Arguments: {a}")
    k = dict((k, a.__dict__[k]) for k in a.__dict__)
    logger.info(f"Modified arguments: {k}")
    agent = a.func(**k)
    agent.main_proc(sys.stdin)
