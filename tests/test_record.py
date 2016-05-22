import json
import mock
import StringIO
import unittest

from trace import record
from trace.constants import SOURCE_DUMP_SCHEMA, EXECUTION_DUMP_SCHEMA, RECORD_FN_NAME


class TestRecord(unittest.TestCase):

    # Patch path refers to current module because the decorator injects the
    # record fn in here.
    record_state_fn_path = '%s.%s' % (__name__, RECORD_FN_NAME)
    dump_state_fn_path = 'trace.record.dump_recorded_state'

    @classmethod
    def setUpClass(cls):
        cls.log_patcher = mock.patch('trace.record.logger')
        cls.log_patcher.start()

    @classmethod
    def tearDownClass(cls):
        if cls.log_patcher:
            cls.log_patcher.stop()

    def setUp(self):
        self._reset_record()

        self.get_dump_file_patcher = mock.patch('trace.record._get_dump_file')
        self.get_dump_file = self.get_dump_file_patcher.start()
        self.dump_file = StringIO.StringIO()
        self.get_dump_file.return_value = self.dump_file, '/tmp/mock_path'

    def tearDown(self):
        if self.get_dump_file_patcher:
            self.get_dump_file_patcher.stop()
        self.dump_file = None

    def test_simple(self):
        """Simple function, no loop, no return, no conditional."""

        @record.record()
        def foo():
            x = 5
            y = 6

        with mock.patch(self.record_state_fn_path) as record_mock:
            foo()

        self._check_record_calls(record_mock, [3, 4])
        self._check_dump_file_structure(self.dump_file)

    def test_conditional(self):
        """Fn with a simple conditional."""

        @record.record()
        def foo():
            x = 3
            y = 2
            if x == 3:
                y = 5

        with mock.patch(self.record_state_fn_path) as record_mock:
            foo()

        self._check_record_calls(record_mock, [3, 4, 5, 6])
        self._check_dump_file_structure(self.dump_file)

    def test_elif(self):
        """Fn with a simple conditional."""

        @record.record()
        def foo():
            x = 3
            if x == 1:
                y = 5
            elif x == 2:
                y = 6
            elif x == 3:
                y = 7

        with mock.patch(self.record_state_fn_path) as record_mock:
            foo()

        self._check_record_calls(record_mock, [3, 4, 6, 8, 9])
        self._check_dump_file_structure(self.dump_file)

    def test_conditional_else(self):
        """Fn with conditional having else."""

        @record.record()
        def foo():
            x = 3
            y = 2
            if x != 3:
                y = 5
            else:
                y = 6

        with mock.patch(self.record_state_fn_path) as record_mock:
            foo()

        # Note: `else` does not have a lineno, using `if`'s lineno.
        self._check_record_calls(record_mock, [3, 4, 5, 8])
        self._check_dump_file_structure(self.dump_file)

    def test_while(self):
        """Fn with a while."""

        @record.record()
        def foo():
            x = 3
            y = 6

            while x < y:
                x += 1

        with mock.patch(self.record_state_fn_path) as record_mock:
            foo()

        self._check_record_calls(record_mock, [3, 4, 6, 7, 6, 7, 6, 7, 6])
        self._check_dump_file_structure(self.dump_file)

    def test_for(self):
        """Fn with a for."""

        @record.record()
        def foo():
            x = 3
            s = 0
            for i in range(x):
                s = s + i

        with mock.patch(self.record_state_fn_path) as record_mock:
            foo()

        self._check_record_calls(record_mock, [3, 4, 5, 6, 5, 6, 5, 6, 5])
        self._check_dump_file_structure(self.dump_file)

    def test_for_else(self):
        """Fn with a for+else."""

        @record.record()
        def foo():
            x = 3
            s = 0
            for i in range(x):
                s = s + i
            else:
                ok = 1

        with mock.patch(self.record_state_fn_path) as record_mock:
            foo()

        self._check_record_calls(record_mock, [3, 4, 5, 6, 5, 6, 5, 6, 5, 8])
        self._check_dump_file_structure(self.dump_file)

    def test_nested_if_in_for(self):
        """Fn with a for containing an if."""

        @record.record()
        def foo():
            x = 3
            s = 0
            for i in range(x):
                if s > -1:
                    s += i

        with mock.patch(self.record_state_fn_path) as record_mock:
            foo()

        self._check_record_calls(record_mock, [3, 4, 5, 6, 7, 5, 6, 7, 5, 6, 7, 5])
        self._check_dump_file_structure(self.dump_file)

    def test_recursive_function(self):
        """Fn with a recursive call."""

        @record.record()
        def foo(x):
            if x == 0:
                return 1
            return 1 + foo(x - 1)

        with mock.patch(self.record_state_fn_path) as record_mock:
            foo(2)

        # Recursive calls are expanded/eval'd first, that's why 3, 3, 3.
        self._check_record_calls(record_mock, [3, 3, 3, 4, 5, 5])
        self._check_dump_file_structure(self.dump_file)

    def test_try_ok(self):
        """Fn with a try that does not raise."""

        @record.record()
        def foo():
            x = 3
            try:
                x = x + 1
            except:
                y = 2

        with mock.patch(self.record_state_fn_path) as record_mock:
            foo()

        self._check_record_calls(record_mock, [3, 4, 5])
        self._check_dump_file_structure(self.dump_file)

    def test_try_except(self):
        """Fn with a try that raises."""

        @record.record()
        def foo():
            x = 3
            try:
                x = 1 / 0
            except:
                y = 2

        with mock.patch(self.record_state_fn_path) as record_mock:
            foo()

        # `1 / 0` raises so the state is not recorded there. Jumps straight ahead to `y = 2`.
        self._check_record_calls(record_mock, [3, 4, 7])
        self._check_dump_file_structure(self.dump_file)

    def test_try_multi_except(self):
        """Fn with a try that raises and has multiple except branches."""

        @record.record()
        def foo():
            x = 3
            try:
                x = 1 / 0
            except KeyboardInterrupt:
                y = 2
            except ZeroDivisionError:
                y = 3

        with mock.patch(self.record_state_fn_path) as record_mock:
            foo()

        # `1 / 0` raises so the state is not recorded there. Jumps straight ahead to `y = 3`.
        self._check_record_calls(record_mock, [3, 4, 9])
        self._check_dump_file_structure(self.dump_file)

    def test_try_ok_else(self):
        """Fn with a try that does not raise and does something in `else`."""

        @record.record()
        def foo():
            x = 3
            try:
                x = x + 1
            except:
                y = 2
            else:
                z = 4

        with mock.patch(self.record_state_fn_path) as record_mock:
            foo()

        self._check_record_calls(record_mock, [3, 4, 5, 9])
        self._check_dump_file_structure(self.dump_file)

    def test_return_wrapping(self):
        """Fn with return has return value captured."""

        @record.record()
        def foo():
            x = 3
            return x

        with mock.patch(self.record_state_fn_path) as record_mock:
            foo()

        self._check_record_calls(record_mock, [3, 4])
        self._check_dump_file_structure(self.dump_file)

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

        with mock.patch(self.record_state_fn_path) as record_mock:
            foo()
            foo()
            foo()

        self._check_dump_file_structure(self.dump_file, 3)

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

        with mock.patch(self.record_state_fn_path) as record_mock:
            foo()
            foo()
            foo()

        self._check_dump_file_structure(self.dump_file, 2)

    def _check_record_calls(self, record_mock, expected_linenos):
        try:
            self.assertEqual(record_mock.call_count, len(expected_linenos),
                             "Wrong number of calls to record.")
            for i, lineno in enumerate(expected_linenos):
                self.assertEqual(record_mock.call_args_list[i][0][0], lineno,
                                 "Record was called with the wrong lineno.")
        except:
            # Helper for debugging.
            print "Actual calls", [record_mock.call_args_list[i][0][0] for i in range(record_mock.call_count)]
            raise

    def _check_dump_file_structure(self, dump_file, num_executions=1):
        # Rewind the file.
        dump_file.seek(0)
        lines = dump_file.readlines()

        # First line should be source.
        data = json.loads(lines[0])
        SOURCE_DUMP_SCHEMA(data)

        # Next lines should be execution dumps.
        for line in lines[1:]:
            data = json.loads(line)
            EXECUTION_DUMP_SCHEMA(data)

        self.assertEqual(len(lines) - 1, num_executions,
                         "Wrong number of executions dumped.")

    def _reset_record(self):
        """Resets `record` state as if a new program was run."""
        record.num_fns_recorded = 0
        record._record_store_hidden_123 = None
        record.first_dump_call = True
        record.num_recorded_executions = 0
