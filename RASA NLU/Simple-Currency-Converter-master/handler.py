from rasa_nlu.model import Interpreter
import json
from flask import Flask, request
from pymessenger.bot import Bot
import requests

app = Flask(__name__)
interpreter = Interpreter.load("./models/current/nlu")

ACCESS_TOKEN = 'EAAHHvUXK7FoBAFTzIOzQmzy6BoswIBzfCYtEbLVIeCGrR2T3SVz1mKXgZB69dEMgZCnRZBwoxOIS1R5EsEL3pHD3VPCKN5dBnFZBoNQqa2ZAEIwyPR1KtzhpwaZA0SEg7aGCzAV1Uo35xH8QCg7mujC0TqdrOYYCReN6ngTYUM6gZDZD'
VERIFY_TOKEN = 'verify'
URL = 'http://data.fixer.io/api/latest?access_key=7d4c619df1eb936b05e678b2c594f428'

bot = Bot(ACCESS_TOKEN)

def get_intent(response):
    if response.get('intent'):
        return response['intent']['name']
    return ''


def get_entity(response, entity):
    if response.get('entities'):
        entity_value = [i['value'] for i in response['entities'] if i['entity'] == entity]
        if len(entity_value) > 0:
            return entity_value[0]

    return ''        

def convert(response):
    amount = get_entity(response, 'amount')
    to_ = get_entity(response,'to').upper()
    from_ = get_entity(response, 'from').upper()
    url_response = requests.get(URL+'&symbols='+from_+','+to_)
    rates = json.loads(url_response.text)['rates']
    if float(rates[from_]) != 0 and to_ in rates and from_ in rates:
        result = float(rates[to_]) * float(amount) / float(rates[from_])
        return round(result,2)
    return 'Can not convert, please try something else!'    

@app.route('/',methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get('hub.verify_token') == VERIFY_TOKEN:
            return request.args.get('hub.challenge')
        return 'invalid token'    

    else:
        data = request.get_json()
        if data['object'] == 'page':
            for event in data['entry']:
                messaging = event['messaging']
                for message in messaging:
                    recipient_id = message['sender']['id']
                    if message['message'].get('text'):
                        text = message['message']['text']
                        response = interpreter.parse(text)
                        print(response)
                        if get_intent(response) == 'greet':
                            bot.send_text_message(recipient_id,text)

                        if get_intent(response) == 'convert':
                            bot.send_text_message(recipient_id,convert(response))



    return 'OK'


app.run(port=5000,debug=True)        