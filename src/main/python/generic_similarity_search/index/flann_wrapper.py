from concurrent.futures import ThreadPoolExecutor
from time import sleep

from mock import Mock

from generic_similarity_search.api.abstract_generator import AbstractGenerator
from tornado import gen

from generic_similarity_search.index.flann_index import *
from generic_similarity_search.metric_writer import Metric

thread_pool = ThreadPoolExecutor(1)

METRIC_VALUE_NO_RELOAD = 0
METRIC_VALUE_SUCCESSFUL_RELOAD = 1
METRIC_VALUE_FAILED_RELOAD = 2


class FlannWrapper(object):
    def __init__(self, generator: AbstractGenerator, metric_namespace: str = None):
        if metric_namespace:
            self.refresh_state_metric = Metric(metric_namespace, "sos_refresh_state")
        else:
            self.refresh_state_metric = Mock()

        self.generator = generator
        self.flann_indices = {}
        self.params = None
        self.index_ready = False
        self.indexing = False

    @gen.coroutine
    def start_refresh_index_checker(self):
        yield thread_pool.submit(self.refresh_index_checker)

    def refresh_index_checker(self):
        """
        Rebuilds Flann indices if the concrete generator implementations needs_refresh() returns true
        """
        while True:
            sleep(60)
            if self.generator.needs_refresh():
                logging.info("Data has changed --> refresh indices")
                self.build_index_blocking()
            else:
                self.refresh_state_metric.write_datapoint(METRIC_VALUE_NO_RELOAD)

    def build_index_blocking(self):
        """
        Builds Flann indices as defined by the concrete generator implementation in a blocking fashion
        """
        if not self.indexing:
            try:
                self.build_flann_indices()
                self.refresh_state_metric.write_datapoint(METRIC_VALUE_SUCCESSFUL_RELOAD)
            except Exception as e:
                logging.error("Indexing failed with error: {0}".format(e))
                logging.exception(e)

                self.refresh_state_metric.write_datapoint(METRIC_VALUE_FAILED_RELOAD)
                self.indexing = False

    def build_flann_indices(self):
        """
        Return a dict of index name to real Flann index
        :return:
        """
        self.indexing = True
        indices = {}

        for name, index in self.generator.get_indices().items():
            logging.info("building new index for type %s with length: %d" % (name, len(index.rows)))
            indices[name] = FlannIndex(index)

        self.flann_indices = indices

        self.index_ready = True
        self.indexing = False

        return indices


class IndexNotReadyException(Exception):
    pass
