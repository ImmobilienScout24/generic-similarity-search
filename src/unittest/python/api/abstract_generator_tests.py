from generic_similarity_search.api.index import Index
from mock import patch, Mock, call
from unittest2 import TestCase
from generic_similarity_search.api.abstract_generator import AbstractGenerator
from generic_similarity_search.api.row import Row


class GeneratorMock(AbstractGenerator):
    def __init__(self, data_url: str, index_config: dict, parse_line_function):
        self.data_url = data_url
        self.index_config = index_config
        self.parse_line_function = parse_line_function

    def get_data_url(self):
        return self.data_url

    def get_index_config(self, dont_care_index_name):
        return self.index_config

    def parse_line(self, line):
        return self.parse_line_function(line)


class AbstractGeneratorTests(TestCase):
    @patch("generic_similarity_search.api.abstract_generator.AbstractGenerator._load_data")
    def test_get_indices_returns_index(self, load_data_mock):
        index_config = {
            "a": {"weight": 0.005, "index": True},
            "b": {"weight": 0.005, "index": True},
            "c": {"weight": 0.005, "index": True},
            "d": {"index": False}
        }

        row_1_mock = Mock(spec=Row)
        row_1_mock.index_name = "index_name"
        row_1_mock.fields = {"a": 1, "b": 2, "c": 3, "d": 2}

        row_2_mock = Mock(spec=Row)
        row_2_mock.index_name = "index_name"
        row_2_mock.fields = {"a": 4, "b": 5, "c": 6, "d": 2}

        parse_line_mock = Mock()
        parse_line_mock.side_effect = [row_1_mock, row_2_mock]
        load_data_mock.return_value = ["line_1", "line_2"]

        generator = GeneratorMock("", index_config, parse_line_mock)

        indices = generator.get_indices()
        name, index = list(indices.items())[0]

        self.assertEqual("index_name", name)
        self.assertIsInstance(index, Index)

        row1 = index.rows[0]
        row2 = index.rows[1]

        self.assertDictEqual({'b': 2, 'c': 3, 'a': 1}, row1.dimensions)
        self.assertDictEqual({'d': 2}, row1.pass_throughs)

        self.assertDictEqual({'a': 4, 'b': 5, 'c': 6}, row2.dimensions)
        self.assertDictEqual({'d': 2}, row2.pass_throughs)

        parse_line_mock.assert_has_calls([call("line_1"), call("line_2")])

    @patch("generic_similarity_search.api.abstract_generator.AbstractGenerator._load_data")
    def test_get_indices_returns_index_for_each_index_name(self, load_data_mock):
        index_config = {
            "a": {"weight": 0.005, "index": True},
            "b": {"weight": 0.005, "index": True},
            "c": {"weight": 0.005, "index": True},
            "d": {"index": False}
        }

        row_1_mock = Mock(spec=Row)
        row_1_mock.index_name = "index1"
        row_1_mock.fields = {"a": 1, "b": 2, "c": 3, "d": 2}

        row_2_mock = Mock(spec=Row)
        row_2_mock.index_name = "index2"
        row_2_mock.fields = {"a": 4, "b": 5, "c": 6, "d": 2}

        row_3_mock = Mock(spec=Row)
        row_3_mock.index_name = "index2"
        row_3_mock.fields = {"a": 1, "b": 8, "c": 2, "d": 1}

        parse_line_mock = Mock()
        parse_line_mock.side_effect = [row_1_mock, row_2_mock, row_3_mock]
        load_data_mock.return_value = ["line_1", "line_2", "line_3"]

        generator = GeneratorMock("", index_config, parse_line_mock)

        indices = generator.get_indices()

        self.assertEqual(2, len(indices.items()), "should contain two indices")

        index1 = indices["index1"]
        index2 = indices["index2"]

        self.assertIsInstance(index1, Index)
        self.assertIsInstance(index2, Index)

        self.assertEqual(1, len(index1.rows))
        self.assertEqual(2, len(index2.rows))

        parse_line_mock.assert_has_calls([call("line_1"), call("line_2"), call("line_3")])

    @patch("generic_similarity_search.api.abstract_generator.AbstractGenerator._load_data")
    def test_get_indices_executes_transformation_function_for_fields(self, load_data_mock):
        to_index_value_function_mock = Mock()
        to_index_value_function_mock.return_value = "transformed_value"
        index_config = {
            "a": {"weight": 0.005, "index": True, "mapper": (to_index_value_function_mock, None)},
            "b": {"weight": 0.005, "index": True},
            "c": {"index": False, "mapper": (to_index_value_function_mock, None)}
        }

        row_1_mock = Mock(spec=Row)
        row_1_mock.index_name = "index"
        row_1_mock.fields = {"a": 1, "b": 2, "c": "some_value"}

        parse_line_mock = Mock()
        parse_line_mock.side_effect = [row_1_mock]
        load_data_mock.return_value = ["line_1"]

        generator = GeneratorMock("", index_config, parse_line_mock)

        indices = generator.get_indices()
        index = indices["index"]

        self.assertDictEqual({'a': 'transformed_value', 'b': 2.0}, index.rows[0].dimensions)
        self.assertDictEqual({'c': 'some_value'}, index.rows[0].pass_throughs)
        self.assertCountEqual([call(1)], to_index_value_function_mock.mock_calls, "")
