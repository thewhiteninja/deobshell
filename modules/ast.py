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


def create_ast_file(ps1_file, use_docker):
    global _g_use_docker  # Hack for optimizations that need to parse a sub-AST
    if use_docker is None:
        use_docker = _g_use_docker
    else:
        _g_use_docker = use_docker

    log_info(f"Creating AST for: {ps1_file}")

    if use_docker:
        cmd = ["docker", "run", "-v", os.path.abspath(os.path.join("tools", "Get-AST.ps1")) + ":/Get-AST.ps1",
            "-v", os.path.abspath(ps1_file / "..") + ":/scriptdir",
            "--net", "none", "--rm", "-it", "mcr.microsoft.com/powershell:lts-7.2-ubuntu-22.04",
            "pwsh", "-File", "/Get-AST.ps1", "-ps1", "/scriptdir/" + ps1_file.name]
    else:
        cmd = ["PowerShell", "-ExecutionPolicy", "Unrestricted", "-File",
            os.path.abspath(os.path.join("tools", "Get-AST.ps1")),
            "-ps1", os.path.abspath(ps1_file)]

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    for line in result.stdout.splitlines():
        log_debug(line)
    for line in result.stderr.splitlines():
        log_debug(line)

    return result.returncode == 0
