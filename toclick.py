import requests
import json
from pprint import pprint

# Create link
def create_link(link_name,short_name):
    url = 'https://to.click/api/v1/links'
    headers = { 'Content-type': 'application/json',
                'X-AUTH-TOKEN': '6uG6YnpUpXXE7yhpiyxNTmnD'}

    data = {    'data' : {  'type': 'link',
                            'attributes': { 'short_url' : short_name,
                                            'web_url' : link_name,
                                            'pixel_ids' : []}}}
    answer = requests.post(url, data=json.dumps(data), headers=headers)
    print(answer)
    response = answer.json()
    pprint(response)

# Access link
url = 'https://to.click/api/v1/links/234'
headers = { 'Content-type': 'application/json',
            'X-AUTH-TOKEN': '6uG6YnpUpXXE7yhpiyxNTmnD'}
data = {'data':{ 'type': 'link', 'id': '1589237'}}

answer = requests.get(url, data=json.dumps(data), headers=headers)
print(answer)
response = answer.json()
pprint(response)
