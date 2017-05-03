from execution_trace.record import record


@record(10)  # 1
def f():  # 2
    """Fn with a simple conditional."""  # 3
    x = 3  # 4
    y = 2  # 5
    if x == 3:  # 6
        y = 5  # 7


args = ()
expected_trace = [{u'data': [{u'lineno': 3, u'state': {}},
                             {u'lineno': 4, u'state': {u'x': u'3'}},
                             {u'lineno': 5, u'state': {u'x': u'3', u'y': u'2'}},
                             {u'lineno': 6, u'state': {u'x': u'3', u'y': u'2'}},
                             {u'lineno': 7, u'state': {u'x': u'3', u'y': u'5'}}]}]
