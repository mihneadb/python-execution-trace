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


args = ()
expected_trace = [{u'data': [{u'lineno': 3, u'state': {}},
                             {u'lineno': 4, u'state': {u'x': u'3'}},
                             {u'lineno': 5, u'state': {u's': u'0', u'x': u'3'}},
                             {u'lineno': 6, u'state': {u'i': u'0', u's': u'0', u'x': u'3'}},
                             {u'lineno': 7, u'state': {u'i': u'0', u's': u'0', u'x': u'3'}},
                             {u'lineno': 6, u'state': {u'i': u'1', u's': u'0', u'x': u'3'}},
                             {u'lineno': 7, u'state': {u'i': u'1', u's': u'1', u'x': u'3'}},
                             {u'lineno': 6, u'state': {u'i': u'2', u's': u'1', u'x': u'3'}},
                             {u'lineno': 7, u'state': {u'i': u'2', u's': u'3', u'x': u'3'}},
                             {u'lineno': 6, u'state': {u'i': u'2', u's': u'3', u'x': u'3'}},
                             {u'lineno': 9,
                              u'state': {u'i': u'2', u'ok': u'1', u's': u'3', u'x': u'3'}}]}]

