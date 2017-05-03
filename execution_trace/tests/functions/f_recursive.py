from execution_trace.record import record


@record(10)  # 1
def f(x):  # 2
    """Simple recursive function."""  # 3
    if x == 0:  # 4
        return 1  # 5

    return 1 + f(x - 1)  # 7


# first call: 3, 4 + spawn second call: 3, 4 + spawn third call: 3, 4, 5
# now return from recursive call in 2nd call - 7, return from recursive call
# in 1st call: 7
expected_linenos = [3, 4, 3, 4, 3, 4, 5, 7, 7]
args = (2,)
expected_num_executions = 3
