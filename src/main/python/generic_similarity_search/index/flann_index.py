import datetime
import logging
from collections import OrderedDict

import numpy
import pyflann

from generic_similarity_search.api.index import Index
from generic_similarity_search.index.index_row import IndexRow


class FlannIndex(object):
    @staticmethod
    def to_value_array(dimensions: dict):
        """

        :param dimensions:
        :param weights:
        :returns list(double)
        """
        sorted_dict = OrderedDict(sorted(dimensions.items()))
        return numpy.array(list(sorted_dict.values()), numpy.float64)

    def __init__(self, index: Index):
        self.index = index

        dimension_values = list(map(self.to_value_array, map(lambda x: x.dimensions, index.rows)))
        m_transposed = numpy.transpose(dimension_values)

        self.meanValue = [numpy.mean(l) for l in m_transposed]
        self.stddev = [1 / e for e in [numpy.std(l) for l in m_transposed]]

        weights = {}
        for key, value in index.config.items():
            if value["index"]:
                weights[key] = value["weight"]

        self.weight = self._get_weight(self.stddev, self.to_value_array(weights))

        number_dimensions = len(weights)

        data_tmp = numpy.dot((dimension_values - numpy.matrix(self.meanValue)),
                             (numpy.eye(number_dimensions) * self.stddev))
        data = numpy.dot(data_tmp, (numpy.eye(number_dimensions) * self.weight))

        self.flann = pyflann.FLANN()
        self.params = self.flann.build_index(data, algorithm="autotuned", log_level="info",
                                             build_weight=0.0, memory_weight=0.0,
                                             target_precision=1.0, sample_fraction=1.0)
        logging.debug(self.params)

    def search(self, result_count: int, search_parameters: dict):
        """

        :param result_count: int
        :param search_parameters: dict()
        :return:
        """
        search_item = self.to_value_array(search_parameters)
        norm = numpy.dot(search_item - numpy.matrix(self.meanValue), numpy.eye(len(search_item)) * self.stddev)
        normalized_search = numpy.dot(norm, numpy.eye(len(search_item)) * self.weight)

        start = datetime.datetime.now()

        result, dists = self.flann.nn_index(normalized_search, result_count, checks=self.params["checks"])

        end = datetime.datetime.now()

        logging.debug("search took: " + str(start - end))

        return list(
            [self._build_result(dists[0][index], self.index.rows[value]) for index, value in enumerate(result[0])])

    @classmethod
    def _build_result(cls, dist: float, row: IndexRow):
        """
        Create a dict containing a result item
        :param dist:
        :param row:
        :return: dict
        """
        distance_dict = {"dist": dist}
        pass_throughs_dict = row.pass_throughs
        dimensions_dict = row.dimensions

        result_dict = distance_dict.copy()
        result_dict.update(pass_throughs_dict)
        result_dict.update(dimensions_dict)
        return result_dict

    @staticmethod
    def _get_weight(stddev, weight_delta):
        return list(map(lambda x: [numpy.sqrt(1.0 / numpy.square(x[1] * x[0]))], zip(stddev, weight_delta)))
