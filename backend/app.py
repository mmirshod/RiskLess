import json

from flask import Flask, request

with open('../data/tickers.json', 'r') as file:
    TICKERS = json.load(file)

app = Flask(__name__)


@app.get('/predict')
def get_prediction():
    ticker = request.args.get('ticker')
    org_type = request.args.get('org_type')
    org_id = TICKERS['ticker']



@app.get('/categories')
def get_categories():
    ...


@app.get('/organisations')
def get_organisations():
    ...


@app.get('/organisations/<ticker>')
def get_organisation(ticker: str):
    ...


@app.post('/login')
def login():
    ...


@app.post('/register')
def register():
    ...
