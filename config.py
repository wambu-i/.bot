import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
env_path = os.path.join(basedir, '.env')

load_dotenv(env_path)

class Config(object):
	#App versions
	VERSION = os.environ.get('version')
	#SECRET_KEY = os.environ.get('session_key')
	#SESSION_TYPE = os.environ.get('session_type')

	# Database Configurations
	DB_URI = os.environ.get('uri')
	DB_PORT = os.environ.get('port')
	DB_NAME = os.environ.get('db')
	DB_USER = os.environ.get('db_user')
	DB_PWD = os.environ.get('db_pwd')

	#AEROCRS Credentials
	AERO_AUTH_ID = os.environ.get('auth_id')
	AERO_PWD = os.environ.get('auth_pwd')

	#General Configurations
	DEBUG = False
	TESTING = False

	@staticmethod
	def init_app(app):
		pass


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True

config = {
    "default": DevelopmentConfig,
    "development": DevelopmentConfig,
    "staging": StagingConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}