from record import record


@record
def foo(x, y):
    a = x + y
    print a


if __name__ == '__main__':
    foo(3, 5)

