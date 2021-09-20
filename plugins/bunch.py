
import numpy
from system import __functioncontrolfolder
from matplotlib import cm



bunchPlot= {
    "name":"bunchplot",
    "type":"function",
    "functionPointer":"bunch.bunch_plot",   #filename.functionname
    "autoReload":True,                                 #set this to true to reload the module on each execution
    "children":[
        {"name":"eventseries","type":"referencer"},                     # the events to use for syncing
        {"name":"variables","type":"referencer"},                        # the variable to create bunch plots from
        {"name":"outputFolder","type":"referencer"},                    # folder to create the bunch plot variables in
        {"name":"syncEvent","type":"const","value":"eventName"},        # give the name of the event to sync on
        {"name":"targetWidget","type":"referencer"},
        __functioncontrolfolder
    ]
}


def get_color_map(size):
    map = cm.get_cmap("gist_rainbow", size) # https://matplotlib.org/stable/tutorials/colors/colormaps.html
    palette = map(range(size))
    colors = []
    for rgb in palette:
        col = "#"+"%02x"%int(rgb[0]*float(255))+"%02x"%int(rgb[1]*255)+"%02x"%int(rgb[2]*255)
        colors.append(col)
        #print(rgb,col)
    return colors

def bunch_plot(functionNode):
    logger = functionNode.get_logger()
    model = functionNode.get_model()
    m=functionNode.get_model()
    logger.info("==>>>> in bunch_plot " + functionNode.get_browse_path())
    progressNode = functionNode.get_child("control").get_child("progress")
    progressNode.set_value(0)

    # now get the input and outputs
    variable = functionNode.get_child("variables").get_leaves()[0]
    eventNode = functionNode.get_child("eventseries").get_target()
    events = eventNode.get_event_series() # get the full event series
    syncEvent = functionNode.get_child("syncEvent").get_value()
    map = events["eventMap"]
    if syncEvent not in map:
        return False
    syncEventNo = map[syncEvent]

    indices = numpy.where(events["values"]==syncEventNo)[0]

    times = events["__time"][indices] # get the time points of the given event

    timeLen = times[1]-times[0] #we take the distance of the first as the length
    #now create nodes:
    outputFolder = functionNode.get_child("outputFolder").get_target()
    folder = outputFolder.create_child("bunch",type="folder")
    #delete all existing children of this folder
    for child in folder.get_children():
        child.delete()

    newNodes=[]
    palette = get_color_map(len(indices))
    for count,idx in enumerate(indices):
        progressNode.set_value(float(count)/float(len(indices)))
        startTime = times[count] #this is the start time of this round of data 
        data = variable.get_time_series(start = startTime-timeLen,end = startTime+timeLen)
        timeOffset = startTime#-times[0]
        #create a new node
        varName = "bunch_" + variable.get_name() + "_" + str(idx) + "#" + str(count)
        new = folder.create_child(varName,type="timeseries")
        new.set_properties({"uiInfo":{"lineColor":palette[count]}})
        newNodes.append(new)
        new.set_time_series(times = data["__time"]-timeOffset,values = data["values"])

    """
    #now also generate the color map
    size = len(newNodes)
    map = cm.get_cmap("gist_rainbow",size)
    palette = map(range(size))
    currentColorsNew={}

    for idx,node in enumerate(newNodes):
        colorcode = "#%06x"%int(palette[idx][0]*256*256+palette[idx][1]*256+palette[idx][2])
        currentColorsNew[node.get_browse_path()]={"lineColor":colorcode}

    #distribute on the widgets
    for widget in model.find_nodes("root",{"type":"widget"}):
        cur = widget.get_child("currentColors").get_value()
        if not cur:
            cur = {}
        cur.update(currentColorsNew)
        widget.get_child("currentColors").set_value(cur)
    """

    #now hook all results in
    widget = functionNode.get_child("targetWidget").get_target()
    widget.get_child("selectableVariables").add_references(folder,deleteAll=True,allowDuplicates=False)
    widget.get_child("selectedVariables").add_references(newNodes,deleteAll=True,allowDuplicates=False)
    
    




    return True
 