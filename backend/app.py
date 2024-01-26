import json
from functools import wraps

import jwt
from flask import Flask, request, current_app

from backend.models import User, AuthError

with open('../data/tickers.json', 'r') as file:
    TICKERS = json.load(file)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'this is a secret'


def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return {'message': 'Token is missing'}, 401

        try:
            # Decode JWT token
            user_data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return {'message': 'Token is expired'}, 401
        except jwt.InvalidTokenError:
            return {'message': 'Invalid token'}, 401

        # Pass the decoded user data to the function
        return f(user_data, *args, **kwargs)

    return decorated_function


def encode_jwt(token):
    return jwt.encode(token, app.config['SECRET_KEY'], algorithm='HS256')


@app.get('/predict')
def get_prediction():
    ticker = request.args.get('ticker')
    org_type = request.args.get('org_type')
    org_id = TICKERS['ticker']


@app.get('/organisations')
def get_organisations():
    org_type = request.args.get('org_type')


@app.get('/organisations/<ticker>')
def get_organisation(ticker: str):
    ...


@app.post('/login')
def login():
    user = request.json
    email = user['email']
    first_name = user['firstName']
    last_name = user['lastName']

    user_data = {'email': email, 'first_name': first_name, 'last_name': last_name}
    token = encode_jwt(user_data)

    return {
        'token': token.decode('UTF-8')
    }, 200


@app.post('/register')
def register():
    """
    Register a new user
    JSON Format:
    {
        "first_name": str
        "last_name": str
        "email": str
        "password": str
    }
    :return:
    """
    try:
        user_data = request.json
        email = user_data['email']
        password = user_data['password']
        first_name = user_data['firstName']
        last_name = user_data['lastName']

        User().create(first_name=first_name, last_name=last_name, email=email, password=password)
        token = encode_jwt({'first_name': first_name, 'last_name': last_name, 'email': email})

        return {
            'token': token.decode('UTF-8')
        }, 201
    except AuthError as e:
        return {
            'error': str(e)
        }, 401
