import os
import json
import base64
import random
import requests
import string

from Crypto.Cipher import AES
#from Crypto.Util.Padding import pad

from dotenv import load_dotenv
import logging

FORMATTER = '[%(asctime)-15s] %(levelname)s [%(filename)s.%(funcName)s#L%(lineno)d] - %(message)s'

def create_logger(name):
	logging.basicConfig(level = logging.DEBUG, format = FORMATTER)
	logger = logging.getLogger(name)
	return logger

#from ..helpers import create_logger

logger = create_logger('pesapoint')

basedir = os.path.abspath(os.path.dirname(__file__))
env_path = os.path.join(basedir, '.env')

load_dotenv(env_path)

terminal_id = os.environ.get('terminal', '15861621')
encryption_key = os.environ.get('encryption_key', '7482308144929650')
transaction_key = os.environ.get('transaction_key', '1157699726')
bs = 16

print(terminal_id, encryption_key)

def generate_request_id():
	min = pow(10, 8)
	max = pow(10, 9) - 1
	return random.randint(min, max)

def pad(s):
    return s + (bs - len(s) % bs) * chr(bs - len(s) % bs)

def unpad(s):
	#data[:-data[-1]]
    return s[:-s[-1]]

def get_encrypted_string(data):
	cipher = AES.new(str.encode(encryption_key), AES.MODE_ECB)

	print(len(data))

	if (len(data) % 16 == 0):
		raw = data.encode('utf-8')
	else:
		raw = pad(data).encode('utf-8')
	print(len(data))
	text = cipher.encrypt(raw)

	encoded = base64.b64encode(text).decode('utf-8')
	final_string = str(encoded).replace('+', '-').replace('/', '_').replace('=', ',')

	return final_string

def get_decrypted_string(data):
	true_string = data.replace('-', '+').replace('_', '/').replace(',', '=')
	decoded = base64.b64decode(true_string)

	cipher = AES.new(str.encode(encryption_key), AES.MODE_ECB)

	text = cipher.decrypt(decoded)
	print(text)
	return text.decode('utf-8').rstrip(string.whitespace)
	#return text.decode('utf-8').strip()

def generate_session_id():
	session_id = None
	url = 'http://rsadmin.pesapoint.co.ke/distributormobilerest/distributormobilerest/'

	request = str(generate_request_id())
	data = '{"function":"DstGenerateSessionID","RequestUniqueID":' + request + ',"MethodName":"DstGenerateSessionID"}'

	cipher = get_encrypted_string(data)
	decrypt = get_decrypted_string(cipher)

	if cipher is not None:
		data = 'TerminalNumber={}&Data={}'.format(int(terminal_id), cipher)
		payload = {
			'TerminalNumber': terminal_id,
			'Data': cipher
		}
		#print(data)
		'''headers = {
			'Content-Type': 'application/json',
			'Accept': 'application/json',
			'Access-Control-Allow-Origin' : '*'
		}'''
		#session = requests.session()
		r = requests.post(url, data = data)

		if r.status_code in [200, 201]:
			response = r.json()
			encrypted = response.get('Data', None)
			if encrypted:
				decrypted = json.loads(get_decrypted_string(encrypted))
				status = decrypted.get('ResponseCode')
				if status == '000':
					return True, decrypted['SessionID']
				else:
					logger.error('{}: {}'.format(status, decrypted['ResponseDescription']))
					return False, decrypted['ResponseDescription']
		else:
			logger.error('{} :{}'.format(r.status_code, r.text))
			return False, False

def get_account_balance(sess):
	url = 'http://rsadmin.pesapoint.co.ke/distributormobilerest/distributormobilerest/'

	request = str(generate_request_id())
	data = '{"function":"DstGenerateSessionID","RequestUniqueID":' + request + ',"MethodName":"DstGetBalance","SessionID": "' + sess + '"}'
	print(data)

	cipher = get_encrypted_string(data)
	decrypt = get_decrypted_string(cipher)
	print(decrypt)
	if cipher is not None:
		data = 'TerminalNumber={}&Data={}'.format(terminal_id, cipher)
		payload = {
			'TerminalNumber': terminal_id,
			'Data': cipher
		}
		#print(data)
		'''headers = {
			'Content-Type': 'application/json',
			'Accept': 'application/json',
			'Access-Control-Allow-Origin' : '*'
		}'''
		r = requests.post(url = url, data = data)

		if r.status_code in [200, 201]:
			response = r.json()
			#print(response)
			encrypted = response.get('Data', None)
			if encrypted:
				decrypted = json.loads(get_decrypted_string(encrypted))
				status = decrypted.get('ResponseCode')
				if status == '000':
					return True, decrypted['Balance']
				else:
					logger.error('{}: {}'.format(status, decrypted['ResponseDescription']))
					return False, decrypted['ResponseDescription']
		else:
			logger.error('{} :{}'.format(r.status_code, r.text))
			return False, False

def get_product_functions(sess):
	url = 'http://rsadmin.pesapoint.co.ke/productrest/productrest/'
	request = str(generate_request_id())

	data = '"SessionID": "' + sess + '","RequestUniqueID":"' + request + '","SystemServiceID":"258987","MethodName":"BillpayProductDetails","function":"BillpayProductDetails"}'
	cipher = get_encrypted_string(data)
	decrypt = get_decrypted_string(cipher)
	print(decrypt)

	if cipher is not None:
		data = 'TerminalNumber={}&TransactionKey={}&Data={}'.format(terminal_id, transaction_key, cipher)

		'''headers = {
			'Content-Type': 'application/json',
			'Accept': 'application/json',
			'Access-Control-Allow-Origin' : '*'
		}'''
		r = requests.post(url = url, data = data)

		if r.status_code in [200, 201]:
			response = r.text
			print(response)
			""" encrypted = response.get('Data', None)
			if encrypted:
				decrypted = json.loads(get_decrypted_string(encrypted))
				status = decrypted.get('ResponseCode')
				if status == '000':
					return True, decrypted['Balance']
				else:
					logger.error('{}: {}'.format(status, decrypted['ResponseDescription']))
					return False, decrypted['ResponseDescription'] """
		else:
			logger.error('{} :{}'.format(r.status_code, r.text))
			return False, False

get_product_functions('b2aa5e9f-ef18-46ad-ba06-1f7ebbc3be03')