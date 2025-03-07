#21datalabplugin
import numpy
from system import __functioncontrolfolder
from model import date2secs
import pandas
import os
import time
from dateutil.parser import parse
from pytz import timezone
import dateutil
import model
import json
import traceback


csvreaderTemplate = {
    "name":"csvReader",
    "type":"function",
    "functionPointer":"csvreader.reader",   #filename.functionname
    "autoReload":True,                                 #set this to true to reload the module on each execution
    "children":[
        {"name":"fileFilter","type":"const","value":"myfiles"},                  # a string match filter: this string must be contained in a filename to be accepted
        {"name":"processedFiles","type":"variable","value":[]},                         # hold a list of files which we have done already
        {"name":"table","type":"referencer"},                                           # pointer to table to insert into
        {"name":"variablesFolder","type":"referencer"},                                 # folder to put the variables
        __functioncontrolfolder
    ]
}

def columns_renamer(name):
    return name.replace('.','_')



def reader(functionNode):
    logger = functionNode.get_logger()
    logger.info("==>>>> in raw_reader_2  "+functionNode.get_browse_path())

    full_path = os.path.realpath(__file__)
    path, filename = os.path.split(full_path)
    folder = path+r'\..\upload'
    m = functionNode.get_model()

    signalNode = functionNode.get_child("control").get_child("signal")
    signalNode.set_value("nosignal")

    varFolder = functionNode.get_child("variablesFolder").get_targets()[0] # we expect a direct link to the folder where to place the new variables
    fileNameMatch = functionNode.get_child("fileFilter").get_value()
    progressNode = functionNode.get_child("control").get_child("progress")
    localtz = timezone('Europe/Berlin')

    fileNames = os.listdir(folder)
    #fileNames = [r'20190805_TempSenMachine_1.dat',r'20190805_TempSenMachine_3.dat',r'20190805_TempSenMachine_2.dat']

    for idx,fileName in enumerate(fileNames):
        progressNode.set_value(round(idx/len(fileNames),2))
        if fileNameMatch not in fileName:
            logger.debug(f"skip file {fileName}, not match")
            continue # this file will be ignored
        if fileName in functionNode.get_child("processedFiles").get_value():
            logger.debug(f"skip file {fileName}, already done ")
            continue
        try:
            # now open the file, read it in
            fullFileName = folder+"\\"+fileName
            logger.info(f"processing {fullFileName}")
            data = pandas.read_csv(fullFileName, sep=",")
            data.rename(columns_renamer,axis="columns",inplace=True)

            #first the times

            cols = list(data.columns)
            times = []
            for dateString in data[cols[0]]:
                mydate = dateutil.parser.parse(dateString,dayfirst=True)
                try:
                    mydateAware = localtz.localize(mydate)
                except:
                    mydateAware = mydate # is already localized

                epoch = model.date2secs(mydateAware)
                times.append(epoch)

            drops = []
            for col in cols[1:]:
                try:
                    values = numpy.asarray(data[col], dtype=numpy.float64)
                except:
                    print(f"could not convert column {col}")
                    drops.append(col)
                    continue
                # print(values)
                values[numpy.isfinite(values) == False] = numpy.nan  # set all not finites to +numpy.nan
                data[col] = values
            data = data.drop(columns=drops)
            cols = list(data.columns)

            # in the file, the variables only have a single, unique name, now we need to find the matches in the table
            # so we will iterate over all columns of the table and try to match the sensor names of the file to the variables
            # by looking at the actual name of the node, we don't care where the nodes reside, just the name of the nodes must match

            #build a look up to speed up things
            existingColumns = {}
            for columnNode in functionNode.get_child("variablesFolder").get_leaves():
                existingColumns[ columnNode.get_name() ] = columnNode



            #now insert
            for col in cols[1:]:
                if signalNode.get_value()=="stop":
                    raise Exception("user stop")
                if col in existingColumns:
                    mynode = existingColumns[col]
                else:
                    mynode = varFolder.create_child(col,properties={"tsAllocSize":100000,"type":"timeseries"})

                m.disable_observers()
                res = mynode.insert_time_series(times=times, values = data[col])
                m.enable_observers()
                logger.debug(f"inserting {len(data[col])} on node {mynode.get_browse_path()}, result = {res}")
        except Exception as ex:
            print(f"can't import file {fileName}, {ex}")
            if signalNode.get_value()=="stop":
                break
            continue

    #remember  these files done
    doneFilesList = functionNode.get_child("processedFiles").get_value()
    doneFilesList.extend(fileNames)
    functionNode.get_child("processedFiles").set_value(doneFilesList)  # remember the files




    return True

