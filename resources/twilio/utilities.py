import os
import sys
import json
import requests

from uuid import uuid4

from resources.helpers import create_logger

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

def make_response(k, **kwargs):
	loaded = None
	message = None

	response = get_response(resp_path)
	if response:
		loaded = response.get(k, None)
	else:
		return None
	if not loaded:
		logger.error("Could not find specified option in provided responses.")
		return None

	return loaded['text']

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

def generate_user_session():
	session = uuid4().hex

	return session

def make_introduction_replies():
    pass
