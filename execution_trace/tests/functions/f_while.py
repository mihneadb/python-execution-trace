from execution_trace.record import record


@record(10)  # 1
def f():  # 2
    """Fn with a while."""  # 3
    x = 3  # 4
    y = 6  # 5

    while x < y:  # 7
        x += 1  # 8


expected_linenos = [3, 4, 5, 7, 8, 7, 8, 7, 8, 7]
args = ()
expected_num_executions = 1
