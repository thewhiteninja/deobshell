# coding=utf-8

from modules.barewords import BAREWORDS
from modules.logger import log_debug
from modules.special_vars import SPECIAL_VARS_NAMES
from modules.utils import replace_node, create_constant_string, get_array_literal_values, create_array_literal_values, \
    get_used_vars


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
    for node in ast.iter():
        if node.tag in ["TypeConstraintAst", "TypeExpressionAst"]:
            typename = node.attrib["TypeName"]

            new_value = typename
            new_value = ".".join(
                [BAREWORDS[t.lower()] if t.lower() in BAREWORDS else t for t in new_value.split(".")])
            new_value = "-".join(
                [BAREWORDS[t.lower()] if t.lower() in BAREWORDS else t for t in new_value.split("-")])

            if typename != new_value:
                node.attrib["TypeName"] = new_value

                log_debug("Fix typename case from '%s' to '%s'" % (typename, new_value))

                return True

    return False


def opt_simplify_paren_single_expression(ast):
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

                replace_node(ast, node, subnodes[0])

                return True
    return False


def opt_simplify_pipeline_single_command(ast):
    for node in ast.iter():
        if node.tag == "PipelineAst":
            subnodes = list(node)
            if len(subnodes) == 1 and subnodes[0].tag in ["PipelineElements"]:
                subnodes = list(subnodes[0])
            if len(subnodes) == 1:

                log_debug("Replace pipeline with single elements by %s" % subnodes[0].tag)

                replace_node(ast, node, subnodes[0])

                return True
    return False


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


def opt_replace_constant_variable_by_value(ast):
    cst_assigned = dict()

    used_vars = get_used_vars(ast)

    for node in ast.iter():
        if node.tag in ["AssignmentStatementAst"]:
            subnodes = list(node)
            if subnodes[0].tag == "VariableExpressionAst":
                variable = subnodes[0]
                if subnodes[1].tag == "CommandExpressionAst":
                    subnodes = list(subnodes[1])
                    if len(subnodes) == 1:
                        if subnodes[0].tag == "StringConstantExpressionAst":
                            cst_assigned[variable.attrib["VariablePath"].lower()] = subnodes[0].text
                        elif subnodes[0].tag == "ArrayLiteralAst":
                            cst_assigned[variable.attrib["VariablePath"].lower()] = get_array_literal_values(
                                subnodes[0])
                    else:
                        if variable.attrib["VariablePath"].lower() in cst_assigned:
                            del cst_assigned[variable.attrib["VariablePath"].lower()]

        if node.tag in ["UnaryExpressionAst", "BinaryExpressionAst", "Arguments", "InvokeMemberExpressionAst"]:
            subnodes = list(node)
            for subnode in subnodes:
                if subnode.tag == "VariableExpressionAst":
                    var_name = subnode.attrib["VariablePath"].lower()
                    if var_name in cst_assigned and used_vars.setdefault(var_name, 0) == 1:

                        value = cst_assigned[var_name]

                        if isinstance(value, str):
                            new_element = create_constant_string(value,
                                                                 "BareWord" if node.tag == "InvokeMemberExpressionAst"
                                                                 else "DoubleQuoted")

                            log_debug("Replace constant variable %s (string) in expression" % (
                                subnode.attrib["VariablePath"]))

                            replace_node(ast, subnode, new_element)
                            return True

                        elif isinstance(value, list):
                            new_element = create_array_literal_values(value)
                            log_debug(
                                "Replace constant variable %s (array) in expression" % (subnode.attrib["VariablePath"]))
                            replace_node(ast, subnode, new_element)
                            return True

    return False
