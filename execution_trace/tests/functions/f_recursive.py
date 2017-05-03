from execution_trace.record import record


@record(10)  # 1
def f(x):  # 2
    """Simple recursive function."""  # 3
    if x == 0:  # 4
        return 1  # 5

    return 1 + f(x - 1)  # 7


args = (2,)
# First is the innermost call (base case), and so on.
# x = 0, x = 1, x= 2.
expected_trace = [{u'data': [{u'lineno': 3, u'state': {u'x': u'0'}},
                             {u'lineno': 4, u'state': {u'x': u'0'}},
                             {u'lineno': 5,
                              u'state': {u'_retval_hidden_123': u'1', u'x': u'0'}}]},
                  {u'data': [{u'lineno': 3, u'state': {u'x': u'1'}},
                             {u'lineno': 4, u'state': {u'x': u'1'}},
                             {u'lineno': 7,
                              u'state': {u'_retval_hidden_123': u'2', u'x': u'1'}}]},
                  {u'data': [{u'lineno': 3, u'state': {u'x': u'2'}},
                             {u'lineno': 4, u'state': {u'x': u'2'}},
                             {u'lineno': 7,
                              u'state': {u'_retval_hidden_123': u'3', u'x': u'2'}}]}]

