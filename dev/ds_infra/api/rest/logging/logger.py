import logging.config

from os import path


import logging


log_file_path = path.join(path.dirname(path.abspath(__file__)), 'logging.config')
logging.config.fileConfig(log_file_path)
logger = logging.getLogger('ds_rest_service')


