# python-execution-trace

Trace complete context of a Python function's execution.

## How to

Install the lib:

```bash
pip install execution-trace
```

Annotate the function you want to trace.

```python
from execution_trace.record import record


@record()
def foo(x, y):
    a = x + y
    return a
```

You can also record multiple executions of the function, by passing in a parameter:

```python
@record(42)
```

Run your code as you normally would. You'll get a message such as:

```
INFO:execution_trace.record:Will record execution of foo in /tmp/record_a0nQs5.json. Use `view_trace <path_to_file>` to view it.
```

View the trace using the supplied viewer:

```bash
view_trace record_a0nQs5.json
```

Go to `http://127.0.0.1:5000/`.

## Viewer

Use up/down arrow keys or the vertical scroll to step through the program's execution. Change
between function executions using the number input on the right.

Here's a GIF:

![Demo](http://i.imgur.com/HtKyNFb.gifv)

## Supported syntax

Hopefully everything:

- assignments/expressions
- if/elif/else
- while/else
- for/else
- try/except/else
- return
- recursive functions

See `tests/test_record.py`.

## Caveats

Can also trace a function at a time. No work was done to support multithreading at this point.
