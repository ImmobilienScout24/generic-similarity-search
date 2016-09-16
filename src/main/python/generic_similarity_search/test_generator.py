import os

from generic_similarity_search.api.abstract_generator import AbstractGenerator
from generic_similarity_search.api.row import Row


class TestGenerator(AbstractGenerator):
    def needs_refresh(self):
        return True

    def parse_line(self, line: str):
        fields = line.strip().split(";")

        return Row(
            index_name=fields[3],
            fields={
                "a": fields[0],
                "b": fields[1],
                "c": fields[2]
            })

    def get_index_config(self, index_name):
        config = {
            "index1": {
                "a": {"weight": 1.0, "index": True},
                "b": {"weight": 1.0, "index": True, "mapper": self.create_enum_mapper(["test1", "test2", "test3"])},
                "c": {"weight": 1.0, "index": False}
            },
            "index2": {
                "a": {"weight": 1.0, "index": True},
                "b": {"weight": 1.0, "index": True, "mapper": self.create_enum_mapper(["test1", "test2", "test3"])},
                "c": {"weight": 1.0, "index": False}
            }
        }
        return config[index_name]

    def get_data_url(self):
        return "file://" + os.path.join(os.path.join(os.path.dirname(__file__), "../../../unittest/resources/"), 'test.csv')
