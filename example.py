import inspect

from record import record


def foo(x, y):
    a = x + y
    for i in range(a):
        x = x + 1
    c = x


if __name__ == '__main__':
    source = inspect.getsource(foo)
    lines = source.split('\n')[:-1]
    lines = ['%d: %s' % (i + 1, line) for i, line in enumerate(lines)]
    annotated_source = '\n'.join(lines)

    print annotated_source, '\n'

    # Not decorating the fn here because we want the `getsource`
    # call above to work for demo purposes.
    record(foo)(1, 3)
