import re
import json
import random
import config
import hashlib
import requests

from urllib.parse import quote

# ------------------------------------------

API_URL = 'https://www.instagram.com/query/'
GRAPHQL_API_URL = 'https://www.instagram.com/graphql/query/'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'

# ------------------------------------------


class InstagramAPI:
    GET_COMMENTS_HASH = ''
    GET_FOLLOWERS_HASH = ''

    def __init__(self, session: requests.Session()):
        self.rhxgis = None
        self.csrftoken = None
        self.session = session or requests.Session()

    def genSig(self, query: dict):
        """
            Generates hash to be used for API requests
        """
        if self.rhxgis and query.get('query_hash') and query.get('variables'):
            q = query.get('variables')
            return hashlib.md5(f'{self.rhxgis}:{q}'.encode()).hexdigest()
        return None

    @staticmethod
    def extractRhxgisToken(html):
        x = re.search(
            '"rhx_gis":"(?P<rhx_gis>[a-f0-9]{32})"', html, re.MULTILINE)
        return x.group('rhx_gis') if x else None

    @staticmethod
    def extractCsrfToken(html):
        x = re.search(
            '"csrf_token":"(?P<csrf_token>[A-Za-z0-9]+)"', html, re.MULTILINE)
        return x.group('csrf_token') if x else None

    def login(self):
        """
            Logins to instagram in order to save the cookies needed \
            for access to its private API
        """
        # Get the csrftoken and rhx_gis token
        x = self.makeRequest(url='https://www.instagram.com', getJSON=False)
        self.csrftoken = self.extractCsrfToken(x)
        self.rhxgis = self.extractRhxgisToken(x)

        params = {
            'username': config.INSTAGRAM_USERNAME,
            'password': config.INSTAGRAM_PASSWORD,
        }
        r = self.makeRequest(
            url='https://www.instagram.com/accounts/login/ajax/', data=params)
        return r

    def searchUsers(self, query: str):
        """
            Searches instagram for users using query
        """
        url = f'https://www.instagram.com/web/search/topsearch/?query=' + \
            '+'.join(query.split())
        r = self.makeRequest(url=url)
        return [i['user'] for i in r['users']]

    def makeRequest(self, url: str, headers: dict = None,
                    data: dict = None, query: dict = None,
                    getJSON: bool=True):
        """
            Handles all the requests to the private API
        """
        if not headers:
            headers = {
                'User-Agent': USER_AGENT,
                'Accept': '*/*',
                'Accept-Language': 'en-US',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'close',
            }
            if data:
                headers.update({
                    'x-csrftoken': self.csrftoken,
                    'x-requested-with': 'XMLHttpRequest',
                    'x-instagram-ajax': '1',
                    'Referer': 'https://www.instagram.com',
                    'Authority': 'www.instagram.com',
                    'Origin': 'https://www.instagram.com',
                    'Content-Type': 'application/x-www-form-urlencoded'
                })
        if query:
            url += ('?' if '?' not in url else '&') + \
                'query_hash=' + query['query_hash']
            url += '&variables=' + quote(query['variables'])
            sig = self.genSig(query)
            if sig:
                headers['X-Instagram-GIS'] = sig

        method = 'POST' if data else 'GET'
        r = self.session.request(method=method, url=url,
                                 data=data, headers=headers)
        if getJSON:
            return r.json()
        else:
            return r.text
