from execution_trace.record import record


@record(10)  # 1
def f():  # 2
    """Fn with return."""  # 3
    x = 3  # 4
    return x  # 5


expected_linenos = [3, 4, 5]
args = ()
expected_num_executions = 1
