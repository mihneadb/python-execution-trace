from execution_trace.record import record


@record(10)  # 1
def f():  # 2
    """Fn with a try that raises."""  # 3
    x = 3  # 4
    try:  # 5
        x = 1 / 0  # 6
    except:  # 7
        y = 2  # 8


# `1 / 0` raises so the state is not recorded there. Jumps straight ahead to `y = 2`.
expected_linenos = [3, 4, 5, 8]
args = ()
expected_num_executions = 1
