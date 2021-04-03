# coding=utf-8

from modules.utils import create_constant_string


def opt_unary_expression_join(ast):
    for node in ast.iter():
        if node.tag in ["UnaryExpressionAst"] and node.attrib["TokenKind"] == "Join":

            node.tag = "BinaryExpressionAst"
            del node.attrib["TokenKind"]
            node.attrib["Operator"] = "Join"
            node.attrib["StaticType"] = "System.Object"

            node.append(create_constant_string(''))

            return True

    return False
