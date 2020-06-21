import os
import json
import base64

from Crypto.Cipher import AES

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
env_path = os.path.join(basedir, '.env')

load_dotenv(env_path)

terminal_id = os.environ.get('terminal', '85681810')
encryption_key = os.environ.get('encryption_key', '5887933073555754')

print(terminal_id, encryption_key)

def get_encrypted_string():
	cipher = AES.new(str.encode(encryption_key), AES.MODE_EAX)

	data = json.dumps({
		'RequestUniqueID': '147852369',
		'MethodName': 'BscGenerateSessionID'
	})

	text, tag = cipher.encrypt_and_digest(data.encode())

	encoded = base64.b64encode(text)
	final_string = str(encoded).replace('+', '/').replace('/', '_').replace('=', ',')

	return final_string


def generate_session_id():
	url = 'http://URL-2.com/businessclientrest/businessclientrest'

get_encrypted_string()