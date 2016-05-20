from trace.record import record


@record
def foo(x, y):
    a = x + y
    for i in range(a):
        x = x + 1
    return x


if __name__ == '__main__':
    print foo(1, 3)
