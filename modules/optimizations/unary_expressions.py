# coding=utf-8

from modules.utils import create_constant_string


def opt_unary_expression_join(ast, parents):
    for node in ast.iter("UnaryExpressionAst"):
        if node.attrib["TokenKind"] == "Join":
            node.tag = "BinaryExpressionAst"
            del node.attrib["TokenKind"]
            node.attrib["Operator"] = "Join"
            node.attrib["StaticType"] = "System.Object"

            empty = create_constant_string('')
            node.append(empty)
            parents[empty] = node

            return True

    return False
