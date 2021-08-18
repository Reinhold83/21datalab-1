from system import __functioncontrolfolder
from typing import List
from model import date2secs, Node, getRandomId
#  from tqdm import tqdm
import logging
import pandas as pd 
import os
import json
import datetime as dt
import time

previewFileTemplate = {
    "name":"importer_preview",
    "type":"function",
    "functionPointer":"importer.preview_file",   # filename.functionname
    "autoReload":True,                             # set this to true to reload the module on each execution
    "children":[
        {"name":"data_preview","type":"variable"},
        {"name":"fileName","type":"variable"},
        __functioncontrolfolder
    ]
}

importRunTemplate = {
    "name":"importer_import",
    "type":"function",
    "functionPointer":"importer.import_run",        # filename.functionname
    "autoReload":True,                              # set this to true to reload the module on each execution
    "children":[
        {"name":"tablename","type":"variable"},     # ...
        {"name":"metadata","type":"variable"},      # ...
        __functioncontrolfolder
    ]
}

pipeline = {
    "name": "pipeline",
    "type": "folder",
    "children": [
        { "name": "imports", "type": "folder" },
        { "name": "cockpit", "type": "const", "value": "customui/importer/index.htm" },
        previewFileTemplate,
        { "name":"observer",
          "type": "observer", "children": [           # observer for the selected variables (not the values)
            {"name": "enabled", "type": "const", "value": True},                # on by default to enable drag + drop
            {"name": "triggerCounter", "type": "variable", "value": 0},         # increased on each trigger
            {"name": "lastTriggerTime", "type": "variable", "value": ""},       # last datetime when it was triggered
            {"name": "targets", "type": "referencer", "references":["importer.importer_preview.control.executionCounter"]},  # pointing to the nodes observed
            {"name": "properties", "type": "const", "value": ["value"]},  # properties to observe [“children”,“value”, “forwardRefs”]
            {"name": "onTriggerFunction", "type": "referencer"},                # the function(s) to be called when triggering
            {"name": "hasEvent", "type": "const", "value": True},               # set to true if we want an event as well
            {"name": "eventString", "type": "const", "value": "importer.importer_preview.data_imported"}  # the string of the event
            ]
        },
        importRunTemplate,
    ]
}


annotation_import = {
   "name":"annotation_import_function",
    "type":"function",
    "functionPointer":"importer.annotation_import_function",            # filename.functionname
    "autoReload":True,                                                  # set this to true to reload the module on each execution
    "children":[
        {"name":"targetFolder","type":"referencer"},
        {"name":"fileName","type":"variable"},
        {"name":"importReferences","type":"const","value":False},       #if import references is set, we try to reconnect the annotations to variables using the id
                                                                        # => this might fail when the ids in the new project are different, be careful here
        {"name":"widgets","type":"referencer"},                         #if widgets are set, we integrate the annotations in the widgets and give them colors etc.
        __functioncontrolfolder
    ]
}

annotation_export = {
   "name":"annotation_export_function",
    "type":"function",
    "functionPointer":"importer.annotation_export_function",   # filename.functionname
    "autoReload":True,                             # set this to true to reload the module on each execution
    "children":[
        {"name":"annotations","type":"referencer"},
        {"name":"fileName","type":"variable","value":None},
        __functioncontrolfolder
    ]
}


def preview_file(iN):

    logger = iN.get_logger()
    logger.debug(f"importer.preview_file()")

    # --- define vars
    observer = iN.get_parent().get_child("observer")
    event = observer.get_child("eventString")
    parentName = iN.get_parent().get_name()
    event.set_value(f"{parentName}.importer_preview.data_imported")

    # --- set vars
    filename = 'upload/' + iN.get_child("fileName").get_value()
    pathBase = os.getcwd()

    # --- load csv data
    dataFile = pd.read_csv(filename, nrows=5)
    previewData = dataFile.head()
    previewDataString = previewData.to_json(orient='table')

    # --- update node with preview data
    node = iN.get_child("data_preview")
    node.set_value(previewDataString)

    # --- return
    return True

def import_run(iN):

    logger = iN.get_logger()
    logger.debug(f"import running..")
    timeStartImport = dt.datetime.now()

    # --- define vars
    importerNode = iN.get_parent()

    # --- [vars] define
    tablename = iN.get_child("tablename").get_value()
    logger.debug(f"tablename: {tablename}")

    #  # --- create needed nodes
    importerNode.create_child('imports', type="folder")
    importsNode = importerNode.get_child("imports")

    # TODO importsNode.get_child(tablename).delete()
    importsNode.create_child(tablename, type="folder")
    table = importsNode.get_child(tablename)
    table.create_child('variables', type="folder")
    table.create_child('columns', type="referencer")
    table.create_child('metadata', type="const")
    vars = table.get_child("variables")
    cols = table.get_child("columns")

    # --- read metadata and fields
    metadataRaw = iN.get_child("metadata").get_value()
    metadata = json.loads(metadataRaw)
    table.get_child("metadata").set_value(metadata)
    fields = metadata["fields"] 
    timefield = int(metadata["timefield"]) - 1
    filename = metadata["filename"]
    headerexists = metadata["headerexists"]
    filepath = 'upload/' + filename 

    # --- load csv data
    # * https://www.shanelynn.ie/python-pandas-read_csv-load-data-from-csv-files/
    # * [ ] optimize speed? https://stackoverflow.com/questions/16476924/how-to-iterate-over-rows-in-a-dataframe-in-pandas
    # * [ ] vectorize a loop https://stackoverflow.com/questions/27575854/vectorizing-a-function-in-pandas
    df = pd.read_csv(filepath)

    # --- define time list
    # * select rows and columns from dataframe https://thispointer.com/select-rows-columns-by-name-or-index-in-dataframe-using-loc-iloc-python-pandas/
    timeList = df.iloc[:,timefield].to_list()
    epochs = [date2secs(time) for time in timeList]
    print(epochs) 

    # --- import data, set vars and columns
    data = {}
    for field in fields:
        fieldno = int(field["no"]) - 1
        fieldname = str(field["val"]).replace('.','_')
        fieldvar = vars.create_child(fieldname, type="timeseries")
        if timefield != fieldno:
            data[fieldname] = df.iloc[ :, fieldno].to_list()
            fieldvar.set_time_series(values=data[fieldname],times=epochs)
        cols.add_references(fieldvar)
        logger.debug(f"import val: {fieldname}")
        print(fieldvar) 

    # look for nodes of type widget and ensure variables can be selected
    workbench_model = iN.get_model()
    widget_nodes: List[Node] = workbench_model.find_nodes("root", matchProperty={"type": "widget"})
    for widget_node in widget_nodes:
        selectable_variables_referencer: Node = widget_node.get_child("selectableVariables")
        selectable_variables_referencer.add_references([vars])

    logger.debug(f"import complete (seconds: {(dt.datetime.now()-timeStartImport).seconds})")
    return True



def annotation_export_function(functionNode):
    logger = functionNode.get_logger()
    progressNode = functionNode.get_child("control").get_child("progress")
    signalNode = functionNode.get_child("control").get_child("signal")
    model = functionNode.get_model()
    fileName = functionNode.get_child("fileName").get_value()
    if type(fileName) is type(None):
        modelPath = functionNode.get_model().get_info()["name"]
        modelName = modelPath.split(os.sep)[-1]
        absPath = model.get_upload_folder_path()+"/"+modelName+"_annos_"+getRandomId()+".json"
    else:
        if os.path.isabs(fileName):
            absPath = fileName
        else:
            absPath = model.get_upload_folder_path()+"/"+fileName+".json"
    logger.debug(f"export annotations to {absPath}")


    annos = functionNode.get_child("annotations").get_leaves()
    if not annos:
        logger.info("no annos to export")
        return True

    f = open(absPath,"w")
    first = True

    progressOld = 0
    for idx,anno in enumerate(annos):
        progress = float(int(50*idx/len(annos)))/50
        if progress!=progressOld:
            progressNode.set_value(progress)
            progressOld=progress
            if signalNode.get_value()=="stop":
                break



        if anno.get_type()=="annotation":
            keys = {"startTime":None,"endTime":None,"type":None,"tags":None,"variable":None,"min":None,"max":None}
            template = {}
            try:
                for key in keys:
                    ch = anno.get_child(key)
                    if ch:
                        if key!="variable":
                            template[key]= ch.get_value()
                        else:
                            #logger.debug("var")
                            template[key] = ch.get_target_ids()
                if first:
                    f.write("[\n")
                    first=False
                else:
                    f.write(",\n")
                f.write(json.dumps(template))
            except Exception as ex:
                logger.warning(f"problem with anno {anno.get_browse_path()}, {ex}")

    f.write("]")
    f.close()
    return True


def annotation_import_function(functionNode):
    logger = functionNode.get_logger()
    model = functionNode.get_model()
    progressNode = functionNode.get_child("control").get_child("progress")
    signalNode = functionNode.get_child("control").get_child("signal")
    fileName = functionNode.get_child("fileName").get_value()
    if os.path.isabs(fileName):
        absPath = fileName
    else:
        if not fileName.endswith(".json"):
            fileName = fileName+".json"
        absPath = model.get_upload_folder_path()+"/"+ fileName

    f=open(absPath,"r")
    data = json.loads(f.read())
    f.close()

    targetFolder = functionNode.get_child("targetFolder").get_target()
    progressOld = 0
    model.disable_observers()
    for idx,anno in enumerate(data):
        progress = float(int(50 * idx / len(data))) / 50
        if progress != progressOld:
            progressNode.set_value(progress)
            progressOld = progress
            if signalNode.get_value() == "stop":
                break
        treeAnno = targetFolder.create_child(name=getRandomId(),type="annotation")

        for k,v in anno.items():
            if k !="variable":
                treeAnno.create_child(name=k,type="const",value=v)
            else:
                variable = treeAnno.create_child(name=k,type="referencer")
                if functionNode.get_child("importReferences").get_value():
                    try:
                        targetNodes = [ model.get_node(id) for id in v if model.get_node(id)]
                        variable.add_references(targetNodes)
                    except Exception as ex:
                        logger.error(f"problem during import anno {ex}")
    model.enable_observers()

    #now integrate them into the widget
    #first find all tags in the imported annos
    newTags = set()
    for anno in data:
        if "tags" in anno:
            for tag in anno["tags"]:
                newTags.add(tag)

    cols = ["#050F2C", "#003666", "#00AEFF", "#3369E7", "#8E43E7", "#B84592", "#FF4F81", "#FF6C5F", "#FFC168", "#2DDE98", "#1CC7D0"]
    # from http://brandcolors.net/ algolia
    for widget in functionNode.get_child("widgets").get_targets():
        #get the current colors
        colors = widget.get_child("hasAnnotation.colors").get_value()
        visibleTags = widget.get_child("hasAnnotation.visibleTags").get_value()
        tags = widget.get_child("hasAnnotation.tags").get_value()
        print("before",colors, visibleTags)
        for idx,tag in enumerate(newTags):
            if tag in colors:
                continue # we have this already
            else:
                #must add the tag
                colors[tag]={"color":cols[idx%11], "pattern":None}
                visibleTags[tag]=False
                tags.append(tag)

        print(colors,visibleTags)
        model.disable_observers()
        widget.get_child("hasAnnotation.visibleTags").set_value(visibleTags)
        widget.get_child("hasAnnotation.tags").set_value(tags)
        model.enable_observers()
        widget.get_child("hasAnnotation.colors").set_value(colors)
    return True