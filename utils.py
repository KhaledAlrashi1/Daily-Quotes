# my_app/utils.py
import json
import os
from datetime import date

def load_quote_offset():
    try:
        with open('quote_offset.json', 'r') as f:
            data = json.load(f)
            return data.get('quote_offset', 0), data.get('last_access_date', None)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0, None

def save_quote_offset(offset, last_access_date):
    with open('quote_offset.json', 'w') as f:
        json.dump({'quote_offset': offset, 'last_access_date': last_access_date}, f)