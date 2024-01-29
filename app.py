import json
import os
from functools import wraps

import jwt
from flask import Flask, request, abort
from dotenv import load_dotenv

if os.path.exists('.env'):
    load_dotenv('.env')

from models import AuthError, User, setup_db
from utils import *

# Generate a secure random string of length 32 (you can adjust the length as needed)
SECRET_KEY = '4fe486cdd13583e85ab2596456aae584ebc01041d92d43f4a244b82dcfe817a0'

with open('data/tickers.json', 'r') as file:
    TICKERS = json.load(file)

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

setup_db(app)


def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token: str = request.headers.get('Authorization')
        print(token)
        if not token:
            return {'message': 'Token is missing'}, 401

        try:
            # Decode JWT token
            token: str = token.split(' ')[1]
            print(token)
            user_data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return {'message': 'Token is expired'}, 401
        except jwt.InvalidTokenError as e:
            return {'message': e}, 401

        # Pass the decoded user data to the function
        return f(*args, **kwargs)

    return decorated_function


def encode_jwt(payload: dict):
    return jwt.encode(payload=payload, key=SECRET_KEY, algorithm='HS256')


@app.get('/predict')
@token_required
def get_prediction():
    ticker = request.args.get('ticker')
    org_type = request.args.get('org_type')
    org_id = TICKERS[ticker]
    annual_report = get_annual_report(org_id, org_type)
    pred_data = get_test_data(annual_report)
    pred = preprocess(pred_data)
    return pred


@app.get('/organisations')
@token_required
def get_organisations():
    org_type = request.args.get('org_type')
    organisations = get_orgs_short(org_type)
    return {
        'data': organisations
    }, 200


@app.get('/organisations/<ticker>')
@token_required
def get_organisation(ticker: str):
    try:
        data = get_orgs_long(TICKERS[ticker])
        return data, 200
    except Exception as e:
        abort(404, message='No such TICKER')


@app.get('/organisations/top_five')
@token_required
def get_top_five():
    top5 = get_top_five_util(org_ids=[val for key, val in TICKERS.items()])

    for org in top5:
        org['org_short_info'] = get_short_org_info(org_id=org['org_id'])

    return {
        'data': top5,
    }, 200


@app.post('/login')
def login():
    """
    Login function
    JSON Format:
    {
        "email": str
        "password": str
    }
    :return: JWT Token
    """
    try:
        user = User.get_by_email(request.json['email'])
        if not user:
            return {'error': 'Invalid Credentials'}, 401

        user.check_password(request.json['password'])
        token = encode_jwt({'email': user.email})

        return {
            'token': token
        }, 200
    except AuthError as e:
        return {'error': e.message}, 401
    except Exception as e:
        return {'error': str(e)}, 401


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
        "occupation": str
        "place_of_work": str
        "purpose": str
    }
    :return:
    JWT Token
    """
    try:
        user_data = request.json
        email = user_data['email']
        password = user_data['password']
        first_name = user_data['firstName']
        last_name = user_data.get('lastName', None)
        occupation = user_data.get('occupation', None)
        place_of_work = user_data.get('place_of_work', None)
        purpose = user_data.get('purpose', None)

        User.create(first_name=first_name, last_name=last_name, email=email, password=password,
                    occupation=occupation, place_of_work=place_of_work, purpose=purpose)
        token = encode_jwt({'email': email})

        return {
            'token': token
        }, 201
    except AuthError as e:
        return {
            'error': str(e)
        }, 401
    except KeyError:
        return {
            'error': 'NOT ENOUGH DATA'
        }, 401


if __name__ == '__main__':
    app.run(debug=True)
