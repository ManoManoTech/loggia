# isort: off
import mm_utils.logging_utils.structlog_utils.log  # noqa

import os

import gunicorn.app.wsgiapp
from gunicorn.app.base import Application

import logging

logger = logging.getLogger(__name__)
logging.info("Worker init")


def application(environ, start_response):
    data = b"Hello, World!\n"
    logger.info("Hello, World!")
    start_response("200 OK", [("Content-Type", "text/plain"), ("Content-Length", str(len(data)))])
    return iter([data])


class StandaloneApplication(gunicorn.app.wsgiapp.WSGIApplication):
    def __init__(self, app, options):  # noqa: ARG002
        self.options = options
        self.app_uri = app
        super().__init__()

    def load_config(self):
        Application.load_config(self)
        if self.cfg is None:
            raise ValueError("cfg is None")
        self.cfg.set("workers", int(os.getenv("GUNICORN_WORKERS", "8")))
        self.cfg.set("bind", "{}:{}".format("0.0.0.0", "8000"))  # noqa: S104

        if "GUNICORN_TIMEOUT" in os.environ:
            self.cfg.set("timeout", int(os.environ["GUNICORN_TIMEOUT"]))
        self.app_uri = "myapp.app"


def main():
    StandaloneApplication(
        "%(prog)s [OPTIONS] [APP_MODULE]",
        {
            "bind": "{}:{}".format("0.0.0.0", "8000"),  # noqa: S104
            "workers": 4,
            # "wsgi_app": "myapp.app",
        },
    ).run()


if __name__ == "__main__":
    main()
