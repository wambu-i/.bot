import os
import json

from flask import Flask, request, Response, session
from twilio.twiml.messaging_response import MessagingResponse

from . import bot
from .utilities import create_logger, make_response

logger = create_logger('bot')
opt_ins = ['hi', 'hello']

@bot.route('/', methods = ['GET'])
def worker_verification():
	pass

@bot.route('/listen/', methods = ['POST'])
def worker_messaging():

	body = request.values.get('Body', None)
	obj = MessagingResponse()
	if body.lower() in opt_ins:
		response = make_response('w-greeting')
		obj.message(response)

	return str(obj)


@bot.route('/test/<id>/', methods = ['GET'])
def test_sessions(id):
	session['test'] = id

	r = Response(status = 200, mimetype = 'application/json')

	return r

@bot.route('/test/', methods = ['GET'])
def get_session():
	result = json.dumps({
		'result': str(session['test'])
	})
	r = Response(response = result, status = 500, mimetype = 'application/json')

	return r