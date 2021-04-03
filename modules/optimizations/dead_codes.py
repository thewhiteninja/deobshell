# coding=utf-8
from modules.logger import log_debug
from modules.utils import parent_map, replace_node, is_prefixed_var, get_used_vars


def opt_unused_variable(ast):
    parents = parent_map(ast)
    used_vars = get_used_vars(ast)

    for node in ast.iter():
        if node.tag in ["AssignmentStatementAst"]:
            subnodes = list(node)
            if subnodes[0].tag == "VariableExpressionAst":
                if subnodes[0].attrib["VariablePath"].lower() not in used_vars:
                    if not is_prefixed_var(subnodes[0].attrib["VariablePath"]):
                        log_debug("Remove assignement of unused variable %s" % (subnodes[0].attrib["VariablePath"]))

                        parents[node].remove(node)

                        return True
    return False


def opt_remove_uninitialised_variable_usage(ast):
    assigned = set()

    for node in ast.iter():
        if node.tag in ["AssignmentStatementAst"]:
            subnodes = list(node)
            if subnodes[0].tag == "VariableExpressionAst":
                assigned.add(subnodes[0].attrib["VariablePath"].lower())
        if node.tag in ["BinaryExpressionAst"]:
            subnodes = list(node)

            if subnodes[0].tag == "VariableExpressionAst":
                variable = subnodes[0]
                other = subnodes[1]
            elif subnodes[1].tag == "VariableExpressionAst":
                variable = subnodes[1]
                other = subnodes[0]
            else:
                variable, other = None, None

            if variable is not None and other is not None:
                if variable.attrib["VariablePath"].lower() not in assigned:
                    if not is_prefixed_var(variable.attrib["VariablePath"]):
                        log_debug("Remove unassigned variable use '%s'" % (variable.attrib["VariablePath"]))
                        replace_node(ast, node, other)

                        return True

    return False
