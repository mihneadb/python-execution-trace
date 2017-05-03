from execution_trace.record import record


@record(10)  # 1
def f():  # 2
    """Fn with return."""  # 3
    x = 3  # 4
    return x  # 5


args = ()
expected_trace = [{u'data': [{u'lineno': 3, u'state': {}},
                             {u'lineno': 4, u'state': {u'x': u'3'}},
                             {u'lineno': 5,
                              u'state': {u'_retval_hidden_123': u'3', u'x': u'3'}}]}]
