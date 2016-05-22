import string


def find_indent_level(source):
    """How indented is the def of the fn?"""
    ws = set(string.whitespace)

    for i, c in enumerate(source):
        if c in ws:
            continue
        return i

    return len(source)


def strip_indent(source):
    """Strip leading indent to have source start at col 0."""
    indent_level = find_indent_level(source)
    lines = source.split('\n')

    stripped_lines = []
    for line in lines:
        try:
            line = line[indent_level:]
        except IndexError:
            # Whitespace only / blank line.
            line = ''
        stripped_lines.append(line)
    return '\n'.join(stripped_lines)
