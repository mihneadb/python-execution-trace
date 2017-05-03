from execution_trace.record import record


@record(10)  # 1
def f():  # 2
    """Fn with a simple conditional."""  # 3
    x = 3  # 4
    y = 2  # 5
    if x == 3:  # 6
        y = 5  # 7


expected_linenos = [3, 4, 5, 6, 7]
args = ()
expected_num_executions = 1
