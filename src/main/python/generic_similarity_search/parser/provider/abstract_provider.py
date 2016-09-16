from abc import ABCMeta, abstractmethod


class AbstractProvider(metaclass=ABCMeta):
    @abstractmethod
    def load_from_url(self, url):
        pass

    @abstractmethod
    def checksum(cls, url):
        pass
