#! /usr/bin/env python3
import logging
import os
from argparse import ArgumentParser
from datetime import datetime
from logging.handlers import RotatingFileHandler

from flask import Flask, request
from flask_autoindex import AutoIndex

app = Flask(__name__)


@app.after_request
def after_request(response):
    """ Logging after every request. """
    logger = logging.getLogger("app.access")
    message = "%s [%s] %s %s %s %s %s %s %s" % \
              (request.remote_addr,
               datetime.utcnow().strftime("%d/%b/%Y:%H:%M:%S.%f")[:-3],
               request.method,
               request.path,
               request.scheme,
               response.status,
               response.content_length,
               request.referrer,
               request.user_agent)
    logger.info(message)

    return response


def main():
    parser = ArgumentParser("Run a flask servlet to feed out static data")
    parser.add_argument("--basedir", "-B", default="~/flask/root", help="Set base directory (default %(default)s)")
    parser.add_argument("--logdir", "-l", default="~/flask/logs", help="Set log directory (default %(default)s)")
    parser.add_argument("--port", "-P", default=8123, type=int, help="TCP port to listen on (default %(default)d)")
    args = parser.parse_args()

    basedir = os.path.abspath(os.path.expanduser(args.basedir))
    logdir = os.path.abspath(os.path.expanduser(args.logdir))

    os.makedirs(logdir, 0o755, exist_ok=True)
    logfile = os.path.join(logdir, "flask.log")

    log_handler = RotatingFileHandler(logfile, maxBytes=100 * 1000 * 1000, backupCount=10, delay=False)
    log_handler.setLevel(logging.INFO)
    log_handler.setFormatter(logging.Formatter("%(message)s"))

    access_logger = logging.getLogger("app.access")
    access_logger.propagate = False
    access_logger.setLevel(logging.INFO)
    access_logger.addHandler(log_handler)

    AutoIndex(app, browse_root=basedir)

    app.run(host="0.0.0.0", port=args.port)


if __name__ == "__main__":
    main()
