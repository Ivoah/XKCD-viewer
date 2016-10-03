import ui
import requests
import io
import dialogs
import random
import console
import os
import json
import clipboard
import glob
import PieView
import objc_util

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

@ui.in_background
def load_comic(view, num):
    if num == 404:
        view['comic'].image = ui.Image('../loading.png')
        view.current = num
        view['comic_num'].text = str(num)
        view['slider'].value = num/latest
        view.comic = None
        objc_util.ObjCInstance(view.navigation_view).navigationController().topViewController().title = objc_util.ns('404 - Not Found')
        return 
    console.show_activity()
    comic = get_info(num)
    if comic:
        view['comic'].image = ui.Image('../loading.png')
        view.current = num
        view['comic_num'].text = str(num)
        view['slider'].value = num/latest
        view.comic = comic
        
        view['comic'].image = get_comic(view.comic['img'])
        objc_util.ObjCInstance(view.navigation_view).navigationController().topViewController().title = objc_util.ns(view.comic['title'])
    
    console.hide_activity()

@ui.in_background
def search(sender):
    sender.superview['tbl_search'].data_source.items = []
    files = sorted(glob.glob('*.json'), key = lambda f: int(f.split('.')[0]))
    num_files = len(files)
    for i, file in enumerate(files):
        sender.superview['pie'].set_value(i/num_files)
        with open(file) as f:
            comic = json.load(f)
            found = True
            for word in sender.text.lower().split():
                if word not in ' '.join([str(v) for v in comic.values()]).lower():
                    found = False
            if found: sender.superview['tbl_search'].data_source.items.append('{num}: {title}'.format(**comic))
    sender.superview['pie'].set_value(0)

@ui.in_background
def select_comic(sender):
    nav.pop_view()
    load_comic(main_view, int(sender.items[sender.selected_row].split(':')[0]))

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
    if not sender.superview.comic: return
    ans = console.alert('{month}/{day}/{year}'.format(**sender.superview.comic), sender.superview.comic['alt'], 'Copy link', 'Explain')
    if ans == 1:
        #dialogs.share_url('http://xkcd.com/{}/'.format(sender.superview.current))
        clipboard.set('http://xkcd.com/{}/'.format(sender.superview.current))
        console.hud_alert('Copied!')
    elif ans == 2:
        explain_view.load_url('http://www.explainxkcd.com/wiki/index.php/{}'.format(sender.superview.current))
        nav.push_view(explain_view)

@ui.in_background
def share(sender):
    dialogs.share_image(main_view['comic'].image)

@ui.in_background
def rand(sender):
    load_comic(sender.superview, random.randint(1, latest))

@ui.in_background
def search_all(sender):
    search_view['tbl_search'].data_source.items = ['{num}: {title}'.format(**json.load(open(f))) for f in sorted(glob.glob('*.json'), key = lambda f: int(f.split('.')[0]))]

os.chdir('cache')

try:
    latest = requests.get('http://xkcd.com/info.0.json'.format(id)).json()['num']
    with open('latest', 'w') as f:
        f.write(str(latest))
except requests.exceptions.ConnectionError:
    with open('latest') as f:
        latest = int(f.read())


main_view = ui.load_view('../xkcd')
main_view.current = latest
main_view.left_button_items = [
    ui.ButtonItem(None, ui.Image('iob:ios7_search_strong_32'), lambda _: nav.push_view(search_view))
]
main_view.right_button_items = [
    ui.ButtonItem(None, ui.Image('iob:share_32'), share)
]

nav = ui.NavigationView(main_view)

search_view = ui.load_view('../search')
search_view['tbl_search'].data_source.items = []
search_view['tbl_search'].data_source.action = select_comic
search_view.right_button_items = [
    ui.ButtonItem('All', None, search_all)
]

explain_view = ui.WebView()
explain_view.name = 'Explain'
explain_view.right_button_items = [
    ui.ButtonItem(None, ui.Image('iob:chevron_right_32'), lambda _: explain_view.go_forward()),
    ui.ButtonItem(None, ui.Image('iob:chevron_left_32'), lambda _: explain_view.go_back())
]

nav.present(hide_title_bar = False)
load_comic(main_view, main_view.current)
