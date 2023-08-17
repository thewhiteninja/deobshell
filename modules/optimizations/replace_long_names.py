# coding=utf-8
from modules.logger import log_debug

# Names longer than this will be renamed.
RENAME_THRESHOLD = 60

VAR_ATTRIB = {
    "VariableExpressionAst": "VariablePath",
    "ParameterAst": "Name",
}

def opt_long_variable_names(ast):
    counter = 0
    var_mapping = {}
    result = False

    for node in ast.iter():
        if node.tag in ("VariableExpressionAst", "ParameterAst"):
            name = node.attrib[VAR_ATTRIB[node.tag]]

            has_dollar = False
            if name[0] == "$":
                name = name[1:]
                has_dollar = True

            if len(name) < RENAME_THRESHOLD:
                continue

            if name not in var_mapping:
                var_mapping[name] = f"deob_{counter}"
                log_debug(f"Replacing long variable name {name} with {var_mapping[name]}")
                counter += 1

            new_name = var_mapping[name]
            if has_dollar:
                new_name = f"${new_name}"
            
            node.attrib[VAR_ATTRIB[node.tag]] = new_name
            result = True

    return result
