import ui
import requests
import io
import dialogs
import random
import console
import os
import json
import clipboard

def get_info(num):
    fp = 'cache/{}.json'.format(num)
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
            with open(fp, 'wb') as f:
                f.write(req.content)
            return ui.Image.from_data(req.content)

def load_comic(view, num):
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
        view.name = view.comic['title']
    
    console.hide_activity()

@ui.in_background
def search(sender):
    sender.superview['tbl_search'].data_source.items = []
    for file in os.listdir('cache'):
        if file.split('.')[-1] != 'json': continue
        with open('cache/{}'.format(file)) as f:
            comic = json.load(f)
            search_text = sender.text.lower()
            if search_text in comic['title'].lower() or search_text in comic['transcript'].lower() or search_text in comic['alt'].lower():
                sender.superview['tbl_search'].data_source.items.append('{num}: {title}'.format(**comic))

def select_comic(sender):
    load_comic(main_view, int(sender.items[sender.selected_row].split(':')[0]))
    nav.pop_view()

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
    ans = console.alert('{month}/{day}/{year}'.format(**sender.superview.comic), sender.superview.comic['alt'], 'Copy link', 'Explain')
    if ans == 1:
        clipboard.set('http://xkcd.com/{}/'.format(sender.superview.current))
        console.hud_alert('Copied!')
    elif ans == 2:
        explain_view.load_url('http://www.explainxkcd.com/wiki/index.php/{}'.format(sender.superview.current))
        nav.push_view(explain_view)

@ui.in_background
def share(sender):
    dialogs.share_image(sender.superview['comic'].image)

@ui.in_background
def rand(sender):
    load_comic(sender.superview, random.randint(1, latest))

try:
    latest = requests.get('http://xkcd.com/info.0.json'.format(id)).json()['num']
    with open('cache/latest', 'w') as f:
        f.write(str(latest))
except requests.exceptions.ConnectionError:
    with open('cache/latest') as f:
        latest = int(f.read())


main_view = ui.load_view()
main_view.current = latest
load_comic(main_view, main_view.current)

nav = ui.NavigationView(main_view)

search_view = ui.load_view('search')
search_view['tbl_search'].data_source.items = []
search_view['tbl_search'].data_source.action = select_comic

explain_view = ui.WebView()
explain_view.name = 'Explain'
explain_view.right_button_items = [
    ui.ButtonItem(None, ui.Image('iob:chevron_right_32'), lambda _: explain_view.go_forward()),
    ui.ButtonItem(None, ui.Image('iob:chevron_left_32'), lambda _: explain_view.go_back())
]

nav.present()
