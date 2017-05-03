from execution_trace.record import record


@record(10)  # 1
def f():  # 2
    """Fn with a while."""  # 3
    x = 3  # 4
    y = 6  # 5

    while x < y:  # 7
        x += 1  # 8


args = ()
expected_trace = [{u'data': [{u'lineno': 3, u'state': {}},
                             {u'lineno': 4, u'state': {u'x': u'3'}},
                             {u'lineno': 5, u'state': {u'x': u'3', u'y': u'6'}},
                             {u'lineno': 7, u'state': {u'x': u'3', u'y': u'6'}},
                             {u'lineno': 8, u'state': {u'x': u'4', u'y': u'6'}},
                             {u'lineno': 7, u'state': {u'x': u'4', u'y': u'6'}},
                             {u'lineno': 8, u'state': {u'x': u'5', u'y': u'6'}},
                             {u'lineno': 7, u'state': {u'x': u'5', u'y': u'6'}},
                             {u'lineno': 8, u'state': {u'x': u'6', u'y': u'6'}},
                             {u'lineno': 7, u'state': {u'x': u'6', u'y': u'6'}}]}]

