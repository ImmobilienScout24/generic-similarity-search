from generic_similarity_search.api.abstract_generator import AbstractGenerator
from mock import Mock, patch
from tornado.web import Application
from unittest2 import TestCase

from generic_similarity_search.api.index import Index
from generic_similarity_search.index.flann_index import FlannIndex
from generic_similarity_search.index.flann_request_handler import FlannSearchHandler
from generic_similarity_search.index.flann_wrapper import FlannWrapper


class FlannSearchHandlerTests(TestCase):
    def test_transform_request_parameter_doesnt_modify_parameters_without_mapper_configured(self):
        index_config = {"my_key": {"mapper": AbstractGenerator.create_enum_mapper(["my_value_1", "my_value_2"])}}
        result_1 = FlannSearchHandler.transform_request_parameter("my_key", "my_value_1", index_config)
        self.assertEqual(0, result_1)

        result_2 = FlannSearchHandler.transform_request_parameter("my_key", "my_value_2", index_config)
        self.assertEqual(1, result_2)

    def test_transform_request_parameter_transforms_given_parameter(self):
        index_config = {"my_key": {"mapper": (lambda x: float(int(x) * 2), None)}}
        result = FlannSearchHandler.transform_request_parameter("my_key", "2", index_config)
        self.assertEqual(4, result)
        self.assertTrue(isinstance(result, float))

    @patch("generic_similarity_search.index.flann_request_handler.tornado.web.RequestHandler.flush")
    @patch("generic_similarity_search.index.flann_request_handler.tornado.web.RequestHandler.finish")
    @patch("generic_similarity_search.index.flann_request_handler.tornado.web.RequestHandler.write")
    @patch("generic_similarity_search.index.flann_request_handler.json.dumps")
    def test_transformation(self, json_mock, write_mock, finish_mock, flush_mock):
        application_mock = Mock(spec=Application)
        application_mock.ui_methods = {}
        application_mock.ui_modules = {}

        index_mock = Mock(spec=Index)
        index_mock.config = {
            "a": {"index": True, "weight": 1.0},
            "b": {"index": True, "weight": 2.0,
                  "mapper": AbstractGenerator.create_enum_mapper(["my_value_1", "my_value_2"])},
            "c": {"index": True, "weight": 3.0}
        }

        flann_index_mock = Mock(spec=FlannIndex)
        flann_index_mock.index = index_mock
        flann_index_mock.search.return_value = [{"a": 1.0, "b": 0, "c": 3.4}, {"a": 2.3, "b": 1, "c": 1.4}]

        flann_wrapper_mock = Mock(spec=FlannWrapper)
        flann_wrapper_mock.flann_indices = {"test-index": flann_index_mock}

        request_mock = Mock()
        request_mock.arguments = {"type": ["test-index"], "a": ["1"], "b": ["my_value_1"], "c": ["3"]}

        handler = FlannSearchHandler(application_mock, request_mock, flann_wrapper=flann_wrapper_mock)
        handler.get()

        # this tests the request parameter mapping transforming parameters mocked in request_mock as defined in index_mock.config
        flann_index_mock.search.assert_called_once_with(50, {'a': 1.0, 'b': 0, 'c': 3.0})

        # this tests the response mapping transforming search responses mocked with flann_index_mock as defined in index_mock.config
        json_mock.assert_called_once_with([{'a': 1.0, 'b': 'my_value_1', 'c': 3.4},
                                           {'a': 2.3, 'b': 'my_value_2', 'c': 1.4}])
