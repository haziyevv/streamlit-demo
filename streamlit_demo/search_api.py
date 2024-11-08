import os
import json
import requests
from config import SERPER_API_URL
from exceptions import CustomSearchAPIError

SERPER_API_KEY = os.getenv("SERPER_API_KEY")

class SearchSerper:
    def __init__(self, max_results=3) -> None:
        self._max_results = max_results

    def search(self, query):
        payload = json.dumps({"q": query})
        headers = {
            'X-API-KEY': SERPER_API_KEY,
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", SERPER_API_URL, headers=headers, data=payload)
        results = response.json()
        if response.status_code != 200:
            raise CustomSearchAPIError(f"Error {results['statusCode']}: {results['message']}. Unable to connect to the serper API." )            
        return [{"title": x.get("title", ''), "body": x.get("snippet", '')} for x in results['organic'][:self._max_results]]
