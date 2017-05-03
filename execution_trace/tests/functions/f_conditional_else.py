from execution_trace.record import record


@record(10)  # 1
def f():  # 2
    """Fn with conditional having else."""  # 3
    x = 3  # 4
    y = 2  # 5
    if x != 3:  # 6
        y = 5  # 7
    else:  # 8
        y = 6  # 9


expected_linenos = [3, 4, 5, 6, 9]
args = ()
expected_num_executions = 1
