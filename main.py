import re
import json
import config
import hashlib
import requests

from urllib.parse import quote

# ------------------------------------------

API_URL = 'https://www.instagram.com/query/'
GRAPHQL_API_URL = 'https://www.instagram.com/graphql/query/'
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.2 Safari/605.1.15'

# ------------------------------------------


class Instagram:
    def __init__(self):
        self.rhxgis = None
        self.csrftoken = None
        self.session = requests.Session()

        self.login()

    def genSig(self, query: dict):
        """
            Generates hash to be used for API requests
        """
        if self.rhxgis and query.get('query_hash') and query.get('variables'):
            q = query.get('variables')
            return hashlib.md5(f'{self.rhxgis}:{q}'.encode()).hexdigest()
        return None

    @staticmethod
    def extractRhxgisToken(html: str):
        x = re.search(
            '"rhx_gis":"(?P<rhx_gis>[a-f0-9]{32})"', html, re.MULTILINE)
        return x.group('rhx_gis') if x else None

    @staticmethod
    def extractCsrfToken(html: str):
        x = re.search(
            '"csrf_token":"(?P<csrf_token>[A-Za-z0-9]+)"', html, re.MULTILINE)
        return x.group('csrf_token') if x else None

    @staticmethod
    def stringify(variables: dict):
        return json.dumps(variables, separators=(',', ':'))

    def login(self):
        """
            Logins to instagram in order to save the cookies needed \
            for access to its private API
        """
        # Get the csrftoken and rhx_gis token
        x = self.session.get(url='https://www.instagram.com',
                             headers={'User-Agent': USER_AGENT})
        self.csrftoken = self.extractCsrfToken(x.text)
        self.rhxgis = self.extractRhxgisToken(x.text)

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

    def followUser(self, handle: str):
        # We make this request first to get the updated csrf token
        # as well as the user ID
        url = f'https://www.instagram.com/{handle}/?__a=1'
        d = self.makeRequest(url)
        userID = d.get('graphql', {}).get('user', {}).get('id')

        # Make the follow request
        url = f'https://www.instagram.com/web/friendships/{userID}/follow/'
        r = self.makeRequest(url, method='POST')
        return r.get('status') == 'ok'

    def unfollowUser(self, handle: str):
        # We make this request first to get the updated csrf token
        # as well as the user ID
        url = f'https://www.instagram.com/{handle}/?__a=1'
        d = self.makeRequest(url)
        userID = d.get('graphql', {}).get('user', {}).get('id')

        # Make the unfollow request
        url = f'https://www.instagram.com/web/friendships/{userID}/unfollow/'
        r = self.makeRequest(url, method='POST')
        return r.get('status') == 'ok'

    def likePost(self, mediaID: str):
        url = f'https://www.instagram.com/web/likes/{mediaID}/like/'
        r = self.makeRequest(url, method='POST')
        return r.get('status') == 'ok'

    def unlikePost(self, mediaID: str):
        url = f'https://www.instagram.com/web/likes/{mediaID}/unlike/'
        r = self.makeRequest(url, method='POST')
        return r.get('status') == 'ok'

    def postComment(self, mediaID: str, comment: str):
        if len(comment) > 300:
            raise ValueError('The total length of the comment cannot exceed 300 characters.')
        if re.search(r'[a-z]+', comment, re.IGNORECASE) and comment == comment.upper():
            raise ValueError('The comment cannot consist of all capital letters.')
        if len(re.findall(r'#[^#]+\b', comment, re.UNICODE | re.MULTILINE)) > 4:
            raise ValueError('The comment cannot contain more than 4 hashtags.')
        if len(re.findall(r'\bhttps?://\S+\.\S+', comment)) > 1:
            raise ValueError('The comment cannot contain more than 1 URL.')

        url = f'https://www.instagram.com/web/comments/{mediaID}/add/'
        data = {'comment_text': comment}
        r = self.makeRequest(url, data=data)
        return r.get('status') == 'ok'

    def deleteComment(self, mediaID: str, commentID: str):
        url = f'https://www.instagram.com/web/comments/{mediaID}/delete/{commentID}/'
        r = self.makeRequest(url, method='POST')
        return r.get('status') == 'ok'

    def getTimeline(self, count: int = 50):
        pass

    def makeRequest(self, url: str, headers: dict = None,
                    data: dict = None, query: dict = None,
                    method: str=None):
        """
            Handles all the requests to the private API
        """
        if not headers:
            headers = {
                'User-Agent': USER_AGENT,
                'Accept': '*/*',
                'Accept-Language': 'en-US',
                'Accept-Encoding': 'br, gzip, deflate',
                'Connection': 'keep-alive',
                'Host': 'www.instagram.com',
            }
            if data or method == 'POST':
                headers.update({
                    'X-CSRFToken': self.csrftoken,
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-Instagram-AJAX': '1',
                    'Referer': 'https://www.instagram.com',
                    'Authority': 'www.instagram.com',
                    'Origin': 'https://www.instagram.com',
                    'Content-Type': 'application/x-www-form-urlencoded',
                })

        if query:
            url += ('?' if '?' not in url else '&') + \
                'query_hash=' + query['query_hash']
            url += '&variables=' + quote(query['variables'])
            sig = self.genSig(query)
            if sig:
                headers['X-Instagram-GIS'] = sig

        if not method:
            method = 'POST' if data else 'GET'
        r = self.session.request(method=method, url=url,
                                 data=data, headers=headers)
        if r.cookies.get('csrftoken'):
            self.csrftoken = r.cookies['csrftoken']

        return r.json()


if __name__ == '__main__':
    ig = Instagram()
    print(ig.postComment('1916585046861649463', 'nice'))
