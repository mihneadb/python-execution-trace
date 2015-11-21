import unittest
import mock

from record import record, RECORD_FN_NAME, find_indent_level, strip_indent


class TestRecord(unittest.TestCase):

    # Patch path refers to current module because the decorator injects the
    # record fn in here.
    record_state_fn_path = 'test_record.%s' % RECORD_FN_NAME

    def test_simple(self):
        """Simple function, no loop, no return, no conditional."""

        @record
        def foo():
            x = 5
            y = 6

        with mock.patch(self.record_state_fn_path) as record_mock:
            foo()

        self.assertEqual(record_mock.call_count, 2, "Missed some call sites.")

    def test_conditional(self):
        """Simple fn with a simple conditional."""

        @record
        def foo():
            x = 3
            y = 2
            if x == 3:
                y = 5

        with mock.patch(self.record_state_fn_path) as record_mock:
            foo()

        self.assertEqual(record_mock.call_count, 4, "Missed some call sites.")

    def test_conditional_else(self):
        """Simple fn with a simple conditional."""

        @record
        def foo():
            x = 3
            y = 2
            if x != 3:
                y = 5
            else:
                y = 6

        with mock.patch(self.record_state_fn_path) as record_mock:
            foo()

        self.assertEqual(record_mock.call_count, 4, "Missed some call sites.")

    def test_find_indent_level(self):
        source = '    def foo()'
        self.assertEqual(find_indent_level(source), 4)

        source = '    '
        self.assertEqual(find_indent_level(source), 4)

        source = ''
        self.assertEqual(find_indent_level(source), 0)

    @mock.patch('record.find_indent_level')
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
