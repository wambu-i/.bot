import os
from datetime import datetime
from uuid import uuid4

from flask import session

from resources.models import using_mongo
from .utilities import make_response
from resources.helpers import create_logger

logger = create_logger('parsers')
confirm = 'Please confirm payment of {0} Ksh for {1}.\n1.Yes\n2.No'

options = {
	'main': {
		'1': 'airtime',
		'2': 'tokens',
		'3': 'postpaid',
		'4': 'internet',
		'5': 'ticket',
		'6': 'other'
	},
	'networks': {
		'1': 'safaricom-airtime',
		'2': 'airtel',
		'3': 'telkom'
	},
	'internet': {
		'1': 'safaricom-home',
		'2': 'zuku-home'
	},
	'other': {
		'1': 'paybill',
		'2': 'lipa'
	}
}

def is_valid_number(number):
	if len(number) != 10:
		return False
	for i in range(10):
		if not number[i].isalnum():
			return False
	return True

def is_valid_meter(number):
	if len(number) < 11:
		return False
	for i in number:
		if not i.isalnum():
			return False
	return True

def parse_response(value, user):
	db = using_mongo()
	db.mongo_connect()
	responses = db.get_client_profile(user)
	msg = None

	if 'option' not in responses:
		menu = options.get('main', None)
		db.create_client_profile(user, 'option', menu.get(value))
		msg = make_response(menu.get(value))

	elif responses['option'] == 'airtime':
		if 'network' not in responses:
			menu = options.get('networks')
			db.create_client_profile(user, 'network', menu.get(value))
			msg = make_response(menu.get(value))
		elif 'account' not in responses:
			if is_valid_number(value):
				logger.info('Buying credit for external number: {}'.format(value))
				db.create_client_profile(user, 'account', value)
				msg = make_response('topup')
			elif len(value) > 1:
				msg = make_response('no-error')
			else:
				_self = responses['user']
				db.create_client_profile(user, 'account', _self)
				msg = make_response('topup')
		elif 'amount' not in responses:
			if value.isdigit():
				db.create_client_profile(user, 'amount', float(value))
				msg = confirm.format(value, responses['network'].capitalize() + 'airtime')
			else:
				msg = make_response('amount-error')
		else:
			if value == '1':
				pass
			else:
				msg = make_response('cancel')

	elif responses['option'] == 'tokens':
		if 'account' not in responses:
			if is_valid_meter(value):
				db.create_client_profile(user, 'account', value)
				logger.info('Buying KPLC tokens for meter number {}'.format(value))
				msg = make_response('tokens-amount')
			else:
				msg = make_response('meter-error')
		elif 'amount' not in responses:
			if value.isdigit():
				db.create_client_profile(user, 'amount', float(value))
				msg = confirm.format(value, 'KPLC tokens')
		else:
			if value == '1':
				pass
			else:
				msg = make_response('cancel')

	elif responses['option'] == 'postpaid':
		if 'account' not in responses:
			if is_valid_meter(value):
				db.create_client_profile(user, 'account', value)
				logger.info('Paying KPLC postpaid for meter number {}'.format(value))
				msg = make_response('postpaid-amount')
			else:
				msg = make_response('meter-error')
		elif 'amount' not in responses:
			if value.isdigit():
				db.create_client_profile(user, 'amount', float(value))
				msg = confirm.format(value, 'KPLC postpaid')
		else:
			if value == '1':
				pass
			else:
				msg = make_response('cancel')

	elif responses['option'] == 'internet':
		if 'internet' not in responses:
			menu = options.get('internet')
			db.create_client_profile(user, 'internet', menu.get(value))
			msg = make_response(menu.get(value))
		else:
			if responses['internet'] == 'zuku':
				if 'account' not in responses:
					db.create_client_profile(user, 'account', value)
					msg = make_response('internet-amount')
				elif 'amount' not in responses:
					if value.isdigit():
						db.create_client_profile(user, 'amount', float(value))
						msg = confirm.format(value, 'Zuku Home Fibre')
					else:
						msg = make_response('amount-error')
				else:
					if value == '1':
						pass
					else:
						msg = make_response('cancel')
			else:
				if 'account' not in responses:
						db.create_client_profile(user, 'account', value)
						msg = make_response('internet-amount')
				elif 'amount' not in responses:
					if value.isdigit():
						db.create_client_profile(user, 'amount', float(value))
						msg = confirm.format(value, 'Safaricom Home Fibre')
					else:
						msg = make_response('amount-error')
				else:
					if value == '1':
						pass
					else:
						msg = make_response('cancel')

	elif responses['option'] == 'ticket':
		pass

	elif responses['option'] == 'other':
		if 'type' not in responses:
			menu = options.get('other')
			db.create_client_profile(user, 'type', menu.get(value))
			msg = make_response(menu.get(value))
		else:
			if responses['type'] == 'paybill':
				if 'account' not in responses:
					db.create_client_profile(user, 'account', value)
					msg = make_response('amount')
				elif 'amount' not in responses:
					db.create_client_profile(user, 'amount', float(value))
					msg = confirm.format(value, 'Paybill - {}'.format(responses['account']))
	else:
		pass

	db.db_close()
	return msg

