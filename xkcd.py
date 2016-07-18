import ui
import requests
import io
import dialogs
import random
import console
import os.path
import json

def get_info(num):
    fp = 'cache/{}.json'.format(num)
    if os.path.exists(fp):
        return json.load(open(fp))
    else:
        try:
            req = requests.get('http://xkcd.com/{}/info.0.json'.format(num))
        except requests.exceptions.ConnectionError:
            return False
        if req.status_code != 200:
            return False
        else:
            open(fp, 'w').write(req.text)
            return req.json()

def get_comic(url):
    fp = os.path.join('cache', url.split('/')[-1])
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
            open(fp, 'wb').write(req.content)
            return ui.Image.from_data(req.content)

def load_comic(view, num):
    view['gear'].start()
    console.show_activity()
    comic = get_info(num)
    if comic or num == 404:
        view['comic'].image = ui.Image('loading.png')
        view['title'].text = 'Loading comic...'
        view.current = num
        view['comic_num'].text = str(num)
        view['slider'].value = num/latest
        view.comic = comic
        
        view['comic'].image = get_comic(view.comic['img'])
        view['title'].text = view.comic['title']
    
    view['gear'].stop()
    console.hide_activity()

@ui.in_background
def prev(sender): 
    load_comic(sender.superview, sender.superview.current - 1)

@ui.in_background
def next(sender):
    load_comic(sender.superview, sender.superview.current + 1)

@ui.in_background
def slider_changed(sender):
    load_comic(sender.superview, int(latest*sender.value) if int(latest*sender.value) > 0 else 1)

@ui.in_background
def alt(sender):
    dialogs.alert('{month}/{day}/{year}'.format(**sender.superview.comic), sender.superview.comic['alt'])

@ui.in_background
def rand(sender):
    load_comic(sender.superview, random.randint(1, latest))

try:
    latest = requests.get('http://xkcd.com/info.0.json'.format(id)).json()['num']
    open('cache/latest', 'w').write(str(latest))
except requests.exceptions.ConnectionError:
    latest = int(open('cache/latest').read())

v = ui.load_view()
v.current = latest
v.present()
load_comic(v, v.current)

