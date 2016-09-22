import logging

from generic_similarity_search.server import run
from generic_similarity_search.test_generator import TestGenerator

msg_format = '%(asctime)s %(levelname)s %(module)s: %(message)s'
date_format = '%d.%m.%Y %H:%M:%S'

logging.basicConfig(format=msg_format, datefmt=date_format)
logging.getLogger().setLevel(logging.INFO)

run(TestGenerator(), port=8888)
