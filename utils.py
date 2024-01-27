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

REPORTS_API_URL = 'https://new-api.openinfo.uz/api/v1/reports'
ORGS_API_URL = 'https://new-api.openinfo.uz/api/v1/home/organizations'


def preprocess(data: dict) -> dict:
    data = pd.DataFrame(data)
    print(data)
    scores: List[float] = [np.expm1(ENV_MODEL.predict(data)[0]), np.expm1(SOC_MODEL.predict(data)[0]), np.expm1(GOV_MODEL.predict(data))[0]]
    scores = [np.round(val, 2) if val < 10 else np.round(val, 1) for val in scores]

    prediction = {
        "env_score": scores[0],
        "soc_score": scores[1],
        "gov_score": scores[2],
    }

    return prediction


API_URL = 'https://new-api.openinfo.uz/api/v1/reports'


def get_annual_report(org_id: int, org_type: str) -> dict:
    resp = requests.get(f'{API_URL}/{org_type}/annual?page_size=500').json()
    report_id = None

    for org in resp['results']:
        if org['organization'] == org_id:
            report_id = org['id']
            break

    if report_id:
        return requests.get(f'{API_URL}/{org_type}/annual/{report_id}').json()


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


def get_orgs_short(org_type):
    organisations_info = []
    suffix_id = NAME_SUFFIX_IDS[org_type]
    resp = requests.get(f"{ORGS_API_URL}?page_size=50&page=1&name_suffix_id={suffix_id}").json()

    i = 2
    while resp:
        for org in resp['results']:
            info = {
                'short_name': org['short_name_text'],
                'address': org['address'],
                'email': org['email'],
                'phone': org['detailinfo']['phone_number'],
                'director': org['detailinfo']['director_name'],
                'org_id': org['id']
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