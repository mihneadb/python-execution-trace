import ast
import copy
import inspect
import json
import logging
import os
import sys
import tempfile
from functools import wraps

from execution_trace.constants import RECORD_FN_NAME, RETVAL_NAME, MANGLED_FN_NAME
from execution_trace.utils import strip_indent

# Init logging.
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Will be initialized in `record`.
_record_store_hidden_123 = None
# To guard against decorating more than one function.
num_fns_recorded = 0
# To know when to print out the source code of the function.
first_dump_call = True
# To know how many executions were recorded.
num_recorded_executions = 0


def _record_state_fn_hidden_123(lineno, f_locals):
    """Stores local line data."""

    # Make sure we have just primitive types.
    f_locals = {k: repr(v) for k, v in f_locals.iteritems()}
    data = {
        'lineno': lineno,
        'state': f_locals,
    }
    _record_store_hidden_123['data'].append(data)


# http://stackoverflow.com/a/12240419
# TL;DR need this because the decorator would
# recursively apply on the new generated function.
_blocked = False
def record(num_executions=1):
    def _record(f):
        """Transforms `f` such that after every line record_state is called.

        *** HERE BE DRAGONS ***
        """
        global num_fns_recorded

        # Make sure this is not a recursive decorator application.
        global _blocked
        if _blocked:
            return f

        # We only support recording one fn's executions at the moment.
        if num_fns_recorded:
            raise ValueError('Cannot `record` more than one function at a time.')
        num_fns_recorded += 1

        source = inspect.getsource(f)
        parsed = ast.parse(strip_indent(source))
        original_body = list(parsed.body[0].body)

        # Update body
        parsed.body[0].body = _fill_body_with_record(original_body)

        # Compile and inject modified function back into its env.
        new_f_compiled = compile(parsed, '<string>', 'exec')
        env = sys.modules[f.__module__].__dict__
        # We also need to inject our stuff in there.
        env[RECORD_FN_NAME] = globals()[RECORD_FN_NAME]

        _blocked = True
        exec(new_f_compiled, env)
        _blocked = False

        # Keep a reference to the (original) mangled function, because our decorator
        # will end up replacing it with `wrapped`. Then, whenever `wrapped` ends up
        # calling the original function, it would end up calling itself, leading
        # to an infinite recursion. Thus, we keep the fn we want to call under
        # a separate key which `wrapped` can call without a problem.
        # We are doing this instead of simply changing the recorded fn's name because
        # we have to support recursive calls (which would lead to NameError if we changed
        # the fn's name).
        env[MANGLED_FN_NAME] = env[f.__name__]

        init_recorded_state()

        file, path = _get_dump_file()
        logger.info("Will record execution of %s in %s . "
                    "Use `view_trace %s` to view it.",
                    f.__name__, path, path)

        # Wrap in our own function such that we can dump the recorded state at the end.
        @wraps(f)
        def wrapped(*args, **kwargs):
            ret = env[MANGLED_FN_NAME](*args, **kwargs)

            global first_dump_call
            if first_dump_call:
                dump_fn_source(file, source)
                first_dump_call = False
            dump_recorded_state(file, num_executions)

            return ret

        return wrapped
    return _record


def _make_record_state_call_expr(lineno):
    # Create locals() call.
    name = ast.Name(ctx=ast.Load(), id='locals', lineno=0, col_offset=0)
    locals_call = ast.Call(func=name, lineno=0, col_offset=0, args=[], keywords=[])

    # Create lineno constant arg.
    num = ast.Num(n=lineno, lineno=0, col_offset=0)

    # Create record_state call.
    name = ast.Name(ctx=ast.Load(), id=RECORD_FN_NAME, lineno=0, col_offset=0)
    call = ast.Call(func=name, lineno=0, col_offset=0,
                    args=[num, locals_call],
                    keywords=[])
    expr = ast.Expr(value=call, lineno=0, col_offset=0)

    return expr


def _make_return_trace_call_exprs(item):
    # Store retval in an aux var and return that instead.
    store_name = ast.Name(ctx=ast.Store(), id=RETVAL_NAME, col_offset=0, lineno=0)
    load_name = ast.Name(ctx=ast.Load(), id=RETVAL_NAME, col_offset=0, lineno=0)

    assign = ast.Assign(col_offset=0, targets=[store_name], value=item.value, lineno=0)
    ret = ast.Return(lineno=0, value=load_name, col_offset=0)

    return [
        assign,
        _make_record_state_call_expr(item.lineno),
        ret
    ]


def _fill_body_with_record(original_body, prepend=False, lineno=None):
    """Adds a record_state call after every item in the block.

    Recursive, works for nested bodies (e.g. if statements).

    `prepend` inserts a record_state call right at the start. We need this for
    recording the state on lines introducing nested blocks (`if`, `while` etc.)
    """
    new_body = []
    if prepend:
        assert lineno is not None, "Should've called prepend with a lineno."
        new_body.append(_make_record_state_call_expr(lineno))

    for item in original_body:

        # Handle return statements separately such that we capture retval as well.
        if isinstance(item, ast.Return):
            new_body.extend(_make_return_trace_call_exprs(item))
            continue

        has_nested = False

        # Look out for nested bodies.
        if hasattr(item, 'body'):
            has_nested = True
            new_nested_body = _fill_body_with_record(item.body, prepend=True, lineno=item.lineno)
            item.body = new_nested_body

        if hasattr(item, 'orelse'):
            has_nested = True

            # Don't want to prepend call for try/except, but we want for the others.
            if isinstance(item, ast.TryExcept):
                prepend = False
            else:
                prepend = True

            # `else` does not have a lineno, using `if`'s lineno.
            new_nested_body = _fill_body_with_record(item.orelse, prepend=prepend, lineno=item.lineno)
            item.orelse = new_nested_body

        # Except blocks.
        if hasattr(item, 'handlers'):
            has_nested = True
            for handler in item.handlers:
                new_nested_body = _fill_body_with_record(handler.body, prepend=False, lineno=handler.lineno)
                handler.body = new_nested_body

        new_body.append(item)
        # Don't append a call after the end of the nested body, it's redundant.
        if not has_nested:
            new_body.append(_make_record_state_call_expr(item.lineno))

    return new_body


def _get_dump_file():
    """Returns file object and its path."""
    fd, path = tempfile.mkstemp(prefix='record_', suffix='.json')
    # Will never be `close`d because we don't know when user stops the program.
    # We'll live with this.
    file = os.fdopen(fd, 'w')
    return file, path


def init_recorded_state():
    global _record_store_hidden_123
    _record_store_hidden_123 = {
        'data': []
    }


def dump_recorded_state(file, num_executions_limit):
    global num_recorded_executions

    if num_recorded_executions < num_executions_limit:
        json.dump(_record_store_hidden_123, file)
        file.write('\n')
        num_recorded_executions += 1

    # Clear state for new run.
    init_recorded_state()


def dump_fn_source(file, source):
    data = {'source': source}
    json.dump(data, file)
    file.write('\n')
