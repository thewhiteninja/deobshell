# coding=utf-8
from types import SimpleNamespace

from modules.escaped_chars import escape_string
from modules.logger import log_warn, log_err, log_info
from modules.utils import parent_map

OPS = {
    "Minus"     : " - ",
    "Plus"      : " + ",
    "Format"    : " -f ",
    "Equals"    : " = ",
    "PlusEquals": " += ",
    "Is"        : " -is ",
    "As"        : " -as ",
    "Ieq"       : " -eq ",
    "Ige"       : " -ge ",
    "Ile"       : " -le ",
    "Ine"       : " -ne ",
    "Bxor"      : " -bxor ",
    "Ireplace"  : " -replace ",
    "Join"      : " -join ",
    "Imatch"    : " -match ",
    "And"       : " -and ",
    "Or"        : " -or ",
}


class Rebuilder:
    def __init__(self, output_filename):
        self.stats = SimpleNamespace()
        setattr(self.stats, "nodes", 0)

        self._level = 0
        self._indent = 3

        self._parent_map = {}

        self.output_filename = output_filename

    @staticmethod
    def lastNode(node):
        return node.find('..')

    @staticmethod
    def lastWrite(node):
        n = node
        while n.tag in ["PipelineAst", "PipelineElements", "CommandAst", "CommandElements"]:
            try:
                n = list(n)[-1]
            except IndexError:
                pass
        return n

    def indent(self):
        self.output.write(" " * self._indent * self._level)

    def write(self, s):
        self.output.write(s)

    def rebuild_operator(self, op):
        if op in OPS:
            self.write(OPS[op])
        else:
            log_err(f"Operator {op} not supported")

    def _rebuild_internal(self, node):
        self.stats.nodes += 1

        if node.tag in ["NamedBlockAst"]:
            for subnode in node:
                self._rebuild_internal(subnode)

        elif node.tag in ["PipelineAst"]:
            for subnode in node:
                self._rebuild_internal(subnode)

        elif node.tag in ["Redirections", "UsingStatements"]:
            for subnode in node:
                self._rebuild_internal(subnode)

        elif node.tag in ["Attributes"]:
            if typename := node.find("TypeConstraintAst"):
                self._rebuild_internal(typename)

            if attribute := node.find("AttributeAst"):
                self._rebuild_internal(attribute)
                self.write("\n")

        elif node.tag in ["AttributeAst"]:
            subnodes = list(node)

            self.indent()
            self.write(f"[{node.attrib['TypeName']}]")

            have_args = False
            for subnode in subnodes:
                if len(list(subnode))>0:
                    have_args = True
                    break

            if have_args:
                self.write("(")

            for subnode in subnodes:
                self._rebuild_internal(subnode)

            if have_args:
                self.write(")")

        elif node.tag in ["NamedAttributeArgumentAst"]:
            self.write(f"{node.attrib['ArgumentName']}")
            self.write("=")
            for subnode in node:
                self._rebuild_internal(subnode)

        elif node.tag in ["NamedArguments"]:
            for i, subnode in enumerate(node):
                if i > 0:
                    self.write(", ")
                self._rebuild_internal(subnode)

        elif node.tag in ["ParamBlockAst"]:
            subnodes = list(node)
            if subnodes[0].tag == "Attributes":
                self._rebuild_internal(subnodes[0])
                subnodes.pop(0)

            self.indent()
            self.write("param")

            if node in self._parent_map:
                self.write("\n")
                self.indent()
                self.write("{\n")
                self._level += 1

            for subnode in subnodes:
                self._rebuild_internal(subnode)

            if node in self._parent_map:
                self._level -= 1
                self.indent()
                self.write("}\n")

        elif node.tag in ["PipelineElements"]:
            subnodes = list(node)

            for i, subnode in enumerate(subnodes):
                if i > 0:
                    self.write(" | ")
                self._rebuild_internal(subnode)

        elif node.tag in ["CommandAst"]:
            for subnode in node:
                self._rebuild_internal(subnode)

        elif node.tag in ["CommandElements"]:
            for i, subnode in enumerate(node):
                self._rebuild_internal(subnode)
                if i < len(node) - 1:
                    self.write(" ")

        elif node.tag in ["Statements"]:
            subnodes = list(node)

            for i, subnode in enumerate(subnodes):
                self.indent()
                self._rebuild_internal(subnode)
                if subnode.tag not in ["IfStatementAst", "TryStatementAst", "ForEachStatementAst", "PipelineAst"]:
                    self.write(";\n")
                elif subnode.tag in ["PipelineAst"]:
                    if self.lastWrite(subnode).tag not in ["ScriptBlockExpressionAst"]:
                        self.write(";\n")

        elif node.tag in ["Elements"]:
            for subnode in node:
                self._rebuild_internal(subnode)

        elif node.tag in ["ParenExpressionAst"]:
            self.write("(")
            for subnode in node:
                self._rebuild_internal(subnode)
            self.write(")")

        elif node.tag in ["NestedAst"]:
            for subnode in node:
                self._rebuild_internal(subnode)

        elif node.tag in ["CommandExpressionAst"]:
            for subnode in node:
                self._rebuild_internal(subnode)

        elif node.tag in ["CommandParameterAst"]:
            self.write(f"-{node.attrib['ParameterName']}")

            for subnode in node:
                self._rebuild_internal(subnode)

        elif node.tag in ["ErrorExpressionAst", "ErrorStatementAst"]:
            for subnode in node:
                self._rebuild_internal(subnode)

        elif node.tag in ["ForEachStatementAst"]:
            self.write("\n")

            subnodes = list(node)

            self.write("foreach(")
            self._rebuild_internal(subnodes[0])
            self.write(" in ")
            self._rebuild_internal(subnodes[2])
            self.write(")\n")

            self._rebuild_internal(subnodes[1])

        elif node.tag in ["ReturnStatementAst"]:
            self.write("return")
            for subnode in node:
                self._rebuild_internal(subnode)

        elif node.tag in ["ParameterAst"]:
            subnodes = list(node)
            if subnodes[0].tag == "Attributes":
                self._rebuild_internal(subnodes[0])
                subnodes.pop(0)

            if len(subnodes) == 2:
                self.indent()
                self.write(f"[{node.attrib['StaticType']}]")
                self._rebuild_internal(subnodes[0])
                self.write(" = ")
                self._rebuild_internal(subnodes[1])

        elif node.tag in ["Parameters"]:
            for i, subnode in enumerate(node):
                self._rebuild_internal(subnode)
                if i < len(list(subnode))-1:
                    self.write(", ")
                self.write("\n")

        elif node.tag in ["ScriptBlockExpressionAst", "ScriptBlockAst"]:
            if node in self._parent_map:
                self.write("\n")
                self.indent()
                self.write("{\n")
                self._level += 1

            for subnode in node:
                self._rebuild_internal(subnode)

            if node in self._parent_map:
                self._level -= 1
                self.indent()
                self.write("}\n")

        elif node.tag in ["StatementBlockAst"]:
            self.indent()
            self.write("{\n")

            self._level += 1

            for subnode in node:
                self._rebuild_internal(subnode)

            self._level -= 1

            self.indent()
            self.write("}\n")

        elif node.tag in ["CatchClauses"]:
            self.indent()
            for subnode in node:
                self._rebuild_internal(subnode)

        elif node.tag in ["CatchClauseAst"]:
            self.write("catch\n")

            for subnode in node:
                self._rebuild_internal(subnode)

        elif node.tag in ["BreakStatementAst"]:
            self.write("break")

        elif node.tag in ["TypeConstraintAst"]:
            self.write("[" + node.attrib["TypeName"] + "]")

        elif node.tag in ["TypeExpressionAst"]:
            self.write("[" + node.attrib["TypeName"] + "]")

        elif node.tag in ["ConvertExpressionAst"]:
            to_type = node.find("TypeConstraintAst")
            self._rebuild_internal(to_type)

            for subnode in node:
                if subnode.tag not in ["TypeConstraintAst"]:
                    self._rebuild_internal(subnode)

        elif node.tag in ["Arguments"]:
            subnodes = list(node)
            for i, subnode in enumerate(subnodes):
                if i > 0:
                    self.write(", ")
                self._rebuild_internal(subnode)

        elif node.tag in ["ArrayLiteralAst"]:
            subnodes = list(list(node)[0])
            self.write("@(")
            for i, subnode in enumerate(subnodes):
                if i > 0:
                    self.write(", ")
                self._rebuild_internal(subnode)
            self.write(")")

        elif node.tag in ["VariableExpressionAst"]:
            self.write("$" + node.attrib["VariablePath"])

        elif node.tag in ["AssignmentStatementAst"]:
            subnodes = list(node)
            self._rebuild_internal(subnodes[0])

            self.rebuild_operator(node.attrib["Operator"])

            self._rebuild_internal(subnodes[1])

        elif node.tag in ["UnaryExpressionAst"]:
            self.rebuild_operator(node.attrib["TokenKind"])

            for subnode in node:
                self._rebuild_internal(subnode)

        elif node.tag in ["ExitStatementAst"]:
            self.write("exit")

        elif node.tag in ["ContinueStatementAst"]:
            self.write("continue")

        elif node.tag in ["FunctionDefinitionAst"]:
            subnodes = list(node)

            if len(subnodes) == 2:
                self.write(f"function {node.attrib['Name']}")
                self.write("(")
                self._rebuild_internal(subnodes[0])
                self.write(")")
                self._rebuild_internal(subnodes[1])
            elif len(subnodes) == 1:
                self.write(f"function {node.attrib['Name']}")
                self._rebuild_internal(subnodes[0])

        elif node.tag in ["BinaryExpressionAst"]:
            subnodes = list(node)
            self._rebuild_internal(subnodes[0])

            self.rebuild_operator(node.attrib["Operator"])

            self._rebuild_internal(subnodes[1])

        elif node.tag in ["ConstantExpressionAst"]:
            if node.attrib["StaticType"] == "int":
                self.write(node.text)

        elif node.tag in ["StringConstantExpressionAst", "ExpandableStringExpressionAst"]:
            if node.attrib["StringConstantType"] == "BareWord":
                self.write("" if node.text is None else escape_string(node.text, mode="BareWord"))
            elif node.attrib["StringConstantType"] == "SingleQuoted":
                self.write("'" + ("" if node.text is None else escape_string(node.text, mode="SingleQuoted")) + "'")
            elif node.attrib["StringConstantType"] == "DoubleQuoted":
                self.write('"' + ("" if node.text is None else escape_string(node.text, mode="DoubleQuoted")) + '"')

        elif node.tag in ["IndexExpressionAst"]:
            subnodes = list(node)
            self._rebuild_internal(subnodes[0])
            self.write("[")
            self._rebuild_internal(subnodes[1])
            self.write("]")

        elif node.tag in ["MemberExpressionAst"]:
            subnodes = list(node)

            self._rebuild_internal(subnodes[0])
            if node.attrib["Static"] == "True":
                self.write("::")
            else:
                self.write(".")
            self._rebuild_internal(subnodes[1])

        elif node.tag in ["TryStatementAst"]:
            subnodes = list(node)

            self.write("try\n")

            self._rebuild_internal(subnodes[0])
            self._rebuild_internal(subnodes[1])

        elif node.tag in ["IfStatementAst"]:
            subnodes = list(node)
            self.write("if (")
            self._rebuild_internal(subnodes[0])
            self.write(")\n")

            self._rebuild_internal(subnodes[1])

            if len(subnodes) == 3:
                self.indent()
                self.write("else\n")
                self._rebuild_internal(subnodes[2])
                self.write("\n")

        elif node.tag in ["InvokeMemberExpressionAst"]:

            subnodes = list(node)
            if len(subnodes) == 3:

                for i, subnode in enumerate(subnodes[1:]):
                    if i > 0:
                        if node.attrib["Static"] == "True":
                            self.write("::")
                        else:
                            self.write(".")

                    self._rebuild_internal(subnode)

                self.write('(')
                self._rebuild_internal(subnodes[0])
                self.write(')')

            elif len(subnodes) == 2:

                self._rebuild_internal(subnodes[0])

                if node.attrib["Static"] == "True":
                    self.write("::")
                else:
                    self.write(".")

                self._rebuild_internal(subnodes[1])

                self.write('(')
                self.write(')')




        else:
            log_warn(f"NodeType: {node} unsupported")

    def rebuild(self, node):
        self.stats.nodes = 0
        self._parent_map = parent_map(node)

        log_info(f"Rebuilding script to: {self.output_filename}")

        with open(self.output_filename, "w") as self.output:
            self._rebuild_internal(node)

            log_info(f"{self.stats.nodes} nodes traversed")
            log_info(f"{self.output.tell()} bytes written")
