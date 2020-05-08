import os

from ..helpers import create_logger

logger = create_logger('mpesa')

def authenticate():
	consumer_key = os.environ.get('key', None)
	consumer_secret = os.environ.get('secret', None)

	if consumer_key is not None and consumer_secret is not None:
		api = os.environ.get('url')
		r = requests.get(api, auth = (consumer_key, consumer_secret))
		print(r.json)
		if r.status_code in [200, 201]:
			logger.info("Successfully gotten authentication string!")
			token = r.json()['access_token']
            return token
		else:
			logger.error('{} :{}'.format(r.status_code, r.text))

	return None