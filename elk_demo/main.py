from os import environ
import logging
from flask import Flask

environ["FLASK_DEBUG"] = "1"

log = logging.getLogger(__name__)

app = Flask(__name__)
flask_log = app.logger


@app.route('/')
def hello_world():
    log.info("Hello from logging")
    flask_log.info("Hello from flask logger")
    return 'Hello, World!'

