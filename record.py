from functools import wraps
import ast
import inspect
import sys


RECORD_FN_NAME = '_record_state_fn_hidden_123'
def _record_state_fn_hidden_123(lineno, f_locals):
    print lineno, f_locals


# http://stackoverflow.com/a/12240419
# TL;DR need this because the decorator would
# recursively apply on the new generated function.
_blocked = False
def record(f):
    """Transforms `f` such that after every line record_state is called."""

    # Make sure this is not a recursive decorator application.
    global _blocked
    if _blocked:
        return f

    parsed = ast.parse(inspect.getsource(f))
    original_body = list(parsed.body[0].body)
    new_body = []

    for item in original_body:
        new_body.append(item)
        new_body.append(make_record_state_call_expr(item.lineno))

    # Update body
    parsed.body[0].body = new_body

    # Compile and inject modified function back into its env.
    new_f_compiled = compile(parsed, '<string>', 'exec')
    env = sys.modules[f.__module__].__dict__
    # We also need to inject the record_state function in there.
    env[RECORD_FN_NAME] = globals()[RECORD_FN_NAME]
    _blocked = True
    exec(new_f_compiled, env)
    _blocked = False

    return env[f.__name__]


def make_record_state_call_expr(lineno):
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

