from generic_similarity_search.api.abstract_generator import AbstractGenerator

from generic_similarity_search.api.index import Index
from unittest2 import TestCase

from generic_similarity_search.api.row import Row
from generic_similarity_search.index.index_row import IndexRow


class IndexTests(TestCase):
    def test_append_row_handles_row_fields_as_configured(self):
        index_config = {"a": {"weight": 1, "index": True}, "b": {"index": False}}
        index = Index(index_config)
        index.append_row(Row("index", {"a": "1.0", "b": "test1"}))
        index.append_row(Row("index", {"a": 2.0, "b": "test2"}))

        index_row_1 = IndexRow(pass_throughs={"b": "test1"}, dimensions={"a": 1.0})
        index_row_2 = IndexRow(pass_throughs={"b": "test2"}, dimensions={"a": 2.0})

        self.assertEqual(2, len(index.rows))
        self.isEqualIndexRow(index_row_1, index.rows[0])
        self.isEqualIndexRow(index_row_2, index.rows[1])

    def test_append_row_mapps_values(self):
        index_config = {"a": {"weight": 1, "index": True, "mapper": AbstractGenerator.create_enum_mapper(["my_value"])}}
        index = Index(index_config)
        index.append_row(Row("index", {"a": "my_value", "b": "test1"}))

        index_row = IndexRow(pass_throughs={}, dimensions={"a": 0})

        self.assertEqual(1, len(index.rows))
        self.isEqualIndexRow(index_row, index.rows[0])

    def isEqualIndexRow(self, expected: IndexRow, actual: IndexRow):
        self.assertEqual(expected.dimensions, actual.dimensions)
        self.assertEqual(expected.pass_throughs, actual.pass_throughs)
