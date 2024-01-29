import joblib
import numpy as np
import pandas as pd
import requests
from typing import List

ENV_MODEL = joblib.load('models/model_v2/sk_models/env_model.pkl')
SOC_MODEL = joblib.load('models/model_v2/sk_models/soc_model.pkl')
GOV_MODEL = joblib.load('models/model_v2/sk_models/gov_model.pkl')

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

NAME_SUFFIX_IDS = {
    'bank': 5,
}

REPORTS_API_URL = '<REPORTS_API_URL>'  # Unfortuantely we were asked to hide api urls
ORGS_API_URL = 'ORGS_API_URL'


def get_top_five_util(org_ids: list) -> list:
    net_profits: List[dict[str: float or int]] = []

    for org_id in org_ids:
        resp = requests.get(f"{REPORTS_API_URL}/financial_indicators?organization_id={org_id}").json()
        net_profits.append({
            'org_id': org_id,
            'net_profit': resp['results'][-1]['net_profit']
        })

    net_profits = sorted(net_profits, key=lambda x: x['net_profit'], reverse=True)
    return net_profits[:5]


def preprocess(data: dict) -> dict:
    data = pd.DataFrame(data)

    scores: List[float] = [np.expm1(ENV_MODEL.predict(data)[0]), np.expm1(SOC_MODEL.predict(data)[0]), np.expm1(GOV_MODEL.predict(data))[0]]
    scores = [np.round(val, 2) if val < 10 else np.round(val, 1) for val in scores]

    prediction = {
        "env_score": scores[0],
        "soc_score": scores[1],
        "gov_score": scores[2],
    }

    return prediction


def get_annual_report(org_id: int, org_type: str) -> dict:
    resp = requests.get(f'{REPORTS_API_URL}/{org_type}/annual?page_size=500').json()
    report_id = None

    for org in resp['results']:
        if org['organization'] == org_id:
            report_id = org['id']
            break

    if report_id:
        return requests.get(f'{REPORTS_API_URL}/{org_type}/annual/{report_id}').json()


def get_test_data(json_data):
    financial_report = json_data['financial_results_report']
    total_operating_expenses = float(financial_report[15853 - 15803]['value'])
    total_non_interest_expenses = float(financial_report[15843 - 15803]['value'])
    total_interest_expenses = float(financial_report[15826 - 15803]['value'])

    data = {
        'Sector': [2.0],  # financial services,
        'Income Before Tax': [float(financial_report[15855 - 15803]['value'])],
        'Net Income': [float(financial_report[15860 - 15803]['value'])],
        'Selling General Administrative': [float(total_operating_expenses) + float(total_non_interest_expenses)],
        'Gross Profit': [float(financial_report[15844 - 15803]['value'])],
        'Ebit': [float(total_interest_expenses) - float(total_operating_expenses)],
        'Operating Income': [float(financial_report[15857 - 15803]['value'])],
        'Interest Expense': [float(total_interest_expenses)],
        'Income Tax Expense': [float(financial_report[15859 - 15803]['value'])],
        'Total Revenue': [float(financial_report[15842 - 15803]['value'])],
        'Total Operating Expenses': [float(total_operating_expenses)],
        'Cost Of Revenue': [float(financial_report[15843 - 15803]['value'])],
        'Total Other Income Expense Net': [float(financial_report[15856 - 15803]['value'])],
        'Net Income From Continuing Ops': [float(financial_report[15858 - 15803]['value'])],
        'Net Income Applicable To Common Shares': [float(financial_report[15860 - 15803]['value'])]
    }

    return data


def get_short_org_info(org_id: int):
    resp = requests.get(f"{ORGS_API_URL}/{org_id}").json()
    info = {
        'short_name': resp['short_name_text'],
        'address': resp['address'],
        'email': resp['email'],
        'phone': resp['detailinfo']['phone_number'],
        'director': resp['detailinfo']['director_name'],
        'org_id': org_id,
        'ticker': resp['exchange_ticket_name']
    }
    return info


def get_orgs_short(org_type):
    organisations_info = []
    suffix_id = NAME_SUFFIX_IDS[org_type]
    resp = requests.get(f"{ORGS_API_URL}?page_size=50&page=1&name_suffix_id={suffix_id}").json()

    i = 2
    while resp:
        for org in resp['results']:
            ticker = org['exchange_ticket_name']
            if not ticker or ticker == "-" or ticker == "мавжуд эмас" or ticker == "None":
                continue

            info = {
                'short_name': org['short_name_text'],
                'address': org['address'],
                'email': org['email'],
                'phone': org['detailinfo']['phone_number'],
                'director': org['detailinfo']['director_name'],
                'org_id': org['id'],
                'ticker': ticker,
            }
            organisations_info.append(info)

        resp = requests.get(f"{ORGS_API_URL}?page_size=50&page={i}&name_suffix_id={suffix_id}")
        if not resp.status_code == 200:
            break
        resp = resp.json()
        i += 1
    return organisations_info


def get_orgs_long(org_id):
    resp = requests.get(f"{ORGS_API_URL}/{org_id}").json()
    financial_indicators = requests.get(f"https://new-api.openinfo.uz/api/v1/reports/financial_indicators/?organization_id={org_id}").json()
    info = resp
    return {
        'financial_indicators': financial_indicators,
        'org_info': info,
    }


if __name__ == '__main__':
    ...
