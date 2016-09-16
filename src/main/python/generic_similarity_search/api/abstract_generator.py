from abc import ABCMeta

from generic_similarity_search.abstract_base_generator import AbstractBaseGenerator


class AbstractGenerator(AbstractBaseGenerator, metaclass=ABCMeta):
    """
    Base class for concrete similarity search implementations.
    """

    def needs_refresh(self):
        return False

