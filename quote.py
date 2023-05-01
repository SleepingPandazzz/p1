import requests

class MyQuote:
    def __init__(self):
        response = requests.get('https://api.quotable.io/quotes/random?maxLength=50').json()[0]
        self.content = response.get('content')
        self.author = response.get('author')