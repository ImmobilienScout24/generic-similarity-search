import json

import tornado.ioloop
import tornado.web
from tornado import gen

from generic_similarity_search.index.flann_wrapper import IndexNotReadyException


class FlannReindexHandler(tornado.web.RequestHandler):
    def initialize(self, flann_wrapper):
        self.flann_wrapper = flann_wrapper

    @tornado.web.asynchronous
    @gen.coroutine
    def get(self):
        self.flann_wrapper.reindex()

        self.set_header("Content-Type", "text/plain")
        self.write("Triggered reindexing")

        self.flush()
        self.finish()


class FlannSearchHandler(tornado.web.RequestHandler):
    def initialize(self, flann_wrapper):
        self.flann_wrapper = flann_wrapper
        self.indices = flann_wrapper.flann_indices

    def data_received(self, chunk):
        pass

    @staticmethod
    def transform_request_parameter(parameter_key: str, parameter_value: str, index_config: dict):
        to_function, _ = index_config[parameter_key].get("mapper", (float, None))
        return to_function(parameter_value)

    def get(self):
        index_type = self.get_argument("type")
        result_count = int(self.get_argument("resultCount", 50))

        index_to_use_for_request = self.indices[index_type]
        index_config = index_to_use_for_request.index.config

        search_parameters = {}
        for key, value in index_config.items():
            if value["index"]:
                search_parameters[key] = self.transform_request_parameter(key, self.get_argument(key), index_config)

        try:
            result = self.flann_wrapper.flann_indices[index_type].search(result_count, search_parameters)

            from_functions = {}
            for key, value in index_config.items():
                mapper = value.get("mapper")
                if value["index"] and mapper:
                    from_functions[key] = mapper[1]

            transformed_result = []
            for result_item in result:
                transformed_result_item = {}

                for key, value in result_item.items():
                    transformed_result_item[key] = from_functions.get(key, lambda x: x)(value)

                transformed_result.append(transformed_result_item)

            self.set_header("Content-Type", "application/json")
            self.write(str(json.dumps(transformed_result)))

        except IndexNotReadyException:
            self.set_status(503)
            self.set_header("Content-Type", "text/plain")
            self.write("index is not ready")

        self.flush()
        self.finish()
