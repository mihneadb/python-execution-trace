from record import record


@record
def foo(x, y):
    a = x + y
    b = x + 2
    c = y + 2


if __name__ == '__main__':
    foo(3, 5)

