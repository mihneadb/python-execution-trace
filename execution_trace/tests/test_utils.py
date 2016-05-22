import unittest
import mock

from execution_trace.utils import find_indent_level, strip_indent


class TestUtils(unittest.TestCase):
    def test_find_indent_level(self):
        source = '    def foo()'
        self.assertEqual(find_indent_level(source), 4)

        source = '    '
        self.assertEqual(find_indent_level(source), 4)

        source = ''
        self.assertEqual(find_indent_level(source), 0)

    @mock.patch('execution_trace.utils.find_indent_level')
    def test_strip_indent(self, find_indent_mock):
        find_indent_mock.return_value = 4

        indented_source = """
    def foo():
        x = 3

        y = 4
        # Comment here
        if x == 3:
            y = 5
        return x + y
"""
        stripped_source = """
def foo():
    x = 3

    y = 4
    # Comment here
    if x == 3:
        y = 5
    return x + y
"""

        self.assertEqual(strip_indent(indented_source), stripped_source,
                         "Incorrectly stripped indentation.")
