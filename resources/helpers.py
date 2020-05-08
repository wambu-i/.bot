import logging

FORMATTER = '[%(asctime)-15s] %(levelname)s [%(filename)s.%(funcName)s#L%(lineno)d] - %(message)s'

def create_logger(name):
	logging.basicConfig(level = logging.DEBUG, format = FORMATTER)
	logger = logging.getLogger(name)
	return logger