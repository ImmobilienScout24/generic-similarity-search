import logging

import tornado.ioloop
import tornado.web

from generic_similarity_search import __version__
from generic_similarity_search.api.abstract_generator import AbstractGenerator
from generic_similarity_search.index.flann_request_handler import FlannSearchHandler
from generic_similarity_search.index.flann_wrapper import FlannWrapper


class StatusHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("OK")
        self.flush()
        self.finish()

    def data_received(self, chunk):
        pass


class VersionHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(__version__)
        self.flush()
        self.finish()

    def data_received(self, chunk):
        pass


class StatusControllerAccessLogFilter(logging.Filter):
    def filter(self, record):
        return not record.getMessage().startswith("200 GET /status ")


def _make_app(generator: AbstractGenerator, additional_request_handlers: list, additional_settings: dict, metric_namespace: str):
    flann_wrapper = FlannWrapper(generator, metric_namespace)
    logging.info("start reindexing")

    flann_wrapper.build_index_blocking()
    flann_wrapper.start_refresh_index_checker()
    handlers = [
                   (r"/status", StatusHandler),
                   (r"/version", VersionHandler),
                   (r"/search", FlannSearchHandler, dict(flann_wrapper=flann_wrapper))
               ] + additional_request_handlers

    return tornado.web.Application(handlers, **additional_settings)


def configure_logging():
    msg_format = '%(asctime)s %(levelname)s %(module)s: %(message)s'
    date_format = '%d.%m.%Y %H:%M:%S'

    filtering_handler = logging.StreamHandler()
    filtering_filter = StatusControllerAccessLogFilter()
    filtering_formatter = logging.Formatter(fmt=msg_format, datefmt=date_format)
    filtering_handler.addFilter(filtering_filter)
    filtering_handler.setFormatter(filtering_formatter)

    tornado_access_logger = logging.getLogger("tornado.access")
    tornado_access_logger.addHandler(filtering_handler)
    tornado_access_logger.propagate = False
    pass


def run(generator: AbstractGenerator,
        additional_request_handlers: list = None,
        additional_settings: dict = None,
        port: int = 8080,
        metric_namespace: str = None):
    if not additional_request_handlers:
        additional_request_handlers = []

    if not additional_settings:
        additional_settings = {}

    configure_logging()
    app = _make_app(generator, additional_request_handlers, additional_settings, metric_namespace)
    app.listen(port)

    logging.info("Starting application - listening on port " + str(port))
    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        logging.info("Stopping application")
        tornado.ioloop.IOLoop.instance().stop()
