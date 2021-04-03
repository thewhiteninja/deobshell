# coding=utf-8
import errno
import glob
import os
import pathlib
import platform
import shutil
import sys
import time
from datetime import datetime
from xml.etree.ElementTree import Element


def get_used_vars(ast):
    parents = parent_map(ast)
    used_vars = dict()
    for node in ast.iter():
        if node.tag == "VariableExpressionAst":
            if parents[node].tag != "AssignmentStatementAst" or parents[node].attrib["Operator"] != "Equals":
                var_name = node.attrib["VariablePath"].lower()
                if var_name in used_vars:
                    used_vars[var_name] += 1
                else:
                    used_vars[var_name] = 1
    return used_vars


def create_constant_string(value, string_type="SingleQuoted"):
    empty_string_element = Element("StringConstantExpressionAst")
    empty_string_element.text = value
    empty_string_element.attrib["StringConstantType"] = string_type
    empty_string_element.attrib["StaticType"] = "string"
    return empty_string_element


def create_array_literal_values(values, string_type="SingleQuoted"):
    new_array_ast = Element("ArrayLiteralAst",
                            {
                                "StaticType": "System.Object[]",
                            })
    new_elements = Element("Elements")

    for val in values:
        new_string_item = Element("StringConstantExpressionAst",
                                  {
                                      "StringConstantType": string_type
                                  })
        new_string_item.text = str(val)
        new_elements.append(new_string_item)

    new_array_ast.append(new_elements)
    return new_array_ast


def get_array_literal_values(node):
    argument_values = []

    arguments = node
    if arguments is not None:
        arguments = arguments.find("Elements")
        if arguments is not None:
            for element in list(arguments):
                if element.tag == "StringConstantExpressionAst":
                    argument_values.append(element.text)
                elif element.tag == "ConstantExpressionAst":
                    argument_values.append(int(element.text))
                else:
                    return None
            return argument_values

    return None


def is_prefixed_var(param):
    prefix = param.lower().split(':')[0]
    return prefix in ["env"]


def parent_map(ast):
    return dict((c, p) for p in ast.iter() for c in p)


def replace_node(ast, old, new, until=None):
    parents = parent_map(ast)
    for i, element in enumerate(parents[old]):
        if element == old:
            if until is not None:
                while element.tag != until and element in parents:
                    element = parents[element]
            if element in parents:
                parents[element].remove(element)
                parents[element].insert(i, new)
                break


def delete_node(ast, old, until=None):
    parents = parent_map(ast)
    for i, element in enumerate(parents[old]):
        if element == old:
            if until is not None:
                while element.tag != until:
                    element = parents[element]
            parents[element].remove(element)
            break


def check_python_version():
    if platform.python_version_tuple()[0] == "2":
        print("Please use Python 3. (Python 2 is no more maintained).")
        sys.exit(0)


def is_root_path(p):
    return os.path.dirname(p) == p


def change_extension(f, ext):
    base = os.path.splitext(f)[0]
    os.rename(f, base + ext)


def delete_directory(dir_path):
    shutil.rmtree(dir_path)


def make_directory(dir_path):
    if not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                return False
    return True


def update_timestamp(directory):
    f = open(os.path.join(directory, "__time__"), "w")
    f.write(datetime.now().strftime("%Y%m%d"))
    f.close()


def get_timestamp(directory):
    f = open(os.path.join(directory, "__time__"), "r")
    d = f.read()
    f.close()
    return datetime.strptime(d, "%Y%m%d")


def file_exists(filename):
    f = pathlib.Path(filename)
    return f.is_file()


def dir_exists(filename):
    f = pathlib.Path(filename)
    return f.is_dir()


def is_os64():
    return "PROGRAMFILES(X86)" in os.environ


def python64():
    return platform.architecture()[0] == "64bit"


def welcome():
    print("Starting %s at %s (%s version)\n" % (
        os.path.basename(sys.argv[0]), time.asctime(time.localtime(time.time())), platform.architecture()[0]))


def humansize(nbytes):
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    if nbytes == 0:
        return '0 B'
    i = 0
    while nbytes >= 1024 and i < len(suffixes) - 1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])


def xor(data, key):
    return bytearray(a ^ key for a in data)


def clean_folder(directory):
    for f in glob.glob(directory + '/*'):
        os.remove(f)
