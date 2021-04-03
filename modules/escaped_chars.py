# coding=utf-8

ESCAPED_CHARS = {
    '\'': '\'\'',
    '\n': '`n',
    '#' : "`#"
}


def escape_string(s, mode="BareWord"):
    return ''.join([ESCAPED_CHARS.setdefault(c, c) for c in s])
