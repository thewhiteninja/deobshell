# coding=utf-8
from modules.logger import log_debug, log_err
from modules.utils import create_constant_number, parent_map, replace_node, \
    is_prefixed_var, get_used_vars, to_numeric


def opt_unused_variable(ast):
    parents = parent_map(ast)
    used_vars = get_used_vars(ast)
    kill_list = []

    for node in ast.iter():
        if node.tag in ["AssignmentStatementAst"]:
            subnodes = list(node)
            if subnodes[0].tag == "VariableExpressionAst":
                if subnodes[0].attrib["VariablePath"].lower() not in used_vars:
                    if not is_prefixed_var(subnodes[0].attrib["VariablePath"]):
                        log_debug("Remove assignment of unused variable %s" % (subnodes[0].attrib["VariablePath"]))

                        kill_list.append(node)

    for node in kill_list:
        parents[node].remove(node)

    return len(kill_list) != 0


def opt_remove_uninitialised_variable_usage(ast):
    assigned = set()
    kill_list = []
    replacements = []

    """
    FIXME This function causes invalid output for constructs like
    $i = 2;
    while ($i -gt 0) {
      $unassgn = $unassn + 4;
      $i--;
    }
    Write-Host $unassgn
    """

    for node in ast.iter():
        if node.tag in ["AssignmentStatementAst"]:
            subnodes = list(node)
            if subnodes[1].tag == "CommandExpressionAst" and subnodes[1][0].tag == "VariableExpressionAst":
                var_source = subnodes[1][0].attrib["VariablePath"].lower()
                if var_source not in assigned:
                    if not is_prefixed_var(var_source) and var_source != "_":
                        var_dest = subnodes[0].attrib["VariablePath"].lower()
                        log_debug(f"Remove variable '{var_dest}' assigned from unassigned variable '{var_source}'")
                        kill_list.append(node)
                        continue

            if subnodes[0].tag == "VariableExpressionAst":
                assigned.add(subnodes[0].attrib["VariablePath"].lower())

        elif node.tag in ["ParameterAst"]:
            var_expr = node.find("VariableExpressionAst")
            if var_expr is not None:
                assigned.add(var_expr.attrib["VariablePath"].lower())

        elif node.tag in ["BinaryExpressionAst"]:
            subnodes = list(node)

            operator = node.attrib["Operator"]

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
                        if operator == "Plus":
                            replacements.append((node, other))
                        elif operator in ["Minus", "Multiply"] and other.tag == "ConstantExpressionAst":
                            replacements.append((variable, create_constant_number(0)))
                        else:
                            continue

                        log_debug("Remove unassigned variable use '%s'" % (variable.attrib["VariablePath"]))

    if kill_list or replacements:
        parents = parent_map(ast)

    for node in kill_list:
        parents[node].remove(node)

    for node, repl in replacements:
        replace_node(ast, node, repl, parents=parents)

    return len(kill_list) + len(replacements) != 0
