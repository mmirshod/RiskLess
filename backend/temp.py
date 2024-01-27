import json

import requests


API_URL = 'https://new-api.openinfo.uz/api/v1/home/organizations?page_size=100&name_suffix_id=5'


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


def _extract_pages_tickers(data):
    organization_info = {}
    for result in data.get('results', []):
        org_id = result.get('id')
        ticker = result.get('exchange_ticket_name')

        if org_id and ticker:
            organization_info[ticker] = org_id

    return organization_info


def get_tickers() -> None:
    data = _get_data_from_api(API_URL)
    tickers = _extract_pages_tickers(data)

    _save_to_json(data=tickers, filename='../data/tickers.json')


def _save_to_json(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=2)


if __name__ == '__main__':
    get_tickers()
