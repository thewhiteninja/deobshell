# coding=utf-8
import os
import pathlib
import sys

from modules.ast import create_ast_file, read_ast_file
from modules.logger import set_log_level, LogLevel
from modules.optimize import Optimizer
from modules.rebuilder import Rebuilder
from modules.utils import welcome

OPTIONS = {}


def usage():
    print("Usage: " + os.path.basename(sys.argv[0]) + ' [options]')
    print()
    print("Command:")
    print("      deob            : Deobfuscate PowerShell script")
    print("      format          : Format PowerShell script")
    print()
    print("Options:")
    print("      -h, --help      : Show help")
    print("      -i, --in        : Input .ps1 file")
    print()
    sys.exit(0)


def parse_args():
    global OPTIONS
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] in ["-h", "--help"]:
            usage()
        elif sys.argv[i] in ["-i", "--in"]:
            OPTIONS["input"] = sys.argv[i + 1]
            i += 1
        else:
            OPTIONS["command"] = sys.argv[i]
        i += 1


def deob(ps1_file):
    p = pathlib.Path(ps1_file)

    if create_ast_file(p):

        if ast := read_ast_file(p.with_suffix(".xml")):

            o = Optimizer()
            o.optimize(ast)

            with open(p.with_suffix(".deob.xml"), "wb") as output:
                ast.write(output)

            r = Rebuilder(p.with_suffix(".deob.ps1"))
            r.rebuild(ast.getroot())


def format(ps1_file):
    p = pathlib.Path(ps1_file)

    if create_ast_file(p):

        if ast := read_ast_file(p.with_suffix(".xml")):

            r = Rebuilder(p.with_suffix(".formatted.ps1"))
            r.rebuild(ast.getroot())


def main():
    cmd = OPTIONS.setdefault("command", None)
    if cmd == "deob":
        deob(OPTIONS['input'])
    elif cmd == "format":
        format(OPTIONS['input'])
    else:
        usage()


if __name__ == '__main__':
    welcome()
    set_log_level(LogLevel.DEBUG)
    parse_args()
    main()
