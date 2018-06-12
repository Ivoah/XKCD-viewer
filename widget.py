import ui
import os
import xkcd
import appex

os.chdir(os.path.dirname(__file__))

width = 304
i = xkcd.get_comic(xkcd.get_info(xkcd.lat())['img'])
v = ui.ImageView()
v.flex = 'WH'
v.height = width/(i.size[0]/i.size[1])
v.content_mode = ui.CONTENT_SCALE_ASPECT_FIT
v.image = i
appex.set_widget_view(v)
