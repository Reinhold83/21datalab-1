
import numpy
from system import __functioncontrolfolder


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
        __functioncontrolfolder
    ]
}



def bunch_plot(functionNode):
    logger = functionNode.get_logger()
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

    times = events["__time"][indices]

    timeLen = times[1]-times[0] #we take the distance of the first as the length
    #now create nodes:
    outputFolder = functionNode.get_child("outputFolder").get_target()
    folder = outputFolder.create_child("bunch",type="folder")
    #delete all existing children of this folder
    for child in folder.get_children():
        child.delete()

    for count,idx in enumerate(indices):
        progressNode.set_value(float(count)/float(len(indices)))
        startTime = times[count]
        data = variable.get_time_series(start = startTime,end = startTime+timeLen)
        timeOffset = startTime-times[0]
        #create a new node
        new = folder.create_child("bunch_"+variable.get_name()+"_"+str(idx)+"#"+str(count),type="timeseries")
        new.set_time_series(times = data["__time"]-timeOffset,values = data["values"])

    return True
 