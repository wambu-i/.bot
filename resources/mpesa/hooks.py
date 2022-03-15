import os
import json
import dotenv

from flask import Flask, request, Response

from . import pesa
from .utilities import authenticate, register_url, transact, initiate_stk_push

@pesa.route('/authenticate/', methods = ['GET'])
def get_token():
	token = authenticate()

	if token:
		dotenv.set_key('.env', 'access', token)
		result = json.dumps({
			'result': 'Successfully obtained OAuth token from M-Pesa API.'
		})
		r = Response(response = result, status = 200, mimetype = 'application/json')
	else:
		result = json.dumps({
			'result': 'Could not obtain OAuth token from M-Pesa API.'
		})
		r = Response(response = result, status = 500, mimetype = 'application/json')

	r.headers.add('Content-Type', 'application/json')
	r.headers.add('Accept', 'application/json')
	r.headers.add('Access-Control-Allow-Origin', '*')

	return r

@pesa.route('/register/', methods = ['POST'])
def register_callback():
	registered = register_url()

	if registered:
		result = json.dumps({
			'result': 'Successfully registered callback urls.'
		})
		r = Response(response = result, status = 200, mimetype = 'application/json')
	else:
		result = json.dumps({
			'result': 'Could not register callback url.'
		})
		r = Response(response = result, status = 500, mimetype = 'application/json')

	r.headers.add('Content-Type', 'application/json')
	r.headers.add('Accept', 'application/json')
	r.headers.add('Access-Control-Allow-Origin', '*')

	return r

@pesa.route('/transact/', methods=['POST'])
def make_transaction():
	number = request.args.get('number')
	amount = request.args.get('amount')

	transaction = transact(number, amount)

	if transaction:
		result = json.dumps({
			'result': 'Successfully completed paybill simulation.'
		})
		r = Response(response = result, status = 200, mimetype = 'application/json')
	else:
		result = json.dumps({
			'result': 'Could not complete paybill simulation'
		})
		r = Response(response = result, status = 500, mimetype = 'application/json')

	r.headers.add('Content-Type', 'application/json')
	r.headers.add('Accept', 'application/json')
	r.headers.add('Access-Control-Allow-Origin', '*')

	return r

@pesa.route('/stk-confirmation/', methods = ['POST'])
def get_confirmation():
	data = request.data

	result = json.dumps({
		'C2BPaymentConfirmationResult': 'Success'
	})
	r = Response(response = result, status = 200, mimetype = 'application/json')

	r.headers.add('Content-Type', 'application/json')
	r.headers.add('Accept', 'application/json')
	r.headers.add('Access-Control-Allow-Origin', '*')

	return r

@pesa.route('/simulate/', methods = ['POST'])
def simulate_transaction():
	pass

@pesa.route('/stk/', methods = ['POST'])
def get_stk_details():
	number = request.args.get('number')
	amount = request.args.get('amount')
	description = request.args.get('description')

	result = initiate_stk_push(number, amount, description)

	if not result:
		status = json.dumps({
			'error': 'Could not successfully complete request'
		})
		r = Response(response = status, status = 500, mimetype = 'application/json')
	else:
		status = status = json.dumps({
			'success': 'Successfully sent request for processing.'
		})
		r = Response(response = status, status = 200, mimetype = 'application/json')

	r.headers.add('Content-Type', 'application/json')
	r.headers.add('Accept', 'application/json')
	r.headers.add('Access-Control-Allow-Origin', '*')

	return r