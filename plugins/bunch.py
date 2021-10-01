
import numpy
from system import __functioncontrolfolder
from matplotlib import cm
from model import getRandomId



bunchPlot= {
    "name":"bunchplot",
    "type":"function",
    "functionPointer":"bunch.bunch_plot",   #filename.functionname
    "autoReload":True,                                 #set this to true to reload the module on each execution
    "children":[
        {"name":"eventseries","type":"referencer"},                     # the events to use for syncing
        {"name":"variables","type":"referencer"},                        # the variable to create bunch plots from, if multiple, we take the first
        {"name":"outputFolder","type":"referencer"},                    # folder to create the bunch plot variables in
        {"name":"syncEvent","type":"const","value":"eventName"},        # give the name of the event to sync on
        {"name":"targetWidget","type":"referencer"},
        __functioncontrolfolder
    ]
}


bunchPlotCockpit= {
    "name":"bunchplotCockpit","type":"folder","children":[
        
        {"name": "cockpit", "type": "const", "value": "/customui/bunchcockpit.htm"},  #the cockpit for the motif miner
        {"name":"variables","type":"referencer"},           #pointing to the selectable variable for the dialog
        bunchPlot,                                          #the bunchplot function
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
    widget = functionNode.get_child("targetWidget").get_target()

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
    
    #widget.get_child("selectableVariables").add_references([],deleteAll=True)#remove all existing
    model.disable_observers()
    children = folder.get_children()
    for child in children[:-1]:
        child.delete()
    model.enable_observers()
    children[-1].delete() # delete the last to trigger the update


    thisRunId = getRandomId()#creating a the name each time we run to force the widget to reload all variables 
    newNodes=[]
    model.disable_observers()
    try:
        palette = get_color_map(len(indices))
        for count,idx in enumerate(indices):
            progressNode.set_value(float(count)/float(len(indices)))
            startTime = times[count] #this is the start time of this round of data 
            data = variable.get_time_series(start = startTime-timeLen,end = startTime+timeLen)
            timeOffset = startTime#-times[0]
            #create a new node
            varName = "bunch_" + variable.get_name() + "_" + str(idx)+"_"+thisRunId + "#" + str(count)
            new = folder.create_child(varName,type="timeseries")
            new.set_properties({"uiInfo":{"lineColor":palette[count]}})
            newNodes.append(new)
            new.set_time_series(times = data["__time"]-timeOffset,values = data["values"])
    finally:
        model.enable_observers()

    #now hook all results in
    model.disable_observers()
    widget.get_child("selectedVariables").add_references(newNodes[0:-1],deleteAll=True)
    model.enable_observers()
    widget.get_child("selectedVariables").add_references(newNodes[-1]) # add the last to trigger the observers 




    return True
 