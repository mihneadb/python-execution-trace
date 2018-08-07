from __future__ import print_function
from collections import defaultdict
import re

from execution_trace.record import record


@record(2)
def wordcount(text):
    words = defaultdict(int)
    for word in re.findall('\w+', text):
        words[word] += 1
    return words


if __name__ == '__main__':
    print(wordcount('Hello, world!'))
    print(wordcount('echo echo echo echo'))
