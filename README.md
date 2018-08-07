# python-execution-trace [![Build Status](https://travis-ci.org/mihneadb/python-execution-trace.svg?branch=add-travis)](https://travis-ci.org/mihneadb/python-execution-trace)

Trace the local context of a Python function's execution. You can step through any function's execution,
viewing the values of all local variables at every step.

![demo](http://i.imgur.com/zdmeBt4.gif)

All this by just adding a decorator to your function!


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
INFO:execution_trace.record:Will record execution of foo in /tmp/record_a0nQs5.json . Use `view_trace /tmp/record_a0nQs5.json` to view it.
```

View the trace using the supplied viewer:

```bash
view_trace /tmp/record_a0nQs5.json
```

Go to `http://127.0.0.1:5000/`.


## Viewer

Use the up/down arrow keys or the vertical scroll to step through the program's execution. Change
between function executions using the number input on the right.


## Supported syntax

Hopefully everything:

- assignments/expressions
- if/elif/else
- while/else
- for/else
- try/except/else
- return
- recursive functions

See `execution_trace/tests/functions/`.


## Performance

No need to worry about performance - the instrumentation overhead is present
only for the number of executions that you want recorded. Once the data was
gathered, only the original version of your code is run.


## Caveats

Can only trace a function at a time.

No work was done to support multithreading at this point.
