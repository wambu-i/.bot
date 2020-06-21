import os
import requests

from ..helpers import create_logger

logger = create_logger('mpesa')

def authenticate():
	consumer_key = os.environ.get('key', None)
	consumer_secret = os.environ.get('secret', None)

	if consumer_key is not None and consumer_secret is not None:
		api = os.environ.get('auth_url')
		r = requests.get(api, auth = (consumer_key, consumer_secret))
		if r.status_code in [200, 201]:
			logger.info('Successfully gotten authentication string!')
			token = r.json()['access_token']
			return token
		else:
			logger.error('{} :{}'.format(r.status_code, r.text))

	return None

def register_url():
	access_token = os.environ.get('access')
	url = 'https://sandbox.safaricom.co.ke/mpesa/c2b/v1/registerurl'

	print(access_token)
	headers = {
		'Authorization': 'Bearer {}'.format(access_token),
		'Content-Type': 'application/json',
	}

	data = {
		'ShortCode': os.environ.get('short_code'),
		'ResponseType': 'Completed',
		'ConfirmationURL': os.environ.get('confirmation'),
		'ValidationURL': os.environ.get('validation'),
	}

	r = requests.post(url, json = data, headers = headers)

	if r.status_code in [200, 201]:
		logger.info('Successfully registered callback URL')
		response = r.json()
		if response['ResponseDescription'] == 'success':
			return True
		else:
			return False
	else:
		logger.error('{} :{}'.format(r.status_code, r.text))

	return None

def transact(number, amount):
	access_token = os.environ.get('access', None)
	print(access_token)
	url = os.environ.get('simulate')
	headers = {
		'Authorization': 'Bearer {}'.format(access_token),
		'Content-Type': 'application/json',
	}

	data = {
		'ShortCode': os.environ.get('short_code'),
		'CommandID': 'CustomerPayBillOnline',
		'Amount': float(amount),
		'Msisdn': number,
		'BillRefNumber': 'account',
		#'AccountReference': 'test'
	}

	r = requests.post(url, json = data, headers = headers)

	if r.status_code in [200, 201]:
		logger.info('Transaction successfully carried out.')
		response = r.json()
		print(response)
		if len(response['ResponseDescription']) > 0 and len(response['ConversationID']) > 0:
			return True
		else:
			return False
	else:
		logger.error('{} :{}'.format(r.status_code, r.text))

	return None

def simulate():
	access_token = os.environ.get('access', None)

	headers = {
		'Authorization': 'Bearer {}'.format(access_token),
		'Content-Type': 'application/json'
	}

	data = {
		'ShortCode': os.environ.get('short_code'),
		'CommandID': 'CustomerPayBillOnline',
		'Amount': amount,
		'Msisdn': number,
		'BillRefNumber': ' '
	}