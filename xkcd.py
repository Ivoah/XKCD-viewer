import ui
import io
import os
import json
import glob
import random
import dialogs
import console
import requests
import clipboard
import objc_util

image_search = False
faves = []

def get_info(num):
    fp = 'data/{}.json'.format(num)
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
    fp = 'data/' + url.split('/')[-1]
    if os.path.exists(fp):
        return os.path.abspath(fp) #ui.Image(fp)
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
            return os.path.abspath(fp) #ui.Image.from_data(req.content)

@ui.in_background
def load_comic(view, num):
    if num == 404:
        #view['comic'].image = ui.Image('loading.png')
        view['wv'].load_url(os.path.abspath('loading.png'))
        view.current = num
        view['comic_num'].text = str(num)
        view['slider'].value = num/latest
        view.comic = None
        objc_util.ObjCInstance(view.navigation_view).navigationController().topViewController().title = objc_util.ns('404 - Not Found')
        return 
    console.show_activity()
    comic = get_info(num)
    if comic:
        if num in faves:
            view['fav'].image = ui.Image('iob:ios7_heart_32')
        else:
            view['fav'].image = ui.Image('iob:ios7_heart_outline_32')
        #view['comic'].image = ui.Image('loading.png')
        view['wv'].load_url(os.path.abspath('loading.png'))
        view.current = num
        view['comic_num'].text = str(num)
        view['slider'].value = num/latest
        view.comic = comic
        
        #view['comic'].image = get_comic(view.comic['img'])
        view['wv'].load_url(get_comic(view.comic['img']))
        objc_util.ObjCInstance(view.navigation_view).navigationController().topViewController().title = objc_util.ns(view.comic['title'])
    
    console.hide_activity()

@ui.in_background
def search(sender):
    sender.superview['tbl_search'].data_source.items = []
    files = sorted((os.path.basename(f) for f in glob.glob('data/*.json')), key = lambda f: int(f.split('.')[0]))
    num_files = len(files)
    results = []
    sender.superview['gear'].start()
    for i, file in enumerate(files):
        with open('data/' + file) as f:
            comic = json.load(f)
            found = True
            for word in sender.text.lower().split():
                if word not in ' '.join([str(v) for v in comic.values()]).lower():
                    found = False
            #if found: sender.superview['tbl_search'].data_source.items.append({
            if found: results.append({
                'title': '{num}: {title}'.format(**comic),
                'image': get_comic(comic['img']) if image_search else None,
                'num': comic['num'],
                'accessory_type': 'detail_button'
            })
    sender.superview['tbl_search'].data_source.items = results
    sender.superview['gear'].stop()

@ui.in_background
def select_comic(sender):
    nav.pop_view()
    load_comic(main_view, 
sender.items[sender.selected_row]['num'])

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
def alt(comic):
    if not comic: return
    ans = console.alert('{month}/{day}/{year}'.format(**comic), comic['alt'], 'Copy link', 'Explain')
    if ans == 1:
        #dialogs.share_url('http://xkcd.com/{}/'.format(sender.superview.current))
        clipboard.set('http://xkcd.com/{}/'.format(comic['num']))
        console.hud_alert('Copied!')
    elif ans == 2:
        explain_view.load_url('http://www.explainxkcd.com/wiki/index.php/{}'.format(comic['num']))
        nav.push_view(explain_view)

@ui.in_background
def share():
    dialogs.share_image(ui.Image(get_comic(main_view.comic['img'])))

@ui.in_background
def rand(sender):
    load_comic(sender.superview, random.randint(1, latest))

@ui.in_background
def search_faves(sender):
    search_view['tbl_search'].data_source.items = [{
        'title': '{num}: {title}'.format(**get_info(num)),
        'image': get_comic(get_info(num)['img']) if image_search else None,
        'num': num,
        'accessory_type': 'detail_button'
    } for num in sorted(faves)]

def lat():
    try:
        l = requests.get('http://xkcd.com/info.0.json').json()['num']
        with open('data/latest', 'w') as f:
            f.write(str(l))
    except requests.exceptions.ConnectionError:
        with open('data/latest') as f:
            l = int(f.read())
    
    return l

def favorite(sender):
    try:
        faves.remove(main_view.comic['num'])
        main_view['fav'].image = ui.Image('iob:ios7_heart_outline_32')
    except ValueError:
        faves.append(main_view.comic['num'])
        main_view['fav'].image = ui.Image('iob:ios7_heart_32')
    with open('data/faves.json', 'w') as f:
        json.dump(faves, f)

if __name__ == '__main__':
    os.chdir(os.path.dirname(__file__))
    
    with open('data/faves.json') as f:
        faves = json.load(f)
        
    latest = lat()
    
    main_view = ui.load_view('xkcd')
    main_view.current = latest
    main_view.left_button_items = [
        ui.ButtonItem(None, ui.Image('iob:ios7_search_strong_32'), lambda _: nav.push_view(search_view))
    ]
    main_view.right_button_items = [
        ui.ButtonItem(None, ui.Image('iob:ios7_information_outline_32'), lambda _: alt(main_view.comic))
    ]
    
    nav = ui.NavigationView(main_view)
    
    search_view = ui.load_view('search')
    search_view['tbl_search'].data_source.items = []
    search_view.right_button_items = [
        ui.ButtonItem('Favorites', None, search_faves)
    ]
    
    explain_view = ui.WebView()
    explain_view.name = 'Explain'
    explain_view.right_button_items = [
        ui.ButtonItem(None, ui.Image('iob:chevron_right_32'), lambda _: explain_view.go_forward()),
        ui.ButtonItem(None, ui.Image('iob:chevron_left_32'), lambda _: explain_view.go_back())
    ]
    
    nav.present(hide_title_bar = True)
    load_comic(main_view, main_view.current)
