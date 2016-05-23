# Run with `python viewer.py PATH_TO_RECORD_JSON.

import json
import os
import sys

from flask import Flask, jsonify
from flask.helpers import send_from_directory


app = Flask(__name__)
viewer_root = os.path.abspath(os.path.dirname(__file__))

# `main` inits these.
# File containing `record` output.
record_path = None
# 0 is source, 1:N is state
record_data = []


@app.route("/")
def hello():
    return send_from_directory(viewer_root, 'index.html')


@app.route("/source.json")
def source():
    return jsonify(record_data[0])


@app.route("/state.json")
def state():
    return jsonify({'data': record_data[1:]})


def read_record_data(f):
    record_data.append(json.loads(f.readline()))
    for line in f:
        record_data.append(json.loads(line))


def main():
    record_path = sys.argv[1]

    with open(record_path) as f:
        try:
            read_record_data(f)
        except ValueError:
            print("Record file empty. Was the recorded function called?")
            sys.exit(1)

    debug = __name__ == '__main__'
    app.run(debug=debug)


if __name__ == "__main__":
    main()
