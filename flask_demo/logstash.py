import logging
import sys
from os import environ

import logstash
from flask import Flask

environ["FLASK_DEBUG"] = "1"

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

app = Flask(__name__)


@app.route('/')
def hello_world():
    log.info("This should not show up in LogStash")

    log.addHandler(logstash.TCPLogstashHandler("localhost", 50000, version=1))

    log.info("Hello from logging to logstash!")
    log.error('test logstash error message.')
    # add extra field to logstash message
    extra = {
        'test_string': 'python version: ' + repr(sys.version_info),
        'test_boolean': True,
        'test_dict': {'a': 1, 'b': 'c'},
        'test_float': 1.23,
        'test_integer': 123,
        'test_list': [1, 2, 3],
    }
    log.info('test extra fields', extra=extra)

    empty_list = []
    try:
        empty_list[1]
    except IndexError:
        log.error("err: problem finding something in an empty list")
        log.exception("exc: problem finding something in an empty list")

    return 'Hello, World!'
