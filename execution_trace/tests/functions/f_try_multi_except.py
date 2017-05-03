from execution_trace.record import record


@record(10)  # 1
def f():  # 2
    """Fn with a try that raises and has multiple except branches."""  # 3
    x = 3  # 4
    try:  # 5
        x = 1 / 0  # 6
    except KeyboardInterrupt:  # 7
        y = 2  # 8
    except ZeroDivisionError:  # 9
        y = 3  # 10


# `1 / 0` raises so the state is not recorded there. Jumps straight ahead to `y = 3`.
expected_linenos = [3, 4, 5, 10]
args = ()
expected_num_executions = 1
