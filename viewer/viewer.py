# Run with `python viewer.py PATH_TO_RECORD_JSON.

import json
import sys

from flask import Flask, jsonify
from flask.templating import render_template


app = Flask(__name__, template_folder='.')
# app.debug = True

# `main` inits these.
# File containing `record` output.
record_path = None
# 0: source, 1: state
record_data = []


@app.route("/")
def hello():
    return render_template('index.html')


@app.route("/source.json")
def source():
    return jsonify(record_data[0])


@app.route("/state.json")
def state():
    return jsonify(record_data[1])


def main():
    record_path = sys.argv[1]

    with open(record_path) as f:
        record_data.append(json.loads(f.readline()))
        record_data.append(json.loads(f.readline()))

    app.run()


if __name__ == "__main__":
    main()
