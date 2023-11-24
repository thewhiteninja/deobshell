# coding=utf-8
from modules.logger import log_info
from modules.utils import parent_map


def opt_remove_empty_nodes(ast):
    parents = parent_map(ast)
    kill_list = []
    for node in ast.iter():
        if node.tag in ("Attributes", "Redirections", "CatchTypes", \
                        "Operator", "TokenKind", "BlockKind", "InvocationOperator", \
                        "Flags", "Clauses"):
            if len(node) == 0:
                kill_list.append(node)

    for node in kill_list:
        parents[node].remove(node)

    if kill_list:
        log_info(f"Deleted {len(kill_list)} empty nodes")

    return False
