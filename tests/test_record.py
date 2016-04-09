import unittest
import mock

import record


class TestRecord(unittest.TestCase):

    # Patch path refers to current module because the decorator injects the
    # record fn in here.
    record_state_fn_path = 'test_record.%s' % record.RECORD_FN_NAME
    dump_state_fn_path = 'record.dump_recorded_state'

    def setUp(self):
        self.dump_patcher = mock.patch(self.dump_state_fn_path)
        self.dump_mock = self.dump_patcher.start()
        self._reset_record()

    def tearDown(self):
        if self.dump_patcher:
            self.dump_patcher.stop()

    def test_simple(self):
        """Simple function, no loop, no return, no conditional."""

        @record.record
        def foo():
            x = 5
            y = 6

        with mock.patch(self.record_state_fn_path) as record_mock:
            foo()

        self._check_record_calls(record_mock, [3, 4])
        self.assertEqual(self.dump_mock.call_count, 1, "Too many calls to dump fn.")

    def test_conditional(self):
        """Fn with a simple conditional."""

        @record.record
        def foo():
            x = 3
            y = 2
            if x == 3:
                y = 5

        with mock.patch(self.record_state_fn_path) as record_mock:
            foo()

        self._check_record_calls(record_mock, [3, 4, 5, 6])
        self.assertEqual(self.dump_mock.call_count, 1, "Too many calls to dump fn.")

    def test_elif(self):
        """Fn with a simple conditional."""

        @record.record
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
        self.assertEqual(self.dump_mock.call_count, 1, "Too many calls to dump fn.")

    def test_conditional_else(self):
        """Fn with conditional having else."""

        @record.record
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
        self.assertEqual(self.dump_mock.call_count, 1, "Too many calls to dump fn.")

    def test_while(self):
        """Fn with a while."""

        @record.record
        def foo():
            x = 3
            y = 6

            while x < y:
                x += 1

        with mock.patch(self.record_state_fn_path) as record_mock:
            foo()

        self._check_record_calls(record_mock, [3, 4, 6, 7, 6, 7, 6, 7, 6])
        self.assertEqual(self.dump_mock.call_count, 1, "Too many calls to dump fn.")

    def test_for(self):
        """Fn with a for."""

        @record.record
        def foo():
            x = 3
            s = 0
            for i in range(x):
                s = s + i

        with mock.patch(self.record_state_fn_path) as record_mock:
            foo()

        self._check_record_calls(record_mock, [3, 4, 5, 6, 5, 6, 5, 6, 5])
        self.assertEqual(self.dump_mock.call_count, 1, "Too many calls to dump fn.")

    def test_for_else(self):
        """Fn with a for+else."""

        @record.record
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
        self.assertEqual(self.dump_mock.call_count, 1, "Too many calls to dump fn.")

    def test_nested_if_in_for(self):
        """Fn with a for containing an if."""

        @record.record
        def foo():
            x = 3
            s = 0
            for i in range(x):
                if s > -1:
                    s += i

        with mock.patch(self.record_state_fn_path) as record_mock:
            foo()

        self._check_record_calls(record_mock, [3, 4, 5, 6, 7, 5, 6, 7, 5, 6, 7, 5])
        self.assertEqual(self.dump_mock.call_count, 1, "Too many calls to dump fn.")

    def test_recursive_function(self):
        """Fn with a recursive call."""

        @record.record
        def foo(x):
            if x == 0:
                return 1
            return 1 + foo(x - 1)

        with mock.patch(self.record_state_fn_path) as record_mock:
            foo(2)

        # Recursive calls are expanded/eval'd first, that's why 3, 3, 3.
        self._check_record_calls(record_mock, [3, 3, 3, 4, 5, 5])
        self.assertEqual(self.dump_mock.call_count, 1, "Too many calls to dump fn.")

    def test_try_ok(self):
        """Fn with a try that does not raise."""

        @record.record
        def foo():
            x = 3
            try:
                x = x + 1
            except:
                y = 2

        with mock.patch(self.record_state_fn_path) as record_mock:
            foo()

        self._check_record_calls(record_mock, [3, 4, 5])
        self.assertEqual(self.dump_mock.call_count, 1, "Too many calls to dump fn.")

    def test_try_except(self):
        """Fn with a try that raises."""

        @record.record
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
        self.assertEqual(self.dump_mock.call_count, 1, "Too many calls to dump fn.")

    def test_try_multi_except(self):
        """Fn with a try that raises and has multiple except branches."""

        @record.record
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
        self.assertEqual(self.dump_mock.call_count, 1, "Too many calls to dump fn.")

    def test_try_ok_else(self):
        """Fn with a try that does not raise and does something in `else`."""

        @record.record
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
        self.assertEqual(self.dump_mock.call_count, 1, "Too many calls to dump fn.")

    def test_return_wrapping(self):
        """Fn with return has return value captured."""

        @record.record
        def foo():
            x = 3
            return x

        with mock.patch(self.record_state_fn_path) as record_mock:
            foo()

        self._check_record_calls(record_mock, [3, 4])
        self.assertEqual(self.dump_mock.call_count, 1, "Too many calls to dump fn.")

    def test_can_only_record_one_fn(self):
        """Decorator should not allow multi-function use."""

        @record.record
        def foo():
            return 3

        def foo2():
            return 4

        with self.assertRaises(ValueError):
            record.record(foo2)

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

    def _reset_record(self):
        """Resets `record` state as if a new program was run."""
        record.num_fns_recorded = 0
        record._record_store_hidden_123 = None
