from execution_trace.record import record


@record(10)  # 1
def f():  # 2
    """Fn with elif."""  # 3
    x = 3  # 4
    if x == 1:  # 5
        y = 5  # 6
    elif x == 2:  # 7
        y = 6  # 8
    elif x == 3:  # 9
        y = 7  # 10


args = ()
expected_trace = [{u'data': [{u'lineno': 3, u'state': {}},
                             {u'lineno': 4, u'state': {u'x': u'3'}},
                             {u'lineno': 5, u'state': {u'x': u'3'}},
                             {u'lineno': 7, u'state': {u'x': u'3'}},
                             {u'lineno': 9, u'state': {u'x': u'3'}},
                             {u'lineno': 10, u'state': {u'x': u'3', u'y': u'7'}}]}]

