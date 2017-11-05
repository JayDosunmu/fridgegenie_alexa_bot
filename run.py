import time
import datetime as dt
from datetime import datetime, timedelta
import decimal
import logging
import json
import random

from operator import itemgetter
import boto3

import requests
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session


'''
Good idea to use default vals in intent declaration
Useful to assign types as well
'''
REPOSITORY = 'johnwheeler/flask-ask'
ENDPOINT = 'https://api.github.com/repos/{}'.format(REPOSITORY)

app = Flask(__name__)
ask = Ask(app, '/')
logger = logging.getLogger()

db = boto3.resource('dynamodb', region_name='us-west-2', endpoint_url="http://localhost:8000")

items_table = db.Table('Items')
recipesTable = db.Table('Recipes')
ordersTable = db.Table('Orders')
donationsTable = db.Table('Donations')

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


@ask.launch
def welcome():
    num_items = items_table.item_count
    msg = render_template('welcome', num_items=num_items)
    hlp = render_template('help')
    return question(msg).reprompt(hlp)


@ask.intent("AddIntent", mapping={'item': 'Item'})
def add_item(item):
    date = (datetime.now() - timedelta(days=7)).date()
    t = int(time.mktime(date.timetuple()))
    to_add = {
        "item": item,
        "price": int(random.random() * 10),
        "expiration_date": t
    }
    session.attributes['item'] = to_add

    items_table.put_item(
        Item=to_add
    )
    message = render_template('add', item_name=item)
    session.attributes['next_prompt'] = 'expiration'

    return question(message)


@ask.intent("RemoveItemIntent", mapping={'item': 'Item'})
def remove_item(item):
    to_remove = {
        "item": item
    }
    session.attributes['item'] = to_remove

    items_table.delete_item(
        Key=to_remove
    )
    message = render_template('remove', item_name=item)

    return question(message)


@ask.intent("SingleExpireIntent", mapping={'date':'Date'})
def expiration(date):
    item = session.attributes['item']
    item['expiration_date'] = date

    items.update_item(
        Key=item
    )
    message = render_template('confirm_expiration', date=date)
    return statement(message)


@ask.intent("CheckFridgeIntent")
def checkFridge():
    pe = "#it"
    ean = {"#it": "item"}
    response = items_table.scan(
        ProjectionExpression=pe,
        ExpressionAttributeNames= ean
    )

    items = response['Items']
    print(items)


    message = render_template(
        'check_fridge',
        items=items,
        num_items=len(items),
        num_expiring=0
    )
    return statement(message)


@ask.intent("HelpIntent")
def help():
    message = render_template('help')

    return statement(message)


@ask.intent("NoIntent")
def cancel():
    message = render_template('cancel')

    return statement(message)


@ask.intent("YesIntent")
def confirm():
    message = render_template('confirm')
    if session.attributes.get('next_prompt', '') == 'expiration':
        item = session.attributes['item']
        message = render_template('expiration', item_name=item.item)

    session.attributes.pop('next_prompt', None)

    return question(message)


# @ask.intent("FairestIntent")
# def fairest():
#     message = render_template('fairest')

#     return statement(message)


@ask.intent("AnswerIntent", convert={'first': int, 'second': int, 'third': int})
def answer(first, second, third):
    winning_numbers = session.attributes['numbers']

    if [first, second, third] == winning_numbers:
        msg = render_template('win')
    else:
        msg = render_template('lose')

    return statement(msg)


if __name__ == '__main__':
    app.run(debug=True)
