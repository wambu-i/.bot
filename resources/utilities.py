import os
import sys
import json
import logging
import requests

from uuid import uuid4


FORMATTER = '[%(asctime)-15s] %(levelname)s [%(filename)s.%(funcName)s#L%(lineno)d] - %(message)s'

def create_logger(name):
	logging.basicConfig(level = logging.DEBUG, format = FORMATTER)
	logger = logging.getLogger(name)
	return logger

resp_path = os.path.abspath("responses.json")

headers = {
	'Content-Type' : 'application/json',
	'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept, x-auth'
}

TWILIO_SID = os.environ.get('sid', None)
TWILIO_AUTHTOKEN = os.environ.get('auth_token', None)
TWILIO_ENDPOINT = os.environ.get('api', None)
TWILIO_NUMBER = os.environ.get('number', None)

_CURRENT_MODULE_ = sys.modules[__name__]

logger = create_logger('utilities')

def get_response(path):
	responses = {}
	print(resp_path)
	try:
		with open(path, "r") as store:
			responses = json.load(store)
			store.close()
	except (IOError, OSError):
		return responses
	return responses

def make_response(_id, t, k, token, **kwargs):
	loaded = None
	message = None

	path = "responses.json"
	response = get_response(path)
	if response:
		loaded = response.get(k, None)
	else:
		return None
	if not loaded:
		logger.error("Could not find specified option in provided responses.")
		return None

	logger.info(graph.format(api, 'messages', token))
	handler_name = 'make_{}_replies'.format(t)
	req = 'send_{}_replies'.format(t)
	try:
		handler = getattr(_CURRENT_MODULE_, handler_name)
		message = handler(loaded)
		api_request = getattr(_CURRENT_MODULE_, req)
		if t == 'message':
			if k == 'greeting':
				msg = loaded.get('text', None) + find_user(_id, token) + '!'
				logger.info(message)
				api_request(_id, msg, token)
				api_request(_id, loaded["description"], token)
			else:
				api_request(_id, loaded.get('text', None), token)
		elif t == 'quick':
			text = loaded.get('text', None)
			api_request(_id, text, message, token)
		elif t == 'list':
			logger.info(message)
			api_request(_id, message, token)
		elif t == 'location':
			text = loaded.get('text', None)
			api_request(_id, text, message, token)
		elif t == 'number':
			text = loaded.get('text', None)
			api_request(_id, text, message, token)
		else:
			pass

	except AttributeError as e:
		logger.warning('Could not find handler for {}'.format(t))
		logger.error(e, exec_info = True)
	return True

def send_message(number, message):
	print(message)
	data = {
        "To": number,
        "From": TWILIO_NUMBER,
        "Body": message,
    }
	api = TWILIO_ENDPOINT.format(TWILIO_SID)
	r = requests.post(api, data = data, auth = (TWILIO_SID, TWILIO_AUTHTOKEN))
	
	if r.status_code in [200, 201]:
		logger.info("Successfully sent message to Twilio api!")
	else:
		logger.error('{} :{}'.format(r.status_code, r.text))

	re = r.json()
	print(re['sid'], re['status'])
