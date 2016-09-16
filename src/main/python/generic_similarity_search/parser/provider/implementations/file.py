from generic_similarity_search.parser.provider.abstract_provider import AbstractProvider
from checksumdir import dirhash
import os
import hashlib

class File(AbstractProvider):

    def load_from_url(self, url):
        return self._get_file_stream(url.split("file://")[1])

    @staticmethod
    def _get_file_stream(url):
        print(" " + url)
        with open(url, 'r', encoding='utf-8') as raw_data:
            for raw_line in raw_data:
                yield raw_line

    @classmethod
    def checksum(cls, url):
        path = url.split("file://")[1]
        if os.path.isdir(path):
            return dirhash(path, 'md5')
        else:
            m = hashlib.md5()
            with open(path,"r",encoding='utf-8') as f:
                m.update(f.read().encode('utf-8'))
            return m.hexdigest()
