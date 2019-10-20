import os
import requests
from sys import argv
from wit import Wit
from bottle import Bottle, request, debug
import json
# Wit.ai parameters
WIT_TOKEN = os.environ.get('WIT_TOKEN') or ''
# Messenger API parameters
FB_PAGE_TOKEN = os.environ.get('FB_PAGE_TOKEN') or \
''
# A user secret to verify webhook get request.
FB_VERIFY_TOKEN = os.environ.get('FB_VERIFY_TOKEN') or ''
PORT = os.environ.get('PORT') or 5000

# Setup Bottle Server
debug(True)
app = Bottle()


# Facebook Messenger GET Webhook
@app.get('/webhook')
def messenger_webhook():
    """
    A webhook to return a challenge
    """
    verify_token = request.query.get('hub.verify_token')
    # check whether the verify tokens match
    if verify_token == FB_VERIFY_TOKEN:
        # respond with the challenge to confirm
        challenge = request.query.get('hub.challenge')
        return challenge
    else:
        return 'Invalid Request or Verification Token'


# Facebook Messenger POST Webhook
@app.post('/webhook')
def messenger_post():
    """
    Handler for webhook (currently for postback and messages)
    """
    data = request.json
    if data['object'] == 'page':
        for entry in data['entry']:
            # get all the messages
            messages = entry['messaging']
            if messages[0]:
                # Get the first message
                message = messages[0]
                # Yay! We got a new message!
                # We retrieve the Facebook user ID of the sender
                fb_id = message['sender']['id']
                # We retrieve the message content
                text = message['message']['text']
                # Let's forward the message to Wit /message
                # and customize our response to the message in handle_message
                response = client.message(msg=text, context={'session_id':fb_id})
                handle_message(response=response, fb_id=fb_id)
    else:
        # Returned another event
        return 'Received Different Event'
    return None


def fb_message(sender_id, text):
    """
    Function for returning response to messenger
    """
    data = {
        'recipient': {'id': sender_id},
        'message': {'text': text}
    }
    # Setup the query string with your PAGE TOKEN
    qs = 'access_token=' + FB_PAGE_TOKEN
    # Send POST request to messenger
    resp = requests.post('https://graph.facebook.com/me/messages?' + qs,
                         json=data)
    return resp.content


def first_entity_value(entities, entity):
    """
    Returns first entity value
    """
    if entity not in entities:
        return None
    val = entities[entity][0]['value']
    if not val:
        return None
    return val['value'] if isinstance(val, dict) else val


def first_entity_unit(entities, entity):
    """
    Returns first entity value
    """
    if entity not in entities:
        return None
    val = entities[entity][0]['unit']
    if not val:
        return None
    return val    


def handle_message(response, fb_id):
    """
    Customizes our response to the message and sends it
    """
    entities = response['entities']
    # Checks if user's message is a greeting
    # Otherwise we will just repeat what they sent us
    greetings = first_entity_value(entities, 'greetings')
    if greetings:
        text = "hello!"
    else:
        if first_entity_value(entities,'intent') == 'convert':
            amount_of_money = float(first_entity_value(entities, 'amount_of_money'))
            crypto = first_entity_value(entities, 'crypto')
            unit = first_entity_unit(entities, 'amount_of_money')  

            if (crypto is not None) and (unit is not None): 
                qs = unit+'-'+crypto
                r = requests.get('https://api.cryptonator.com/api/ticker/'+qs) 
                resp = json.loads(r.content)
                price = float(resp['ticker']['price']) 

                result = price * amount_of_money
            else:
                result = 'Couldn\'nt calculate'

        else:
            result = 'Couldn\'nt calculate'

        text = result
    # send message
    fb_message(fb_id, text)


# Setup Wit Client
client = Wit(access_token=WIT_TOKEN)

if __name__ == '__main__':
    # Run Server
    app.run(reloader=True, host='0.0.0.0', port=PORT)