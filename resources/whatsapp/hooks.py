import os
from flask import Flask, request, Response
from datetime import datetime
from uuid import uuid4

from . import bot
from resources.utilities import create_logger

logger = create_logger('bot')

@bot.route('/', methods = ['GET'])
def worker_verification():
	pass

@bot.route('/', methods = ['POST'])
def worker_messaging():
	pass