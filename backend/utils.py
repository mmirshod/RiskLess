import json

import joblib
import numpy as np
import pandas as pd
import requests
from typing import List

API_URL = 'https://new-api.openinfo.uz/api/v1/reports'
ENV_MODEL = joblib.load('../models/model_v2/sk_models/env_model.pkl')
SOC_MODEL = joblib.load('../models/model_v2/sk_models/soc_model.pkl')
GOV_MODEL = joblib.load('../models/model_v2/sk_models/gov_model.pkl')

SECTOR_MAPPING = {
    'Healthcare': 0,
    'Industrials': 1,
    'Consumer': 2,
    'Technology': 3,
    'Utilities': 4,
    'Financial Services': 5,
    'Basic Materials': 6,
    'Real Estate': 7,
    'Energy': 8,
    'Communication Services': 9
}




def _get_data_from_api(api_url) -> dict or None:
    try:
        # Make a GET request to the API
        response = requests.get(api_url)
        response.raise_for_status()  # Check for errors in the response

        # Parse JSON response
        json_data = response.json()
        return json_data

    except requests.exceptions.RequestException as e:
        # Handle request errors
        print(f"Error making GET request: {e}")
        return None


def _extract_pages_tickers(data, url):
    organization_info = {}
    for result in data.get('results', []):
        organization_id = result.get('id')
        response_data = requests.get(f'{url}/{organization_id}').json()
        ticker = response_data.get('organization', {}).get('exchange_ticket_name', None)

        if organization_id and ticker:
            organization_info[ticker] = organization_id

    return organization_info


def get_tickers(org_type: str) -> None:

    all_tickers = {}
    data = _get_data_from_api(f"{API_URL}/{org_type}/annual/")

    i = 2
    while True:
        page_tickers = _extract_pages_tickers(data, url=f"{API_URL}/{org_type}/annual")
        all_tickers.update(page_tickers)

        data = _get_data_from_api(f"{API_URL}/{org_type}/annual/?page={i}")
        if not data:
            break

        i += 1

    _save_to_json(data=all_tickers, filename='../data/tickers.json')


def _save_to_json(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=2)


def preprocess(data: dict) -> dict:
    data = pd.DataFrame.from_dict({key: [value] for key, value in data.items()})
    scores: List[float] = [np.expm1(ENV_MODEL.predict(data))[0], np.expm1(SOC_MODEL.predict(data))[0], np.expm1(GOV_MODEL.predict(data))[0]]
    scores = [np.round(val, 2) if val < 10 else np.round(val, 1) for val in scores]

    prediction = {
        "env_score": scores[0],
        "soc_score": scores[1],
        "gov_score": scores[2],
    }

    return prediction


def get_annual_report(org_id: int, org_type: str) -> dict:
    resp = requests.get(f'{API_URL}/{org_type}/annual/{org_id}').json()
    balance_sheet = resp['balance_sheet_report']
    financial_report = resp['financial_results_report']
    total_operating_expenses = financial_report[15853 - 15803]['value']
    total_non_interest_expenses = financial_report[15843 - 15803]['value']
    total_interest_expenses = financial_report[]['value']
    total_interest_income = financial_report['']['value']
    total_non_interest_income = financial_report['']['value']

    data = {
        'Sector': [2.0],  # financial services,
        'Income Before Tax': [financial_report[15855 - 15803]['value']],
        'Net Income': [financial_report[15860 - 15803]['value']],
        'Selling General Administrative': [total_operating_expenses + total_non_interest_expenses],
        'Gross Profit': [financial_report[15844 - 15803]['value']],
    }





# {
#     'Sector': [2.0],
#     'Income Before Tax': [1477000000.0],
#     'Net Income': [1078000000.0],
#     'Selling General Administrative': [1525000000.0],
#     'Gross Profit': [2631000000.0],
#     'Ebit': [1074000000.0],
#     'Operating Income': [1074000000.0],
#     'Interest Expense': [-87000000.0],
#     'Income Tax Expense': [398000000.0],
#     'Total Revenue': [6642000000.0],
#     'Total Operating Expenses': [5568000000.0],
#     'Cost Of Revenue': [4011000000.0],
#     'Total Other Income Expense Net': [403000000.0],
#     'Net Income From Continuing Ops': [1079000000.0],
#     'Net Income Applicable To Common Shares': [1078000000.0]
# }



if __name__ == '__main__':
    ...