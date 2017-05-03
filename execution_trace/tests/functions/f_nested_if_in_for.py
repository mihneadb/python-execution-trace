from execution_trace.record import record


@record(10)  # 1
def f():  # 2
    """Fn with a for containing an if."""  # 3
    x = 3  # 4
    s = 0  # 5
    for i in range(x):  # 6
        if s > -1:  # 7
            s += i  # 8


expected_linenos = [3, 4, 5, 6, 7, 8, 6, 7, 8, 6, 7, 8, 6]
args = ()
expected_num_executions = 1
