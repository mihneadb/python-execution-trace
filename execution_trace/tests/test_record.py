import importlib
import json
import mock
import StringIO
import unittest

from parameterized import parameterized

from execution_trace import record
from execution_trace.constants import SOURCE_DUMP_SCHEMA, EXECUTION_DUMP_SCHEMA, RECORD_FN_NAME


# Covers all supported syntax. See `execution_trace.tests.functions`
# package for context.
SYNTAX_TESTS = [
    'simple', 'conditional', 'elif',
    'conditional_else', 'while', 'for',
    'for_else', 'nested_if_in_for',
    'recursive', 'try_ok', 'try_except',
    'try_multi_except', 'try_ok_else',
    'return',
]


def custom_name_func(testcase_func, param_num, param):
    """Generates friendly names such as `test_syntax_while`."""
    return "%s_%s" % (testcase_func.__name__, param.args[0])


class TestRecord(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.log_patcher = mock.patch('execution_trace.record.logger')
        cls.log_patcher.start()

    @classmethod
    def tearDownClass(cls):
        if cls.log_patcher:
            cls.log_patcher.stop()

    def setUp(self):
        self._reset_record()

        self.get_dump_file_patcher = mock.patch('execution_trace.record._get_dump_file')
        self.get_dump_file = self.get_dump_file_patcher.start()
        self.dump_file = StringIO.StringIO()
        self.get_dump_file.return_value = self.dump_file, '/tmp/mock_path'

    def tearDown(self):
        if self.get_dump_file_patcher:
            self.get_dump_file_patcher.stop()
        self.dump_file = None

    @parameterized.expand(SYNTAX_TESTS, testcase_func_name=custom_name_func)
    def test_syntax(self, f_module_name):
        """Go through all supported constructs and test them."""

        f_module_name = 'f_%s' % f_module_name
        f_module = importlib.import_module('execution_trace.tests.functions.%s' % f_module_name)

        f = f_module.f
        args = f_module.args
        expected_trace = f_module.expected_trace
        expected_num_executions = len(expected_trace)

        # Run it.
        f(*args)

        self._check_dump_file(self.dump_file, expected_num_executions,
                              expected_trace=expected_trace)

    def test_can_only_record_one_fn(self):
        """Decorator should not allow multi-function use."""

        @record.record()
        def foo():
            return 3

        def foo2():
            return 4

        with self.assertRaises(ValueError):
            record.record()(foo2)

    def test_multiple_executions_are_recorded(self):
        """Multiple executions end up as multiple lines in the file."""

        @record.record(3)
        def foo():
            pass

        # Run it.
        foo()
        foo()
        foo()

        self._check_dump_file(self.dump_file, 3)

        # Check that the same number of steps is recorded each time.
        self.dump_file.seek(0)
        self.dump_file.readline()
        # We know we have 3 lines.
        line1 = self.dump_file.readline()
        line2 = self.dump_file.readline()
        line3 = self.dump_file.readline()
        self.assertTrue(len(line1) == len(line2) == len(line3),
                        "State was not the same for 3 identical executions.")

    def test_limit_recorded_executions_number(self):
        """`record` takes in `num_executions` and respects it."""

        @record.record(2)
        def foo():
            pass

        # Run it.
        foo()
        foo()
        foo()

        self._check_dump_file(self.dump_file, 2)

    def test_call_original_function_after_num_executions(self):
        """Original function is called when we are done recording."""

        @record.record(2)
        def foo():
            return 3

        # Patch path refers to current module because the decorator injects the
        # record fn in here.
        record_state_fn_path = '%s.%s' % (__name__, RECORD_FN_NAME)
        with mock.patch(record_state_fn_path) as record_mock:
            foo()
            foo()
            r = foo()

        self.assertEqual(record_mock.call_count, 2,
                         "Wrong number of calls to record.")
        self._check_dump_file(self.dump_file, 2)
        self.assertEqual(r, 3,
                         "Third call did not return what it was supposed to.")

    def _check_dump_file(self, dump_file, num_executions=1, expected_trace=None):
        # Rewind the file.
        dump_file.seek(0)
        lines = dump_file.readlines()

        # First line should be source.
        data = json.loads(lines[0])
        SOURCE_DUMP_SCHEMA(data)

        # Next lines should be execution dumps.
        executions = []
        for line in lines[1:]:
            data = json.loads(line)
            EXECUTION_DUMP_SCHEMA(data)
            executions.append(data)

        if expected_trace is not None:
            self.assertEqual(executions, expected_trace,
                             "Wrong trace recorded.")

        self.assertEqual(len(lines) - 1, num_executions,
                         "Wrong number of executions dumped.")

    def _reset_record(self):
        """Resets `record` state as if a new program was run."""
        record.num_fns_recorded = 0
        record._record_store_hidden_123 = None
        record.first_dump_call = True
        record.num_recorded_executions = 0
