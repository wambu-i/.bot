import os
import json

from flask import Flask, request, Response, session
from twilio.twiml.messaging_response import MessagingResponse

from . import bot
from .utilities import create_logger, make_response, send_message, generate_user_session
from .parsers import parse_response
from resources.models import using_mongo

logger = create_logger('bot')
opt_ins = ['hi', 'hello']
restarts = ['restart', 'home']

@bot.route('/', methods = ['GET'])
def worker_verification():
	pass

@bot.route('/listen/', methods = ['POST'])
def worker_messaging():
	number = request.values.get('From')
	body = request.values.get('Body')
	current = number.split(':')[1]

	try:
		db = using_mongo()
		db.mongo_connect()
	except Exception as e:
		logger.error(e, exec_info = True)

	obj = MessagingResponse()
	if body.lower() in opt_ins:
		user = generate_user_session()
		session[current] = user
		intro = make_response('w-greeting')
		send_message(number, make_response('w-greeting'))
		send_message(number, make_response('w-products'))
		products = make_response('home')
		obj.message(products)
		db.create_session(current, user)

	elif body.lower() in restarts:
		user = generate_user_session()
		session[current] = user
		intro = make_response('restart')
		obj.message(intro)
		db.create_session(current, user)

	else:
		id = session[current]
		resp = parse_response(body.lower(), id)
		obj.message(resp)

	if db:
		db.db_close()
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