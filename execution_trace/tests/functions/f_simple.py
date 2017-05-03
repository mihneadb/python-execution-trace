from execution_trace.record import record


@record(10)  # 1
def f():  # 2
    """Simple function, no loop, no return, no conditional."""  # 3
    x = 5  # 4
    y = 6  # 5


expected_linenos = [3, 4, 5]
args = ()
expected_num_executions = 1
