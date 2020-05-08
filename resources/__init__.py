import sys
import os
from flask import Flask, session
from flask_cors import CORS, cross_origin
from config import Config, config
from flask_session import Session

from .twilio import bot

sess = Session()

def setup(config_name):
	application = Flask(__name__)
	application.config.from_object(config[config_name])
	config[config_name].init_app(application)
	sess.init_app(application)

	version = os.environ.get('version')
	application.register_blueprint(bot, url_prefix = '/{}/whatsapp'.format(version))
	CORS(application)
	return application