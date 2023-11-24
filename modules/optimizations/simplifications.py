# coding=utf-8

from xml.etree.ElementTree import Element

from modules.barewords import BAREWORDS
from modules.logger import log_debug
from modules.scope import Scope
from modules.special_vars import SPECIAL_VARS_NAMES
from modules.utils import (create_array_literal_values, create_constant_number,
                           create_constant_string, get_array_literal_values, get_assigned_vars,
                           parent_map, replace_node, to_numeric)


def opt_command_element_as_bareword(ast):
    for node in ast.iter():
        if node.tag == "CommandElements":
            for subnode in node:
                if subnode.tag == "StringConstantExpressionAst" and subnode.attrib["StringConstantType"] != "BareWord":
                    if subnode.text in BAREWORDS:
                        subnode.attrib["StringConstantType"] = "BareWord"

                        log_debug(f"Fix string type for command {subnode.text}")

                        return True
    return False


def opt_special_variable_case(ast):
    for node in ast.iter():
        if node.tag == "VariableExpressionAst":
            if node.attrib["VariablePath"].lower() in SPECIAL_VARS_NAMES:
                if node.attrib["VariablePath"] != SPECIAL_VARS_NAMES[node.attrib["VariablePath"].lower()]:
                    node.attrib["VariablePath"] = SPECIAL_VARS_NAMES[node.attrib["VariablePath"].lower()]

                    log_debug(f'Fix variable name case for ${node.attrib["VariablePath"]}')

                    return True
    return False


def opt_type_constraint_from_convert(ast):
    for node in ast.iter():
        if node.tag == "ConvertExpressionAst":
            subnodes = list(node)
            if subnodes[0].tag == "TypeConstraintAst":
                if subnodes[0].attrib["TypeName"] != node.attrib["StaticType"]:
                    subnodes[0].attrib["TypeName"] = node.attrib["StaticType"]
                    return True
    return False


def opt_type_constraint_case(ast):
    def get_new_value(t):
        new_val = t
        new_val = ".".join(
            [BAREWORDS[t.lower()] if t.lower() in BAREWORDS else t for t in new_val.split(".")])
        new_val = "-".join(
            [BAREWORDS[t.lower()] if t.lower() in BAREWORDS else t for t in new_val.split("-")])
        return new_val

    for node in ast.iter():
        if node.tag == "ConvertExpressionAst":
            typename = node.attrib["StaticType"]
            new_value = get_new_value(typename)

            if typename != new_value:
                node.attrib["StaticType"] = new_value
                log_debug("Fix typename case from '%s' to '%s'" % (typename, new_value))
                return True

        elif node.tag in ["TypeConstraintAst", "TypeExpressionAst"]:
            typename = node.attrib["TypeName"]
            new_value = get_new_value(typename)

            if typename != new_value:
                node.attrib["TypeName"] = new_value
                log_debug("Fix typename case from '%s' to '%s'" % (typename, new_value))
                return True

    return False


def opt_simplify_paren_single_expression(ast):
    replacements = []
    for node in ast.iter():
        if node.tag == "ParenExpressionAst":
            subnodes = list(node)
            if len(subnodes) == 1 and subnodes[0].tag in ["PipelineAst"]:
                subnodes = list(subnodes[0])
            if len(subnodes) == 1 and subnodes[0].tag in ["PipelineElements"]:
                subnodes = list(subnodes[0])
            if len(subnodes) == 1 and subnodes[0].tag in ["CommandExpressionAst"]:
                subnodes = list(subnodes[0])
            if len(subnodes) == 1 and subnodes[0].tag not in ["CommandAst", "UnaryExpressionAst",
                                                              "BinaryExpressionAst"]:
                log_debug("Replace paren with single expression by %s" % subnodes[0].tag)

                replacements.append((node, subnodes[0]))

    if replacements:
        parents = parent_map(ast)
    for node, repl in replacements:
        replace_node(ast, node, repl, parents=parents)

    return len(replacements) != 0


def opt_simplify_pipeline_single_command(ast):
    replacements = []
    for node in ast.iter():
        if node.tag == "PipelineAst":
            subnodes = list(node)
            if len(subnodes) == 1 and subnodes[0].tag in ["PipelineElements"]:
                subnodes = list(subnodes[0])
            if len(subnodes) == 1:
                log_debug("Replace pipeline with single elements by %s" % subnodes[0].tag)

                replacements.append((node, subnodes[0]))

    if replacements:
        parents = parent_map(ast)
    for node, repl in replacements:
        replace_node(ast, node, repl, parents=parents)

    return len(replacements) != 0


def opt_simplify_single_array(ast):
    for node in ast.iter():
        if node.tag == "ArrayLiteralAst":
            subnodes = list(node)
            if len(subnodes) == 1 and subnodes[0].tag in ["Elements"]:
                subnodes = list(subnodes[0])
            if len(subnodes) == 1 and subnodes[0].tag not in ["CommandAst", "UnaryExpressionAst",
                                                              "BinaryExpressionAst"]:
                log_debug("Replace array with single element by %s" % subnodes[0].tag)

                replace_node(ast, node, subnodes[0])

                return True
    return False


def opt_constant_string_type(ast):
    for node in ast.iter():
        if node.tag in ["InvokeMemberExpressionAst", "MemberExpressionAst"]:
            for cst_string_node in node.findall("StringConstantExpressionAst"):
                if cst_string_node.text is None:
                    continue
                member = cst_string_node.text.lower()
                if member in BAREWORDS:
                    if cst_string_node.attrib["StringConstantType"] != "BareWord":
                        cst_string_node.text = BAREWORDS[member]

                        log_debug("Fix member string type for '%s'" % cst_string_node.text)

                        cst_string_node.attrib["StringConstantType"] = "BareWord"

                        return True

        if node.tag in ["CommandElements"]:
            for subnode in node:
                if subnode.tag == "StringConstantExpressionAst" and subnode.attrib["StringConstantType"] != "BareWord":
                    subnode.attrib["StringConstantType"] = "BareWord"

                    log_debug("Fix command string type for '%s'" % subnode.text)

                    return True
                break
    return False


def opt_bareword_case(ast):
    for node in ast.iter():
        if node.tag in ["StringConstantExpressionAst"] and node.attrib["StringConstantType"] == "BareWord":
            old_value = node.text

            new_value = node.text
            is_type = new_value[0] == "[" and new_value[-1] == "]"
            if is_type:
                new_value = new_value[1:-1]

            new_value = ".".join([BAREWORDS[t.lower()] if t.lower() in BAREWORDS else t for t in new_value.split(".")])
            new_value = "-".join([BAREWORDS[t.lower()] if t.lower() in BAREWORDS else t for t in new_value.split("-")])

            if is_type:
                new_value = "[" + new_value + "]"

            if old_value != new_value:
                node.text = new_value

                log_debug("Fix bareword case from '%s' to '%s'" % (old_value, node.text))

                return True

    return False


def opt_prefixed_variable_case(ast):
    for node in ast.iter():
        if node.tag == "StringConstantExpressionAst" and node.attrib["StringConstantType"] == "BareWord":
            names = node.text.split(":")
            if len(names) > 1 and names[0].lower() in ["variable", "env"]:
                old_name = node.text
                names[0] = names[0].lower()
                new_name = ":".join(names)

                if old_name != new_name:
                    node.text = new_name

                    log_debug("Fix string case from '%s' to '%s'" % (old_name, node.text))

                    return True
    return False


class ConstantPropagator:

    def __init__(self):
        self._scope = Scope()
        self._loop_assigned = None
        self.replacements = []

    def _replace_var(self, parent_node, var_expression):
        var_name = var_expression.attrib["VariablePath"].lower()
        if self._loop_assigned is not None and var_name in self._loop_assigned:
            # Variable is touched in a loop, so we can't arrive
            # at any conclusion without a more complicated analysis.
            return

        value = self._scope.get_var(var_name)
        if value is not None:
            if isinstance(value, str):
                new_element = create_constant_string(value,
                                                     "BareWord" if parent_node.tag == "InvokeMemberExpressionAst"
                                                     else "DoubleQuoted")

                log_debug("Replace constant variable %s (string) in expression" % (
                    var_expression.attrib["VariablePath"]))

                self.replacements.append((var_expression, new_element))

            elif isinstance(value, (int, float)):
                new_element = create_constant_number(value)
                log_debug("Replace constant variable %s (number) in expression" % (
                    var_expression.attrib["VariablePath"]))
                self.replacements.append((var_expression, new_element))

            elif isinstance(value, list):
                new_element = create_array_literal_values(value)
                log_debug(
                    "Replace constant variable %s (array) in expression" % (var_expression.attrib["VariablePath"]))
                self.replacements.append((var_expression, new_element))

    def propagate(self, node):
        is_loop_tag = False

        if node.tag == "StatementBlockAst":
            self._scope.enter()

        elif node.tag in ["ForStatementAst", "ForEachStatementAst", "DoWhileStatementAst", "WhileStatementAst"]:
            if self._loop_assigned is None:
                # Once entering any type of loop, get a set of variables the loop touches.
                # This includes any nested loop statements, so we only get it once (until
                # we leave the topmost-level loop).
                self._loop_assigned = get_assigned_vars(node)
                is_loop_tag = True

        elif node.tag in ["AssignmentStatementAst"]:
            subnodes = list(node)
            if subnodes[0].tag == "VariableExpressionAst":
                variable = subnodes[0]
                if subnodes[1].tag == "CommandExpressionAst":
                    var_name = variable.attrib["VariablePath"].lower()
                    subnodes = list(subnodes[1])
                    if len(subnodes) == 1 and node.attrib["Operator"] == "Equals":
                        if subnodes[0].tag == "StringConstantExpressionAst":
                            self._scope.set_var(var_name, subnodes[0].text)
                        elif subnodes[0].tag == "ConstantExpressionAst":
                            self._scope.set_var(var_name, to_numeric(subnodes[0].text))
                        elif subnodes[0].tag == "ArrayLiteralAst":
                            self._scope.set_var(var_name, get_array_literal_values(subnodes[0]))
                        elif subnodes[0].tag == "VariableExpressionAst":
                            # $somevar = $var_that_is_constant;
                            self._replace_var(node, subnodes[0])
                    else:
                        self._scope.del_var(var_name)

        elif node.tag == "UnaryExpressionAst" and node.attrib["TokenKind"] in ["PostfixPlusPlus", "PostfixMinusMinus"]:
            subnodes = list(node)
            if subnodes[0].tag == "VariableExpressionAst":
                variable = subnodes[0]
                self._scope.del_var(variable.attrib["VariablePath"].lower())

        if node.tag in ["UnaryExpressionAst", "BinaryExpressionAst", "Arguments",
                        "InvokeMemberExpressionAst", "ConvertExpressionAst"]:
            subnodes = list(node)
            for subnode in subnodes:
                if subnode.tag == "VariableExpressionAst":
                    self._replace_var(node, subnode)

        for subnode in node:
            self.propagate(subnode)

        if is_loop_tag:
            self._loop_assigned = None

        if node.tag == "StatementBlockAst":
            self._scope.leave()


def opt_replace_constant_variable_by_value(ast):
    prop = ConstantPropagator()
    prop.propagate(ast.getroot())

    if prop.replacements:
        parents = parent_map(ast)
    for node, repl in prop.replacements:
        replace_node(ast, node, repl, parents=parents)

    return len(prop.replacements) != 0


def opt_convert_bogus_loops(ast):
    """Turns loops with one unconditional break at the end into an if-statement."""

    for node in ast.iter():
        if node.tag == "WhileStatementAst" and len(node) == 2:
            if node[0].tag == "StatementBlockAst" and node[0][0].tag == "Statements":
                statements = node[0][0]
                last_break = statements[-1]
                if last_break.tag == "BreakStatementAst":
                    if any(stmt.tag in ["BreakStatementAst", "ContinueStatementAst"] and stmt != last_break
                           for stmt in statements.iter()):
                        # There's another break/continue somewhere in the loop, so we can't convert this one.
                        continue

                    statements.remove(last_break)

                    if_stmt = Element("IfStatementAst")
                    if_stmt.append(node[1])  # Condition
                    if_stmt.append(node[0])  # StatementBlockAst

                    log_debug("Converting while-loop to if-statement")
                    replace_node(ast, node, if_stmt)
                    return True

        elif node.tag == "ForStatementAst":
            assign_index = 0 if node[0].tag == "AssignmentStatementAst" else -1
            for block_index in range(assign_index + 1, 3):
                if node[block_index].tag == "StatementBlockAst":
                    break
            else:
                continue  # Shouldn't happen

            statements = node[block_index][0]
            if statements.tag != "Statements":
                continue

            last_break = statements[-1]
            if last_break.tag == "BreakStatementAst":
                if any(stmt.tag in ["BreakStatementAst", "ContinueStatementAst"] and stmt != last_break
                       for stmt in statements.iter()):
                    # There's another break/continue somewhere in the loop, so we can't convert this one.
                    continue

                statements.remove(last_break)

                cond_index = block_index + 1 if len(node) > block_index + 1 else -1
                if cond_index != -1:
                    if_stmt = Element("IfStatementAst")
                    if_stmt.append(node[cond_index])   # Condition
                    if_stmt.append(node[block_index])  # StatementBlockAst

                    log_debug("Converting for-loop to if-statement")
                    if assign_index != -1:
                        replace_node(ast, node, (node[assign_index], if_stmt))
                    else:
                        replace_node(ast, node, if_stmt)
                    return True

                else:
                    log_debug("Lifting for-loop without condition")
                    if assign_index != -1:
                        replace_node(ast, node, [node[assign_index]] + list(statements))
                    else:
                        replace_node(ast, node, list(statements))
                    return True

    return False


def opt_lift_switch_with_just_default(ast):
    """
    switch (<nothing-with-potential-side-effects>) {
      default {
        ...
      }
    }
    """
    for node in ast.iter():
        if node.tag == "SwitchStatementAst" and len(node) == 2:
            if node[1].tag == "CommandExpressionAst" and node[1][0].tag in \
                    ["ConstantExpressionAst", "StringConstantExpressionAst", "VariableExpressionAst"]:
                if node[0].tag == "StatementBlockAst" and node[0][0].tag == "Statements":
                    replace_node(ast, node, list(node[0][0]))
                    return True

    return False
