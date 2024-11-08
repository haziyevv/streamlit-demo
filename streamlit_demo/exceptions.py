class CustomOpenAIAuthenticationError(Exception):
    def __init__(self, message) -> None:
        self.message = message if message else "Authorization error . "

class CustomSearchAPIError(Exception):
    def __init__(self, message) -> None:
        self.message = message if message else "Unable to connect to the search API. "