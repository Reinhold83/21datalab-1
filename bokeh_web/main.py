import sys
from widgets import *

from bokeh.themes import Theme

try:
    modelUrl = sys.argv[1]
    modelPath = sys.argv[2]
except:
    pass

print("modelurl and path",modelUrl,modelPath,type(modelUrl),type('http://localhost:6001/'))


ts_server = TimeSeriesWidgetDataServer(str(modelUrl),str(modelPath))
t = TimeSeriesWidget(ts_server)

curdoc().add_root(t.get_layout())
curdoc().add_periodic_callback(t.periodic_cb, 500)
#curdoc().theme = Theme(json=themes.defaultTheme)
curdoc().theme = Theme(json=themes.whiteTheme)
t.set_curdoc(curdoc)

