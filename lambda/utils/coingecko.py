"""
Helper functions for API

Coingecko API https://www.coingecko.com/en/api/documentation
"""

import requests
import json

BASE_URL = 'https://api.coingecko.com/api/v3'

def check_status():
    url = BASE_URL + '/ping'

    # add HTTP headers
    headers = {
        'Accept': 'application/json'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return True

    return False

def fetch_price_data_by_symbol(symbol):
    url = BASE_URL + '/simple/price'

    # add query args
    params = {
        'ids': symbol,
        'vs_currencies': 'usd',
        'precision': 4,
        'include_last_updated_at': 'true',
        'include_market_cap': 'true',
        'include_24hr_vol': 'true',
        'include_24hr_change': 'true'
    }

    # add HTTP headers
    headers = {
        'Accept': 'application/json'
    }

    response = requests.get(url, headers=headers, params=params)

    if not response.ok:
        raise Exception(f"Request for '{url}' failed")

    content = json.loads(response.content)

    return content