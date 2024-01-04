# coding=utf-8
from types import SimpleNamespace

from modules.logger import log_info, log_debug
from modules.optimizations.alias import opt_alias
from modules.optimizations.binary_expressions import opt_binary_expression_plus, opt_binary_expression_format, \
    opt_binary_expression_replace, opt_binary_expression_join, opt_binary_expression_numeric_operators
from modules.optimizations.complex_operations import opt_value_of_const_array
from modules.optimizations.dead_codes import opt_unused_variable, opt_remove_uninitialised_variable_usage, \
    opt_remove_dead_loops, opt_remove_dead_switch_cases, opt_remove_dead_if_clauses
from modules.optimizations.empty_nodes import opt_remove_empty_nodes
from modules.optimizations.invoke_member import opt_invoke_split_string, opt_invoke_replace_string, \
    opt_invoke_reverse_array, opt_invoke_expression, opt_invoke_base64_decode
from modules.optimizations.replace_long_names import opt_long_variable_names
from modules.optimizations.simplifications import opt_convert_bogus_loops, opt_simplify_paren_single_expression, \
    opt_bareword_case, opt_constant_string_type, opt_prefixed_variable_case, opt_replace_constant_variable_by_value, \
    opt_simplify_single_array, opt_simplify_pipeline_single_command, opt_type_constraint_from_convert, \
    opt_command_element_as_bareword, opt_type_constraint_case, opt_special_variable_case, \
    opt_lift_switch_with_just_default
from modules.optimizations.type_convertions import opt_convert_type_to_int, opt_convert_type_to_type, \
    opt_convert_type_to_char, opt_convert_type_to_array, opt_convert_type_to_string
from modules.optimizations.unary_expressions import opt_unary_expression_join


def optimize_pass(ast, stats):
    optimizations = [
        # Remove nodes
        opt_remove_empty_nodes,
        opt_unused_variable,
        opt_simplify_paren_single_expression,
        opt_simplify_pipeline_single_command,
        opt_simplify_single_array,
        opt_remove_uninitialised_variable_usage,
        opt_remove_dead_switch_cases,
        opt_remove_dead_loops,
        opt_remove_dead_if_clauses,
        # Expressions
        opt_unary_expression_join,
        opt_binary_expression_plus,
        opt_binary_expression_format,
        opt_binary_expression_replace,
        opt_binary_expression_join,
        opt_binary_expression_numeric_operators,
        # Invoke member
        opt_invoke_split_string,
        opt_invoke_replace_string,
        opt_invoke_reverse_array,
        opt_invoke_expression,
        opt_invoke_base64_decode,
        # Type conversion
        opt_convert_type_to_type,
        opt_convert_type_to_string,
        opt_convert_type_to_int,
        opt_convert_type_to_char,
        opt_convert_type_to_array,
        # Complex operations
        opt_value_of_const_array,
        # Syntax simplification
        opt_long_variable_names,
        opt_prefixed_variable_case,
        opt_bareword_case,
        opt_constant_string_type,
        opt_special_variable_case,
        opt_type_constraint_from_convert,
        opt_command_element_as_bareword,
        opt_type_constraint_case,
        opt_alias,
        opt_convert_bogus_loops,
        opt_lift_switch_with_just_default,
        # Last
        opt_replace_constant_variable_by_value,
    ]

    for opt in optimizations:
        did_opt = False
        while opt(ast):
            stats.steps += 1
            did_opt = True
        if did_opt:
            return True

    return False


class Optimizer:
    def __init__(self):
        self.stats = SimpleNamespace()
        setattr(self.stats, "steps", 0)

    def optimize(self, ast):
        count_in = sum(1 for _ in ast.getroot().iter())
        log_debug(f"{count_in} nodes loaded")

        while optimize_pass(ast, self.stats):
            pass

        log_info(f"{self.stats.steps} optimization steps executed")

        count_out = sum(1 for _ in ast.getroot().iter())
        ratio = "{:02.2f}".format(count_out / count_in * 100.00)
        log_debug(f"{count_out} nodes in output ({ratio}%)")

        return ast
