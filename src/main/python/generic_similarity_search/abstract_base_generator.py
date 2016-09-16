import importlib
from abc import ABCMeta, abstractmethod
from urllib.parse import urlparse

from generic_similarity_search.api.index import Index


class AbstractBaseGenerator(metaclass=ABCMeta):
    """
    Base class for concrete similarity search implementations.
    """

    @abstractmethod
    def needs_refresh(self):
        """
        Determine if the index should be rebuild.

        :returns: bool
        """
        pass

    @abstractmethod
    def get_data_url(self):
        """
        Gets URL to fetch data from. Currently 's3' and 'file' are supported. The data MUST be line based.

        :returns: url of type str
        """
        pass

    @abstractmethod
    def parse_line(self, line: str):
        """
        Parse a single line and return a Row object
        :param line: str
        :returns Row
        """
        pass

    @abstractmethod
    def get_index_config(self, index_name: str):
        """
        Read index config dict defining weights, mapping functions and pass_through for index row fields
        :param index_name: str
        :returns dict
        """
        pass

    @staticmethod
    def create_enum_mapper(a: list):
        """
        Returns a tuple of functions converting a given string to an index value and vice versa
        :param a: list of items to map to index_values
        :return: tuple(string_to_index_value,index_value_to_string)
        """
        return lambda value_as_string: a.index(value_as_string), lambda array_position: a[array_position]

    def get_indices(self):
        """
        Creates a dictionary containing all indices.
        :returns: dict(<index-name>, <index>)
        """
        indices = {}
        # noinspection PyTypeChecker
        for line in self._load_data(self.get_data_url()):
            row = self.parse_line(line)
            if row is None:
                continue

            index_name = row.index_name
            config = self.get_index_config(index_name)

            if index_name not in indices:
                # noinspection PyTypeChecker
                indices[index_name] = Index(config)

            indices[index_name].append_row(row)

        return indices

    @staticmethod
    def _load_data(url: str):
        """
        Load data from specified url by importing a provider implementation for the urls protocol
        (s3://foo/baa.json uses generic_similarity_search.parser.provider.implementations.s3.S3 class)
        :param url: str
        :return: utf-8 encoded raw data
        """
        protocol = urlparse(url).scheme
        protocol_import = "generic_similarity_search.parser.provider.implementations." + protocol
        try:
            provider_module = importlib.import_module(protocol_import)
            provider_class = getattr(provider_module, protocol.capitalize())
            return provider_class().load_from_url(url)
        except Exception as e:
            raise RuntimeError("Unknown provider protocol: " + protocol, e)
