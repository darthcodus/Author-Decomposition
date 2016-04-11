import json
import http.client
import urllib.parse

import requests
from requests.packages.urllib3 import HTTPResponse


def try1():
    text = 'La ecología es algo que cada vez preocupa más. El calentamiento global es un hecho sobre el que hay consenso científico y las altas temperaturas del año pasado y del invierno parecen darles la razón.'
    url = '25.30.82.122:8011'
    headers = {
        'Accept': 'application/json, text/javascript, */*',
        'Accept-Encoding': 'gzip, deflate',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
    }
    properties = {
        "annotators": "tokenize,ssplit",
        "coref.md.type": "dep",
        "coref.mode": "statistical"
    }
    params = urllib.parse.urlencode({'/?properties': str(properties)})
    conn = http.client.HTTPConnection(url)
    conn.request('POST', params, text.encode(), headers)
    response = conn.getresponse()

    output = response.read().decode()
    output = json.loads(output, encoding='utf-8', strict=True)
    print(response.status)
    print(output['sentences'][0]['tokens'][1]['word'])


def try2():
    text = 'La ecología es algo que cada vez preocupa más. El calentamiento global es un hecho sobre el que hay consenso científico y las altas temperaturas del año pasado y del invierno parecen darles la razón.'
    url = 'http://25.30.82.122:8011'
    properties = {
        "annotators": "tokenize,ssplit",
        "coref.md.type": "dep",
        "coref.mode": "statistical"
    }
    params = {'properties': str(properties)}
    data = text.encode()
    r = requests.post(url, params=params, data=data)
    output = r.text
    output = json.loads(output, encoding='utf-8', strict=True)
    print(output['sentences'][0]['tokens'][1]['word'])


def main():
    try2()


if __name__ == '__main__':
    main()
