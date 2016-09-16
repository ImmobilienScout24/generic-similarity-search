import logging
import boto3
import hashlib

from generic_similarity_search.parser.provider.abstract_provider import AbstractProvider

class S3(AbstractProvider):
    def load_from_url(self, url):
        return self._get_s3_stream(url)

    @classmethod
    def checksum(cls, url):
        path = cls._get_s3_path(url)
        bucket_name, prefix = path.split("/", 1)
        resource = boto3.resource('s3', 'eu-west-1')
        etags = [resource.ObjectSummary(bucket_name, key.key).e_tag for key in resource.Bucket(bucket_name).objects.filter(Prefix=prefix)]
        return hashlib.md5("".join(sorted(etags)).encode('utf-8')).hexdigest()

    @classmethod
    def _get_s3_stream(cls, url):
        path = cls._get_s3_path(url)
        bucket_name, prefix = path.split("/", 1)
        s3_bucket = boto3.resource('s3', 'eu-west-1').Bucket(bucket_name)
        logging.info("searching for files in s3 bucket: " + bucket_name + " with prefix : " + prefix)
        for key in s3_bucket.objects.filter(Prefix=prefix):
            logging.info("reading file: " + key.key)
            body = s3_bucket.Object(key.key).get()['Body']
            yield from cls._split_stream(body, 10000000)

    @staticmethod
    def _split_stream(body, read_size):
        len_new_line = len(b'\n')
        leftover = b''
        aggregated_chunk = b''
        for chunk in iter(lambda: body.read(read_size), b''):
            aggregated_chunk += chunk
            if b'\n' in aggregated_chunk:
                last_index_of_new_line = aggregated_chunk.rfind(b'\n')

                valid_utf_8 = aggregated_chunk[:last_index_of_new_line + len_new_line]
                raw_data = (leftover + valid_utf_8).decode('utf-8')
                for raw_line in raw_data.strip().split('\n'):
                    yield raw_line

                leftover = aggregated_chunk[last_index_of_new_line + len_new_line:]
                aggregated_chunk = b''
        if leftover or aggregated_chunk:
            yield (leftover + aggregated_chunk).decode('utf-8')

    @staticmethod
    def _get_s3_path(url):
        path = url.lstrip("/")
        path = path.replace("s3://", "")
        return path

