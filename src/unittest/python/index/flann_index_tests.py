import numpy
from unittest2 import TestCase

from generic_similarity_search.index.flann_index import FlannIndex


class FlannIndexTests(TestCase):
    def test_to_value_array_properly_sorts_dict(self):
        result = FlannIndex.to_value_array({"b": 2.0, "a": 1.2})
        self.assertListEqual([1.2, 2.0], list(result))

    def test_get_weight(self):
        stddev = 5
        weight = 10

        expected = [numpy.sqrt(1.0 / numpy.square(weight * stddev))]

        result = FlannIndex._get_weight([stddev], [weight])
        self.assertEqual([expected], result)

    def test_get_weight_for_multiple_values(self):
        stddev = [5, 2, 3]
        weight = [10, 5, 1]

        result1 = [numpy.sqrt(1.0 / numpy.square(weight[0] * stddev[0]))]
        result2 = [numpy.sqrt(1.0 / numpy.square(weight[1] * stddev[1]))]
        result3 = [numpy.sqrt(1.0 / numpy.square(weight[2] * stddev[2]))]

        result = FlannIndex._get_weight(stddev, weight)
        self.assertListEqual([result1, result2, result3], result)
