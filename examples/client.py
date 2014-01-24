import json

from requests_oauthlib import OAuth1Session


API_KEY = "<API_KEY>"
API_SECRET = "<API_SECRET>"


def test_get():
    url = 'http://127.0.0.1:5000/some/api/endpoint'
    params = {'q': 'helloworld'}
    client = OAuth1Session(API_KEY, API_SECRET, None, None)
    r = client.get(url, params=params)
    print(r.status_code, r.json())


def test_post():
    url = 'http://127.0.0.1:5000/some/other/api/endpoint'
    with open('dummydata.json') as f:
        data = json.load(f)
    client = OAuth1Session(API_KEY, API_SECRET, None, None)
    headers = {'content-type': 'application/json'}
    r = client.post(url, data=json.dumps(data), headers=headers)
    print(r.status_code, r.json())


if __name__ == '__main__':
    test_get()
    # test_post()
