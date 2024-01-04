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
    print("      parse           : Parse PowerShell script to XML AST")
    print("      deob            : Deobfuscate PowerShell script")
    print("      format          : Format PowerShell script")
    print()
    print("Options:")
    print("      -h, --help      : Show help")
    print("      -i, --in        : Input file: .ps1 or .xml with AST")
    if sys.platform == "linux" or sys.platform == "darwin":
        print("      --docker        : Run PowerShell under Docker")
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
        elif sys.argv[i] == "--docker":
            OPTIONS["docker"] = True
        else:
            OPTIONS["command"] = sys.argv[i]
        i += 1


def parse(input_file):
    p = pathlib.Path(input_file)

    if p.suffix == ".ps1":
        if create_ast_file(p, "docker" in OPTIONS):
            ast_file = p.with_suffix(".xml")
            return read_ast_file(ast_file)
    elif p.suffix == ".xml":
        return read_ast_file(p)


def deob(input_file):
    if ast := parse(input_file):
        o = Optimizer()
        o.optimize(ast)

        p = pathlib.Path(input_file)
        with open(p.with_suffix(".deob.xml"), "wb") as output:
            ast.write(output)

        output = p.with_suffix(".deob.ps1")
        r = Rebuilder(output)
        r.rebuild(ast.getroot())
        return output


def format(input_file):
    if ast := parse(input_file):
        p = pathlib.Path(input_file)
        output = p.with_suffix(".formatted.ps1")
        r = Rebuilder(output)
        r.rebuild(ast.getroot())
        return output


def main():
    cmd = OPTIONS.setdefault("command", None)
    input_file = pathlib.Path(OPTIONS['input'])

    if cmd == "parse":
        parse(input_file)
    elif cmd == "deob":
        deob(input_file)
    elif cmd == "format":
        format(input_file)
    else:
        usage()


if __name__ == '__main__':
    welcome()
    set_log_level(LogLevel.DEBUG, 500)
    parse_args()
    main()
