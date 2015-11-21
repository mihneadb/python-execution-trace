from record import record


@record
def foo(x, y):
    a = x + y
    for i in range(a):
        x = x + 1
    c = x


if __name__ == '__main__':
    foo(2, 3)

