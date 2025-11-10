import requests
from typing import List, Dict
import re

from pathlib import Path
import os
import json

# def check_cache(full_text_search_term:str):
#     """ Check cache and proceed to ingest data if data is not present in cache."""
#     cache_dir = Path('.cache')
#     cache_dir.mkdir(exist_ok=True)

#     cache_path = os.path.join(cache_dir, f"{full_text_search_term}.json")

#     return cache_path

#     # if os.path.exists(cache_path):
#     #     with open(cache_path, 'r', encoding='utf-8') as f_in:
#     #         return json.load(f_in)
#     # search_term_list = search(full_text_search_term)

#     # for i in search_term_list:
#     #     results = get_page(i)
#     #     with open(cache_path, 'w', encoding='utf-8') as f_out:
#     #         json.dump(results, f_out, ensure_ascii=False, indent=2)
#     # return results
    
def search(full_text_search_term:str) -> List[Dict]:
    """
    Sends a GET request to the Wikipedia API to perform full-text search for a given term. 
    Returns a list of dictionaries of all terms pertinent to the search term provided by the user.
    """


    url = 'https://en.wikipedia.org/w/api.php?'

    params = {
        'action': 'query',
        'format': 'json', 
        'list': 'search',
        'srsearch': full_text_search_term
        
    }
    headers = {
        'User-Agent': 'Student Project'
    }

    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()

    data = response.json()
    return data['query']['search']

def get_page(search_term:str) -> str:    
    """
    Send request to Wikipedia based on a single search term.
    Returns text strings of content.
    """
    url = 'https://en.wikipedia.org/w/index.php?'

    params = {
        'title':search_term,
        'action':'raw',
    }
    headers = {
            'User-Agent': 'Student Project'
        }

    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()

    return response.text




        













