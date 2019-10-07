import numpy
from system import __functioncontrolfolder




thresholdScorer= {
    "name":"thresholdScorer",
    "type":"function",
    "functionPointer":"threshold.threshold_scorer",   #filename.functionname
    "autoReload":True,                                 #set this to true to reload the module on each execution
    "children":[
        {"name":"input","type":"referencer"},                  # the output column
        {"name":"output","type":"referencer"},
        {"name":"streaming","type":"const","value":False},    #if set to true, we only update the values in the output which are not finite
        {"name":"annotations","type":"referencer"},             #the user annotations
        __functioncontrolfolder
    ]
}

thresholdScorer2= {
    "name":"thresholdScorer2",
    "type":"function",
    "functionPointer":"threshold.threshold_scorer_2",           #filename.functionname
    "autoReload":True,                                          #set this to true to reload the module on each execution
    "children":[
        {"name":"input","type":"referencer"},                   # the inputs, must be columns of one table
        {"name":"output","type":"folder"},                      # the output columns, these are generated by the scorer and placed here, and also "connected" to the table
                                                                # the outputs are named as the inputs, but with _score ending, plus we have the columns _total_score, and _differential
        {"name":"annotations","type":"referencer"},             # the user annotations
        {"name":"annotationsFilter","type":"const","value":[]}, # a list of strings to filter tags, if an annotation holds one of the filter tags, then we take it in
        {"name":"annotations2", "type": "referencer"},         # the additional user annotations, if given, these must OVERLAP with the annotations, it is another filter in the time
        {"name":"annotationsFilter2", "type": "const", "value": []}, # a list of strings to filter tags, if an annotation holds one of the filter tags, then we take it in
        {"name":"thresholds","type":"referencer"},              # pointing to the thresholds
        {"name":"incremental","type":"const","value":False},    # if incremental is set, then we only score areas that we haven't scored yet
        __functioncontrolfolder                                 # signal "reset" is used to initialize the function, create and hook the outputs, reset all values
    ]
}


def threshold_scorer_2_init(functionNode):
    """
        initialization:
        create all outputs, hook them
    """
    logger = functionNode.get_logger()
    logger.debug("threshold_scorer_2_init()")

    #get some helper nodes for later:
    inputNodes = functionNode.get_child("input").get_leaves()
    if not inputNodes:
        logger.error("no input nodes, exit")
        return
    tableNode = inputNodes[0].get_table_node()
    if not tableNode:
        logger.error("table not found, exit")
        return
    tableLen = len(inputNodes[0].get_value())

    timeNode = tableNode.get_table_time_node()
    if not timeNode:
        logger.error("time node not found")
        return


    #delete all outputs if there are any
    #outputNodes = functionNode.get_child("output").get_children()
    #for node in outputNodes:
    #    logger.info(f"deleting node {node.get_browse_path()}")
    #    node.delete()


    #now create all output nodes fresh
    outputNode = functionNode.get_child("output")
    for inputNode in inputNodes:
        if inputNode.get_id() == timeNode.get_id():
            continue # skip the time node
        newName = inputNode.get_name()+"_score"
        logger.info(f"create node {newName}")
        newNode = outputNode.create_child(newName,type="column")
        newNode.connect_to_table(tableNode) #this will reset the values and hook it to the table

    #also add two more:
    outputNode.create_child("_total_score",type="column").connect_to_table(tableNode)
    outputNode.create_child("_differential", type="column").connect_to_table(tableNode)
    outputNode.get_child("_differential").set_value(numpy.full(tableLen,False,dtype=numpy.float64))


def threshold_scorer_2(functionNode):
    """
        the threshold-scorer:
        it goes through the annotations and picks the time areas where the tag of the annotation match the filter
        it then goes through the annnotations2 and pick the time ares where the tag matches filter2
        those two time areas are "AND" merged: it is useful to define additional "regions"

        then we iterate over the thresholds and look for annotations of type "threshold"
        for each variable only one threshold (the last in the list) will be evaluated
        the variables to score on are the variables in the inputs which also have a threshold tag given

        the time areas to score on is either the full range (differential = false)
        or just the missing areas (differential = True)

        modelling:
        - put the scorer where you like
        - connect annotations and inputs
        - execute it once
        - connect the widgets.scoreVariables to the output folder (to make them scores)
        - install an observer (event:timeSeriesWidget.variables) in the widget to watch the selectedVariables and scoreVariables value change


        Args: the functionNode

    """
    logger = functionNode.get_logger()
    logger.debug(f'threshold_scorer_2() {functionNode.get_child("control").get_child("signal").get_value()}')

    #check for initialization
    if functionNode.get_child("control").get_child("signal").get_value() == "reset":

        #this is the first call, we just initialize
        threshold_scorer_2_init(functionNode)
        functionNode.get_child("control").get_child("signal").set_value("")
        return

    inputNodes = functionNode.get_child("input").get_leaves()
    tableNode = inputNodes[0].get_table_node()
    timeNode = tableNode.get_table_time_node()
    tableLen = len(timeNode.get_value())
    totalOutputNode = functionNode.get_child("output").get_child("_total_score")


    #first find the time areas to work on for the scorer, this is the overlap area of annotations and annotations2
    timeIndices = numpy.full(tableLen,False,dtype=numpy.bool) # True on the time points we want to score, , false for not score here

    annos1 = functionNode.get_child("annotations").get_leaves()
    annos1Filter = functionNode.get_child("annotationsFilter").get_value()

    for anno in annos1:
        logger.debug(f"processing anno {anno.get_name()}")
        if anno.get_child("type").get_value() != "time":
            continue # only time annotations
        if annos1Filter:
            #we must filter
            tags = anno.get_child("tags").get_value()
            if not any([tag in annos1Filter for tag in tags]):
                continue
        #take the indices
        indices = list(timeNode.get_time_indices(anno.get_child("startTime").get_value(),anno.get_child("endTime").get_value()))
        timeIndices[indices]=True #fancy indexing

    #now merge with the seconds selection
    annos2 = functionNode.get_child("annotations2").get_leaves()
    annos2Filter = functionNode.get_child("annotationsFilter2").get_value()
    for anno in annos2:
        if anno.get_child("type").get_value() != "time":
            continue # only time annotations
        if annos2Filter:
            #we must filter
            tags = anno.get_child("tags").get_value()
            if not any([tag in annos2Filter for tag in tags]):
                continue
        #take the indices
        indices = list(timeNode.get_time_indices(anno.get_child("startTime").get_value(),anno.get_child("endTime").get_value()))
        mask = numpy.full(tableLen,False,dtype=numpy.bool)
        mask[indices] = True
        timeIndices = numpy.logical_and(timeIndices,mask)


    #finally merge with the "differential" variable if required
    if functionNode.get_child("incremental").get_value():
        #we must work incremental, so we merge the data once more with the mask of the differential
        oldMask = functionNode.get_child("output").get_child("_differential").get_value() # the mask is true where a scoring has been done in the last round already
        mask = oldMask != True # we get an array of [true, false,....] for the elementwise expression != True
        timeIndices = numpy.logical_and(timeIndices,mask) # apply it on the mask
        newMask = oldMask or mask # unify merge the old and new mask
        functionNode.get_child("output").get_child("_differential").set_value(newMask) # set all true
    else:
        functionNode.get_child("output").get_child("_differential").set_value(timeIndices) # write out this area to eval


    # now we have in timeIndices the time indices to work on as a true/false mask
    # now find the variables and according thresholds
    thresholds ={} # a dict holding the nodeid and the threshold thereof (min and max)

    for anno in functionNode.get_child("thresholds").get_leaves():
        if anno.get_child("type").get_value() != "threshold":
            continue # only thresholds
        id = anno.get_child("variable").get_leaves()[0].get_id() # the first id of the targets of the annotation target pointer, this is the node that the threshold is referencing to

        thisMin  = anno.get_child("min").get_value()
        if type(thisMin) is type(None):
            thisMin = -numpy.inf
        thisMax = anno.get_child("max").get_value()
        if type(thisMax) is type(None):
            thisMax = numpy.inf
        thresholds[id] = {"min": thisMin, "max": thisMax}


    total_score = numpy.full(tableLen,numpy.inf,dtype=numpy.float64) # rest all
    for node in inputNodes:
        id = node.get_id()
        if id in thresholds:
            #must score
            logger.debug(f"must score {node.get_browse_path()} with {thresholds[id]['min']}, {thresholds[id]['max']}")
            values = node.get_value()
            #now find where the limits are over/under
            outOfLimit = numpy.logical_or( values < thresholds[id]['min'], values > thresholds[id]['max'] )
            outOfLimit = numpy.logical_and(outOfLimit,timeIndices)
            outOfLimitIndices = numpy.where(outOfLimit==True)
            outPutNode = functionNode.get_child("output").get_child( node.get_name()+"_score")
            if functionNode.get_child("incremental").get_value():
                score = outPutNode.get_value() # take the old and merge
            else:
                score = numpy.full(tableLen,numpy.inf,dtype=numpy.float64) # rest all
            score[timeIndices]=numpy.inf
            score[outOfLimitIndices] = values[outOfLimitIndices]
            total_score[numpy.isfinite(score)] = -1 #set one where the score is finite, there we have an anomaly
            outPutNode.set_value(score)

    totalOutputNode.set_value(total_score)
    return True



def threshold_scorer(functionNode):

    """
        # the threshold scorer can be used in standard or streaming,
        # if used in streaming (streaming = True), we only set the missing values in the output
        # (the points which are numpy.inf)
        # it can evaluate just one input or multiple
        # for multiple: it takes the order of the inputs the same as the outputs
        # the output is inf for no problem and a value for problem
        # currently, streamingMode is not supported
    """

    logger = functionNode.get_logger()
    logger.info(f">>>> in threshold_scorer {functionNode.get_browse_path()}")

    streamingMode = functionNode.get_child("streaming").get_value()

    #now get the input and outputs, check if number is the same
    inputNodesList = functionNode.get_child("input").get_leaves()
    outputNodesList =  functionNode.get_child("output").get_leaves()
    if len(inputNodesList) != len(outputNodesList):
        logger.error(f"input len {len(inputNodesList)} does not match output len {len(outputNodesList)}")
        return False

    inputNodes = {node.get_id():node for node in inputNodesList} # {nodeid:nodeObject}
    outputNodes ={node.get_id():node for node in outputNodesList}  # {nodeid:nodeObject}
    inoutNodes = {input.get_id():output for input,output in zip(inputNodesList,outputNodesList)}

    tableLen = len(inputNodes[list(inputNodes.keys())[0]].get_value())

    # get annotations remove all which we don't need
    # prepare a dict of {annotationId: {"annotation":annoobject,"input":inputobjece","output"
    annotationsList =  functionNode.get_child("annotations").get_leaves()
    #annotations = {node.get_id():node for node in annotationsList}
    thresholds = {}
    for anno in functionNode.get_child("annotations").get_leaves():
        if anno.get_child('tags').get_value()[0] == "threshold":
            targetNodeId = anno.get_child("variable").get_leaves()[0].get_id()
            if targetNodeId in inputNodes:
                #this annotation is a threshold and points to one of our inputs, we take it
                thresholds[anno.get_id()] = {"annotation":anno,"input":inputNodes[targetNodeId],"output":inoutNodes[targetNodeId]}

    if not thresholds:
        logger.error(f"we have no annotations for the thresholds of our variables")
        return False



    #now we have in thresholds what we have to process
    for thresholdId,info in thresholds.items():
        values = info["input"].get_value()
        min = info["annotation"].get_child("min").get_value()
        max = info["annotation"].get_child("max").get_value()

        score = numpy.full(tableLen,numpy.inf)

        if type(min) is type(None):
            min = -numpy.inf
        if type(max) is type(None):
            max = numpy.inf

        #set an numpy.inf where the score is ok and the value of the data where the score is not ok
        score = numpy.where(numpy.logical_and(values > min,values<max), numpy.inf, values)
        info["output"].set_value(score)


    return True
