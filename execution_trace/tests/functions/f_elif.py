from execution_trace.record import record


@record(10)  # 1
def f():  # 2
    """Fn with elif."""  # 3
    x = 3  # 4
    if x == 1:  # 5
        y = 5  # 6
    elif x == 2:  # 7
        y = 6  # 8
    elif x == 3:  # 9
        y = 7  # 10


expected_linenos = [3, 4, 5, 7, 9, 10]
args = ()
expected_num_executions = 1
