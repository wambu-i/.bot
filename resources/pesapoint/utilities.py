import os
import json
import base64
import requests

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

from dotenv import load_dotenv

#from ..helpers import create_logger

#logger = create_logger('pesapoint')

basedir = os.path.abspath(os.path.dirname(__file__))
env_path = os.path.join(basedir, '.env')

load_dotenv(env_path)

terminal_id = os.environ.get('terminal', '13881544')
encryption_key = os.environ.get('encryption_key', '1926566078703918')

print(terminal_id, encryption_key)

def get_encrypted_string(data):
	cipher = AES.new(str.encode(encryption_key), AES.MODE_ECB)

	print(data)
	data = data.encode('utf-8')

	text = cipher.encrypt(pad(data, 16))

	encoded = base64.b64encode(text).decode('utf-8')
	final_string = str(encoded).replace('+', '-').replace('/', '_').replace('=', ',')

	return final_string

def get_encryption_key():
	pass

def generate_session_id():
	session_id = None
	url = 'http://rshost.pesapoint.co.ke/businessclientrest/businessclientrest/'

	data = json.dumps({
		'RequestUniqueID': '5635666445675',
		'MethodName': 'DstGenerateSessionID'
	})

	cipher = get_encrypted_string(data)

	if cipher is not None:
		data = 'TerminalNumber={}&Data={}'.format(terminal_id, cipher)
		payload = {
			'TerminalNumber': terminal_id,
			'Data': cipher
		}
		#print(data)
		"""headers = {
			'Content-Type': 'application/json',
			'Accept': 'application/json',
			'Access-Control-Allow-Origin' : '*'
		}"""
		session = requests.session()
		r = session.get(url, json = payload)
		if r.status_code in [200, 201]:
			response = session.cookies.get_dict()
			session_id = response.get('PHPSESSID', None)
		else:
			logger.error('{} :{}'.format(r.status_code, r.text))

		print(session_id)
		return session_id

def get_account_balance():
	url = 'http://rshost.pesapoint.co.ke/businessclientrest/businessclientrest/'

	data = json.dumps({
		'RequestUniqueID': '147852369',
		'MethodName': 'DstGetBalance',
		'SessionID': generate_session_id()
	})

	cipher = get_encrypted_string(data)
	print(cipher)
	if cipher is not None:
		data = 'TerminalNumber={}&Data={}'.format(terminal_id, cipher)
		payload = {
			'TerminalNumber': terminal_id,
			'Data': cipher
		}
		#print(data)
		"""headers = {
			'Content-Type': 'application/json',
			'Accept': 'application/json',
			'Access-Control-Allow-Origin' : '*'
		}"""
		r = requests.get(url = url, params = data)
		print(r.url)
		print(r.status_code)

get_account_balance()