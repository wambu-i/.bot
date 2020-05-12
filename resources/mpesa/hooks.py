import os
import json
import dotenv

from flask import Flask, request, Response

from . import api
from .utilities import authenticate, register_url

@api.route('/authenticate/', methods = ['GET'])
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

	r.headers = {
		'Content-Type': 'application/json',
		'Accept': 'application/json',
		'Access-Control-Allow-Origin' : '*'
	}

	return r

@api.route('/register/', methods = ['POST'])
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

	r.headers = {
		'Content-Type': 'application/json',
		'Accept': 'application/json',
		'Access-Control-Allow-Origin' : '*'
	}

	return r