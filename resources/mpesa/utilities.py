import os
import requests
import base64

from datetime import datetime

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
		'ConfirmationURL': os.environ.get('confirmation').format(os.environ.get('version')),
		'ValidationURL': os.environ.get('validation').format(os.environ.get('version')),
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
		'AccountReference': 'test'
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

def generate_pass_code():
	dt = datetime.now()
	timestamp = '{:%Y%m%d%I%M%S}'.format(dt)
	string = '{}{}{}'.format(os.environ.get('lipa_code'), os.environ.get('pass_key'), timestamp)
	pass_code = base64.b64encode(string.encode())

	return pass_code, timestamp

def initiate_stk_push(number, amount, description):
	url = os.environ.get('stk')
	access_token = os.environ.get('access', None)

	headers = {
		'Authorization': 'Bearer {}'.format(access_token),
		'Content-Type': 'application/json'
	}

	passkey, timestamp = generate_pass_code()

	print(passkey)

	data = {
		'BusinessShortCode': os.environ.get('lipa_code'),
		'Password': passkey.decode('utf-8'),
		'Timestamp': timestamp,
		'TransactionType': 'CustomerPayBillOnline',
		'Amount': float(amount),
		'PartyA': number,
		'PartyB': os.environ.get('lipa_code'),
		'PhoneNumber': number,
		'CallBackURL': 'https://1ecd9a812cbd.ngrok.io/v1/api/stk-confirmation/',
		'AccountReference': number,
		'TransactionDesc': description
	}

	r = requests.post(url, json = data, headers = headers)
	if r.status_code in [200, 201]:
		logger.info('Transaction successfully carried out.')
		response = r.json()
		print(response)
		if response['ResponseCode'] == '0':
			return response['CheckoutRequestID']
		else:
			return False

	else:
		logger.error('{} :{}'.format(r.status_code, r.text))

def query_transaction_status(id):
	url = 'https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query'

	access_token = os.environ.get('access', None)

	headers = {
		'Authorization': 'Bearer {}'.format(access_token),
		'Content-Type': 'application/json'
	}

	passkey, timestamp = generate_pass_code()

	print(passkey)

	data = {
		'BusinessShortCode': os.environ.get('lipa_code'),
		'Password': passkey.decode('utf-8'),
		'Timestamp': timestamp,
		'CheckoutRequestID': id
	}

	r = requests.post(url, json = data, headers = headers)
	if r.status_code in [200, 201]:
		logger.info('Transaction successfully carried out.')
		response = r.json()
		print(response)
		if response['ResponseCode'] == '0':
			return True
		else:
			return False

	else:
		logger.error('{} :{}'.format(r.status_code, r.text))