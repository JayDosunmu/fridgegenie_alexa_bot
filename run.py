import logging
from operator import itemgetter
import boto3

import requests
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session

from random import randint

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

@ask.launch
def welcome():
    welcome_msg = render_template('welcome')

    return question(welcome_msg)


@ask.intent("YesIntent")
def next_round():
    numbers = [randint(0, 9) for _ in range(3)]
    round_msg = render_template('round', numbers=numbers)
    session.attributes['numbers'] = numbers[::-1]  # reverse

    return question(round_msg)

@ask.intent("FairestIntent")
def fairest():
    message = render_template('fairest')

    return statement(message)


@ask.intent("AnswerIntent", convert={'first': int, 'second': int, 'third': int})
def answer(first, second, third):
    winning_numbers = session.attributes['numbers']

    if [first, second, third] == winning_numbers:
        msg = render_template('win')
    else:
        msg = render_template('lose')

    return statement(msg)


@ask.intent("StatsIntent")
def stats():
    r = requests.get(ENDPOINT)
    repo_json = r.json()

    if r.status_code == 200:
        repo_name = ENDPOINT.split('/')[-1]
        keys = ['stargazers_count', 'subscribers_count', 'forks_count']
        stars, watchers, forks = itemgetter(*keys)(repo_json)
        speech = "{} has {} stars, {} watchers, and {} forks. " \
            .format(repo_name, stars, watchers, forks)
    else:
        message = repo_json['message']
        speech = "There was a problem calling the GitHub API: {}.".format(message)

    logger.info('speech = {}'.format(speech))
    return statement(speech)


if __name__ == '__main__':

    app.run(debug=True)
