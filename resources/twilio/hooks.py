import os
import json
from flask import Flask, request, Response, session

from . import bot
from .utilities import create_logger

logger = create_logger('bot')

@bot.route('/', methods = ['GET'])
def worker_verification():
	pass

@bot.route('/listen/', methods = ['POST'])
def worker_messaging():
	body = request.values.get('Body', None)

	print(body)
	r = Response(status = 200, mimetype = 'application/json')

	return r


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