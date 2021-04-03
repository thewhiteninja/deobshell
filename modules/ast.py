# coding=utf-8
import os
import subprocess
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET

from modules.logger import log_info, log_debug, log_err


def read_ast_file(filename):
    log_info(f"Reading input AST: {filename}")
    try:
        ast = ET.parse(filename)
        return ast
    except IOError as e:
        log_err(e.args[1])
        return None
    except Exception as e:
        log_err(str(e))
        return None


def create_ast_file(ps1_file):
    log_info(f"Creating AST for: {ps1_file}")

    cmd = ["PowerShell", "-ExecutionPolicy", "Unrestricted", "-File",
           os.path.abspath(os.path.join("tools", "Get-AST.ps1")),
           "-ps1", os.path.abspath(ps1_file)]

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    for line in result.stdout.splitlines():
        log_debug(line)

    return result.returncode == 0
