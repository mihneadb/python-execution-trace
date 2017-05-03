from execution_trace.record import record


@record(10)  # 1
def f():  # 2
    """Fn with a for+else."""  # 3
    x = 3  # 4
    s = 0  # 5
    for i in range(x):  # 6
        s = s + i  # 7
    else:  # 8
        ok = 1  # 9


expected_linenos = [3, 4, 5, 6, 7, 6, 7, 6, 7, 6, 9]
args = ()
expected_num_executions = 1