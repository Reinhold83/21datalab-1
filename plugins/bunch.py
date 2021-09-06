
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








    annotations = functionNode.get_child("annotations").get_leaves()

    if annotations:
        for anno in annotations:
            logger.debug("annotation " + anno.get_browse_path())


    """
        now prepare the data for processing:

        1.1) define the sample times "times" from the data or generated
        1.2) use the map to match the tag labels to values 
        1.3) resample and select data based on annotations, region and the "times"
        1.4) train the model, score on region or full data 
    """

    # two ways to define the sampling:
    # if resamplePeriod is given, we take the interval for the sampling, if not given
    # we assume all data from the same timing, we take the times from the first variable as resampling
    period = functionNode.get_child("resamplePeriod").get_value()
    times = inputNodes[0].get_time_series()["__time"]
    if period:
        times = numpy.arange(times[0],times[-1],period)

    # get the annotation map
    tagsFilter = functionNode.get_child("annotationFilter").get_value()  # pick the tags to take

    # the annotations_to_class_vector takes all annotations in the positive list
    # and will also take the ones which are not explicitly ignored and extend the tags list with it,so we
    # prepare:


    if not tagsFilter:
        tags = set()
        for anno in annotations:
            tags.update(anno.get_child("tags").get_value())
        tagsFilter = list(tags)


    tagsMap = {tag:idx for idx,tag in enumerate(tagsFilter)}
    labels = mh.annotations_to_class_vector(annotations,times,regionTag="region",tagsMap=tagsMap,autoAdd=False)
    inputMask = numpy.isfinite(labels)


    trainingData = []
    # now grab the values from the columns
    valuesMask = numpy.full(len(times),True,dtype=numpy.bool)
    for node in inputNodes:
        #values = numpy.asarray(node.get_value())
        values = numpy.float32(node.get_time_series(resampleTimes=times)["values"])
        #valuesMask = numpy.isfinite(values)
        valuesMask = valuesMask & numpy.isfinite(values)
        trainingData.append(values)

    trainingDataFiltered = []
    for t in trainingData:
        trainingDataFiltered.append(list(t[valuesMask&inputMask]))


    table = numpy.stack(trainingDataFiltered, axis=0)

    logger.debug(f"Data quality: {numpy.count_nonzero(inputMask == True)} is good of {len(inputMask)}")

    progressNode.set_value(0.3)
    #
    # now fit the model
    #
    model =  RandomForestClassifier()
    model.fit(table.T, labels[valuesMask&inputMask])
    progressNode.set_value(0.6)
    #
    # scoring
    #
    # we score on the whole times or the selection by a region
    # do  we have a region?
    regions = mh.filter_annotations(annotations,"region")
    if regions:
        regionMask = numpy.isfinite(mh.annotations_to_class_vector(regions,times,ignoreTags=[]))
        scoreTimes = times[regionMask]
    else:
        scoreTimes = times


    # now grab the values from the columns
    scoreData = []
    valuesMask = numpy.full(len(scoreTimes), True, dtype=numpy.bool)
    for node in inputNodes:
        data = node.get_time_series(resampleTimes=scoreTimes)["values"]
        valuesMask = valuesMask & numpy.isfinite(data)
        scoreData.append(data)

    scoreFiltered = []
    for t in scoreData:
        scoreFiltered.append(list(t[valuesMask]))

    scoreData = scoreFiltered




    scoreTable = numpy.stack(scoreData, axis=0)
    score = model.predict(scoreTable.T)

    #write back the output
    outputNode.set_time_series(times=scoreTimes,values=score)
    progressNode.set_value(1)

    #write back the info of the background node
    widget = functionNode.get_child("widget").get_target()
    if widget:
        currentBackground = widget.get_child("background").get_target()
        if currentBackground and currentBackground.get_id() == outputNode.get_id():
            #we have set the ref before already
            pass
        else:
            widget.get_child("background").add_references(functionNode.get_child("output"),deleteAll=True,allowDuplicates=False)


    #write the background classes coloring based on the annotation colors
    annoColors = widget.get_child("hasAnnotation.colors").get_value() #{"busy":{"color":"#ffe880","pattern":"/"},"free":{"color":"brown","pattern":"+"},"region":{"color":"grey","pattern":null},"pattern_match":{"color":"#808080","pattern":"v"}}
    backgroundColors = {str(no):annoColors[tag]["color"]  for tag,no in tagsMap.items() if tag in annoColors}
    backgroundColors["-1"]="red"         #these are typical default values
    backgroundColors["default"]="white"
    widget.get_child("backgroundMap").set_value(backgroundColors)



    return True
