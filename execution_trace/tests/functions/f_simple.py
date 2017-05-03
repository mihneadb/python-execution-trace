from execution_trace.record import record


@record(10)  # 1
def f():  # 2
    """Simple function, no loop, no return, no conditional."""  # 3
    x = 5  # 4
    y = 6  # 5


args = ()
expected_trace = [{u'data': [{u'lineno': 3, u'state': {}},
                             {u'lineno': 4, u'state': {u'x': u'5'}},
                             {u'lineno': 5, u'state': {u'x': u'5', u'y': u'6'}}]}]
