# coding=utf-8
from modules.logger import log_debug
from modules.utils import delete_node


def opt_remove_empty_nodes(ast):
    for node in ast.iter():
        if node.tag in ["Attributes", "Redirections", "CatchTypes"]:
            subnodes = list(node)
            if len(subnodes) == 0:

                log_debug(f"Remove empty node {node.tag}")

                delete_node(ast, node)

                return True

    return False
