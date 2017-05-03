from execution_trace.record import record


@record(10)  # 1
def f():  # 2
    """Fn with a try that does not raise and does something in `else`."""  # 3
    x = 3  # 4
    try:  # 5
        x = x + 1  # 6
    except:  # 7
        y = 2  # 8
    else:  # 9
        z = 4  # 10


expected_linenos = [3, 4, 5, 6, 10]
args = ()
expected_num_executions = 1
