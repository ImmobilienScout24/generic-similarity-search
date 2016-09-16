from unittest2 import TestCase

from generic_similarity_search.index.flann_index import FlannIndex
from generic_similarity_search.test_generator import TestGenerator


class TestFlannIndex(TestCase):
    def setUp(self):
        self.indices = TestGenerator().get_indices()

    def test_generator_creates_two_indices(self):
        self.assertEqual(len(self.indices), 2)

    def test_returns_correct_results(self):
        index1 = FlannIndex(self.indices["index1"])
        result1 = index1.search(2, {"a": 5, "b": 3})
        self.assertListEqual([{'a': 4.0, 'b': 0, 'c': '6', 'dist': 9.9999999999999982},
                              {'a': 3.0, 'b': 0, 'c': '1.0', 'dist': 12.999999999999998}], result1)

        index2 = FlannIndex(self.indices["index2"])
        result2 = index2.search(2, {"a": 5, "b": 3})
        self.assertListEqual([{'c': '6', 'dist': 10.0, 'a': 2.0, 'b': 2},
                              {'c': '9.2', 'dist': 15809.489999999998, 'a': 130.7, 'b': 0}], result2)
