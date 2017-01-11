import ui
import os
import json
import appex
import requests

def get_info(num):
    fp = '{}.json'.format(num)
    if os.path.exists(fp):
        with open(fp) as f:
            return json.load(f)
    else:
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
        return ui.Image(fp)
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
            return ui.Image.from_data(req.content)

os.chdir('cache')

try:
    latest = requests.get('http://xkcd.com/info.0.json'.format(id)).json()['num']
    with open('latest', 'w') as f:
        f.write(str(latest))
except requests.exceptions.ConnectionError:
    with open('latest') as f:
        latest = int(f.read())

@ui.in_background
def new(sender):
    i = get_comic(get_info(200)['img'])
    v.image = i
    vv.height = width/(i.size[0]/i.size[1])

#latest = 999
width = 304
i = get_comic(get_info(latest)['img'])
vv = ui.Button()
v = ui.ImageView()
v.flex = 'WH'
v.height = width/(i.size[0]/i.size[1])
v.content_mode = ui.CONTENT_SCALE_ASPECT_FIT
v.image = i
vv.add_subview(v)
vv.action = new
appex.set_widget_view(v)
