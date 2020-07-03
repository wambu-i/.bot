from pymongo import MongoClient
from urllib import parse
import os
import logging

from .helpers import create_logger

logger = create_logger('database')

class using_mongo:
	def __init__(self):
		self.db = None
		self.client = None

	def mongo_connect(self):
		try:
			pwd = os.environ.get('db_pwd', None)
			user = os.environ.get('db_user', None)
			uri = os.environ.get('db_uri', None)
			db = os.environ.get('db', None)
			uri = uri.format(user, pwd)
			self.client = MongoClient(uri)
			self.db = self.client[db]
			logger.info("Connection to database successful!")
			return self.db

		except Exception as e:
			logger.warning('Could not connect to database')
			logger.error(e, exec_info = True)
			return None

	def db_close(self):
		logger.info('Closing database worker...')
		self.client.close()

	def create_client_profile(self, id, _type, value):
		collection = self.db['profile']
		present = collection.count_documents({'_id': id})
		if present != 0:
			client = collection.find_one({'_id': id})
			if _type in client:
				v = client[_type]
				logger.info("Client already has {} {}. Replacing ...".format(_type, v))
				client[_type] = value
				collection.update_one({'_id': id},  {"$set": {_type: value}}, upsert = False)
			else:
				logger.info("Adding property {} with value {}".format(_type, value))
				collection.update_one({'_id': id},  {"$set": {_type: value}}, upsert = False)
		else:
			pass

	def get_client_profile(self, id):
		collection = self.db['profile']
		client = collection.find_one({'_id': id})

		return client

	def delete_field(self, col, id, field):
		collection = self.db[col]
		collection.update_one({'_id': id},{"$unset": {field: 1}})

	def drop_record(self, col, id):
		collection = self.db[col]
		collection.delete_one({'_id': id})

	def create_session(self, id, session):
		collection = self.db['profile']
		present = collection.count_documents({'_id': session})

		if present != 0:
			pass
		else:
			collection.insert_one({
				'_id': session,
				'user': id
			})

	def record_transaction(self, session, transaction, details):
		collection = self.db['transactions']
		present = collection.count_documents({'_id': session})

		if present != 0:
			pass
		else:
			collection.insert_one({
				'_id': session,
				'transaction': transaction,
				'details': details
			})

	def get_transaction(self, session):
		collection = self.db['transactions']
		client = collection.find_one({'_id': session})

		return client

	def insert_profile(self, search):
		collection = self.db['profile']
		collection.insert(search)

	def update_transaction(self, session, status):
		collection = self.db['bookings']
		present = collection.count_documents({'_id': session})

		if present != 0:
			pass
		else:
			collection.update_one({'_id': session},  {"$set": {'status': status}}, upsert = False)