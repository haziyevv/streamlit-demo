import os
import json
import requests
from config import SERPER_API_URL
from exceptions import CustomSearchAPIError
from typing import List, Dict

SERPER_API_KEY = os.getenv("SERPER_API_KEY")

class SearchSerper:
    """
    A class to handle web searches using the Serper API.
    
    This class provides functionality to search the web and return formatted results
    using the Serper search API. It handles authentication, request formatting,
    and response processing.
    """

    def __init__(self, max_results: int = 3) -> None:
        """
        Initialize the SearchSerper with a maximum number of results.

        Args:
            max_results (int): Maximum number of search results to return. Defaults to 3.
        """
        self._max_results = max_results

    def search(self, query: str) -> List[Dict[str, str]]:
        """
        Perform a web search using the Serper API.

        Args:
            query (str): The search query string.

        Returns:
            List[Dict[str, str]]: List of search results, each containing 'title' and 'body'.
                Example: [{'title': 'Result Title', 'body': 'Result snippet...'}]

        Raises:
            CustomSearchAPIError: If the API request fails or returns an error status.
        """
        payload = json.dumps({"q": query})
        headers = {
            'X-API-KEY': SERPER_API_KEY,
            'Content-Type': 'application/json'
        }

        # Make API request
        response = requests.request("POST", SERPER_API_URL, headers=headers, data=payload)
        results = response.json()

        # Handle error responses
        if response.status_code != 200:
            raise CustomSearchAPIError(
                f"Error {results['statusCode']}: {results['message']}. "
                "Unable to connect to the serper API."
            )

        # Process and return results
        return [
            {
                "title": x.get("title", ''),
                "body": x.get("snippet", '')
            } 
            for x in results['organic'][:self._max_results]
        ]
