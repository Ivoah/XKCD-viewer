import requests
import os

def get_info(num):
    fp = '{}.json'.format(num)
    try:
        req = requests.get('http://xkcd.com/{}/info.0.json'.format(num))
    except requests.exceptions.ConnectionError:
        return False
    if req.status_code != 200:
        return False
    else:
        with open(fp, 'w') as f:
            f.write(req.text)
        return req.json()

def get_comic(url):
    fp = url.split('/')[-1]
    if os.path.exists(fp):
        return
    else:
        try:
            req = requests.get(url)
        except requests.exceptions.ConnectionError:
            return False
        if req.status_code != 200:
            return False
        else:
            with open(fp, 'wb') as f:
                f.write(req.content)
            return

latest = requests.get('http://xkcd.com/info.0.json'.format(id)).json()['num']
os.chdir('cache')
for i in range(1, latest + 1):
    if i == 404: continue
    print(i)
    get_comic(get_info(i)['img'])
