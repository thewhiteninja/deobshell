# coding=utf-8
from xml.etree.ElementTree import Element

from modules.logger import log_debug
from modules.special_vars import SPECIAL_VARS_VALUES
from modules.utils import replace_node, create_array_literal_values


def opt_convert_type_to_type(ast):
    for node in ast.iter():
        if node.tag in ["ConvertExpressionAst"]:
            type_name = node.find("TypeConstraintAst")
            if type_name is not None:
                type_name = type_name.attrib["TypeName"].lower()

            if type_name in ["type"]:
                cst_string_node = node.find("StringConstantExpressionAst")
                if cst_string_node is not None:
                    type_value = cst_string_node.text

                    new_element = Element("StringConstantExpressionAst",
                                          {
                                              "StringConstantType": "BareWord",
                                              "StaticType"        : "string",
                                          })

                    new_element.text = "[" + type_value + "]"

                    log_debug("Replace type string '%s' by type '%s'" % (type_value, new_element.text))

                    replace_node(ast, node, new_element)

                    return True


def opt_convert_type_to_string(ast):
    for node in ast.iter():
        if node.tag in ["ConvertExpressionAst"]:
            type_name = node.find("TypeConstraintAst")
            if type_name is not None:
                type_name = type_name.attrib["TypeName"].lower()

            if type_name in ["string"]:
                cst_string_node = node.find("VariableExpressionAst")
                if cst_string_node is not None:
                    var_value = cst_string_node.attrib["VariablePath"]

                    if var_value.lower() in SPECIAL_VARS_VALUES and SPECIAL_VARS_VALUES[var_value.lower()] is not None:
                        log_debug(
                            "Use special variable value '%s' for $%s" % (SPECIAL_VARS_VALUES[var_value.lower()], var_value))
                        var_value = SPECIAL_VARS_VALUES[var_value.lower()]

                    new_element = Element("StringConstantExpressionAst",
                                          {
                                              "StringConstantType": "DoubleQuoted",
                                              "StaticType"        : "string",
                                          })

                    new_element.text = var_value

                    log_debug("Replace type of variable $%s to string" % (var_value))

                    replace_node(ast, node, new_element)

                    return True

                cst_string_node = node.find("StringConstantExpressionAst")
                if cst_string_node is not None:

                    log_debug("Remove unused cast to string for '%s'" % (cst_string_node.text))

                    replace_node(ast, node, cst_string_node)

                    return True


def opt_convert_type_to_array(ast):
    for node in ast.iter():
        if node.tag in ["ConvertExpressionAst"]:
            type_name = node.find("TypeConstraintAst")
            if type_name is not None:
                type_name = type_name.attrib["TypeName"].lower()

            if type_name == "array":
                cst_string_node = node.find("StringConstantExpressionAst")
                if cst_string_node is not None:

                    log_debug("Replace array of one string to string '%s'" % cst_string_node.text)

                    replace_node(ast, node, cst_string_node)

            elif type_name == "char[]":
                cst_string_node = node.find("StringConstantExpressionAst")
                if cst_string_node is not None:
                    arrayed = [c for c in cst_string_node.text]

                    new_array_ast = create_array_literal_values(arrayed)

                    log_debug("Replace (cast) string to array: '%s'" % arrayed)

                    replace_node(ast, node, new_array_ast)


def opt_convert_type_to_char(ast):
    for node in ast.iter():
        if node.tag in ["ConvertExpressionAst"]:
            type_name = node.find("TypeConstraintAst")
            if type_name is not None:
                type_name = type_name.attrib["TypeName"].lower()

            if type_name == "char":
                cst_int_node = node.find("ConstantExpressionAst")

                if cst_int_node is not None and cst_int_node.attrib["StaticType"] == "int":
                    type_value = int(cst_int_node.text)

                    new_element = Element("StringConstantExpressionAst",
                                          {
                                              "StringConstantType": "SingleQuoted",
                                              "StaticType"        : "string",
                                          })
                    new_element.text = chr(type_value)

                    log_debug("Replace integer %d convertion to char '%s'" % (type_value, new_element.text))

                    replace_node(ast, node, new_element)

                    return True

    return False
