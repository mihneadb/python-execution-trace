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


args = ()
expected_trace = [{u'data': [{u'lineno': 3, u'state': {}},
                             {u'lineno': 4, u'state': {u'x': u'3'}},
                             {u'lineno': 5, u'state': {u'x': u'3'}},
                             {u'lineno': 6, u'state': {u'x': u'4'}},
                             {u'lineno': 10, u'state': {u'x': u'4', u'z': u'4'}}]}]

