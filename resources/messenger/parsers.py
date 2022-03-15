import os
from datetime import datetime
from uuid import uuid4

from resources.utilities import create_logger, make_response, pass_over_control, parse_dates, send_message_replies, make_generic_message, send_carousel, take_thread_control
from resources.models.mongo import using_mongo
from resources.helpers import create_messenger_flow

logger = create_logger('parsers')
PAT = os.environ.get('PAT', None)

def create_session_id(id):
	with open('/tmp/sessions', 'w+') as store:
		store.write('{}'.format(id))
		store.close()

def get_session_id():
	id = None

	with open('/tmp/sessions', 'r') as store:
		id = store.read().strip()
		store.close()
	
	return id

def make_confirmation(id):
	logger.info('Creating confirmation text...')
	db = using_mongo()
	db.mongo_connect()
	client = db.get_client_profile(id)
	user = client['user']
	start_dt = datetime.fromtimestamp(client['start'])
	end_dt = datetime.fromtimestamp(client['end'])
	start = '{}, {} {} {}'.format(start_dt.strftime('%A'), start_dt.strftime('%d'), start_dt.strftime('%b'), start_dt.strftime('%Y'))
	end = '{}, {} {} {}'.format(end_dt.strftime('%A'), end_dt.strftime('%d'), end_dt.strftime('%b'), end_dt.strftime('%Y'))
	response = '''
Origin: {}
Destination: {}
From: {}
To: {}
Adults: {}
Children: {}
Infants: {}
	'''.format(
		client['from'].capitalize(), client['to'].capitalize(),
		start, end, client['adults'], client['child'], client['infant'])
	make_response(user, 'message', 'confirmation', PAT)
	send_message_replies(user, response, PAT)
	make_response(user, 'quick', 'details', PAT)
	db.db_close()

def send_flight_options(id):
	logger.info('Getting flight options for user...')
	print(id)
	if len(id) == 0:
		return
	db = using_mongo()
	db.mongo_connect()
	client = db.get_client_profile(id)
	db.db_close()
	if not client:
		return

	user = client['user']
	try:
		start = datetime.fromtimestamp(client['start']).strftime("%Y/%m/%d")
		end = datetime.fromtimestamp(client['end']).strftime('%Y/%m/%d')
	except KeyError:
		return
	client['start'] = start
	client['end'] = end
	logger.info(client)
	flights = create_messenger_flow(client)
	if not flights:
		make_response(user, 'quick', 'no-flights', PAT)
	else:
		logger.info(flights)
		payload = make_generic_message(flights, id)
		make_response(user, 'message', 'response', PAT)
		send_carousel(user, payload, PAT)

def process_postbacks(msg, sender_id):
    received = msg['postback']['payload']
    db = using_mongo()
    if received == 'start':
        session_id = uuid4().hex
        #create_session_id(session_id)
        
        db.mongo_connect()
        client = db.create_session(sender_id, session_id)
        make_response(sender_id, 'message', 'greeting', PAT)
        make_response(sender_id, 'quick', 'products', PAT)
        db.db_close()
    elif received.lower() == 'help':
        make_response(sender_id, 'message', 'contact', PAT)
        pass_over_control(sender_id, PAT)
    elif received.lower() == 'restart':
        session_id = uuid4().hex
        create_session_id(session_id)
        db.mongo_connect()
        client = db.create_session(sender_id, session_id)
        make_response(sender_id, 'message', 'restart', PAT)
        make_response(sender_id, 'quick', 'from', PAT)
        db.db_close()

def process_quick_replies(msg, sender_id):
    option = msg["quick_reply"]["payload"]
    db = using_mongo()
    if option.lower() == 'contact':
        make_response(sender_id, 'message', 'contact', PAT)
        pass_over_control(sender_id, PAT)
    elif option.lower() == 'flights':
        make_response(sender_id, 'quick', 'from', PAT)
    elif 'origin-' in option.lower():
        db.mongo_connect()
        origin = option.lower().split('-')
        session = get_session_id()
        db.create_client_profile(session, 'from', origin[1])
        make_response(sender_id, 'quick', 'destination', PAT)
        db.db_close()
    elif 'dest-' in option.lower():
        db.mongo_connect()
        destination = option.lower().split('-')
        session = get_session_id()
        db.create_client_profile(session, 'to', destination[1])
        make_response(sender_id, 'message', 'dates', PAT)
    elif option.lower() == 'de-correct':
        session = get_session_id()
        make_response(sender_id, 'message', 'search', PAT)
        send_flight_options(session)
    elif option.lower() == 'restart' or option.lower() == 'new-s':
        new_session = uuid4().hex
        create_session_id(new_session)
        db.mongo_connect()
        client = db.create_session(sender_id, new_session)
        make_response(sender_id, 'message', 'restart', PAT)
        make_response(sender_id, 'quick', 'from', PAT)
        db.db_close()

def process_nlp(msg, sender_id):
    option = msg['nlp']['entities']
    db = using_mongo()
    if option.get('datetime'):
        records = None
        nlp = option['datetime']
        for dt in nlp:
            tmp = dt['values']
            records = parse_dates(tmp)

        if records == None:
            make_response(sender_id, 'message', 'date-error', PAT)
        elif records == False:
            make_response(sender_id, 'message', 'end-error', PAT)
        else:
            db.mongo_connect()
            session = get_session_id()
            db.create_client_profile(session, 'start', records['start'])
            db.create_client_profile(session, 'end', records['end'])
            make_response(sender_id, 'message', 'adults', PAT)
            db.db_close()

    elif option.get('location'):
        location = None
        nlp = option['location']
        for entity in nlp:
            location = entity['value']
        db.mongo_connect()
        session = get_session_id()
        client = db.get_client_profile(session)

        if not client:
            session_id = uuid4().hex
            create_session_id(session_id)
            client = db.create_session(sender_id, session_id)

        if 'from' not in client:
            db.create_client_profile(session, 'from', location)
            make_response(sender_id, 'quick', 'destination', PAT)
        else:
            db.create_client_profile(session, 'to', location)
            make_response(sender_id, 'message', 'dates', PAT)
        db.db_close()

    elif option.get('sentiment'):
        txt = None
        no = None
        nlp = option['sentiment']
        for sentiment in nlp:
            value = sentiment['value']
            if value == 'neutral':
                txt = msg['text']
        try:
            no = int(txt)
        except ValueError:
            logger.error('Not a number... continuing.')

        if no is not None:
            session = get_session_id()
            logger.info(no)
            db.mongo_connect()
            client = db.get_client_profile(session)
            if not client:
                pass
            else:
                if 'adults' not in client:
                    db.create_client_profile(session, 'adults', no)
                    make_response(sender_id, 'message', 'children', PAT)
                elif 'child' not in client:
                    db.create_client_profile(session, 'child', no)
                    make_response(sender_id, 'message', 'infants', PAT)
                elif 'infant' not in client:
                    db.create_client_profile(session, 'infant', no)
                    make_confirmation(session)
            db.db_close()
    else:
        db.db_close()

def process_standby(message):
    for msg in message['standby']:
        if msg.get('message'):
            logger.info(msg)
            payload = msg['message']['text']
            app = msg['message'].get('app_id', None)
            if 'clearing' in payload and str(app) == os.environ.get('bot'):
                logger.info('Requesting back control...')
                recipient = msg['recipient']['id']
                take_thread_control(recipient, PAT)
            else:
                pass
        else:
            pass