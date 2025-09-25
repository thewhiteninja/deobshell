# coding=utf-8
from modules.logger import log_info
from modules.utils import del_tree


def opt_remove_empty_nodes(ast, parents):
    kill_list = []
    for node in ast.iter():
        if node.tag in ("CommandExpressionAst"):
            if len(node) == 0:
                kill_list.append(node)

    for node in kill_list:
        parents[node].remove(node)
        del_tree(parents, node, ())

    if kill_list:
        log_info(f"Deleted {len(kill_list)} empty nodes")

    return False
