#21datalabplugin
import numpy
from system import __functioncontrolfolder
from model import date2secs, secs2dateString, date2msecs
import dates
import copy
import remote
import pandas as pd
from remote import RemoteModel
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as plotdates
import stumpy as stp
import scipy as scy

# use a list to avoid loading of this in the model as template
mycontrol = [copy.deepcopy(__functioncontrolfolder)]
mycontrol[0]["children"][-1]["value"]="threaded"

stumpyMinerTemplate = {
    "name": "StumpyMiner",
    "type": "folder",
    "children":[
        {
            "name": "StumpyStump",
            "type": "function",
            "functionPointer": "stumpyAlgorithm.minerStumpy",  # filename.functionname
            "autoReload": True,  # set this to true to reload the module on each execution
            "children": [
                {"name": "motif", "type": "referencer"},        # the one motif we are using
                {"name": "widget","type":"referencer"} ,        # the widget to which this miner belongs which is used (to find the selected motif
                {"name": "annotations","type":"folder"},        # the results
                {"name": "results","type":"variable"},          # list of results
                {"name": "Patternlength", "type": "variable", "value": 4},
                {"name": "maxNumberOfMatches","type":"const","value":20},      # the maximum number of matches to avoid massive production of annotations
                mycontrol[0]
            ]
        },
        {
            "name": "StumpyMASS",
            "type": "function",
            "functionPointer": "stumpyAlgorithm.minerMass",  # filename.functionname
            "autoReload": True,  # set this to true to reload the module on each execution
            "children": [
                {"name": "motif", "type": "referencer"},  # the original pattern to look for
                {"name": "widget","type":"referencer"} ,        # the widget to which this miner belongs which is used (to find the selected motif
                {"name": "annotations","type":"folder"},        # the results
                {"name": "results","type":"variable"},          # list of results
                {"name": "maxNumberOfMatches", "type": "const", "value": 10},  # the detection threshold
                mycontrol[0]
            ]
        },
        {
            "name": "update",
            "type": "function",
            "functionPointer": "stumpyAlgorithm.update",  # filename.functionname
            "autoReload": True,  # set this to true to reload the module on each execution
            "children": [
                {"name":"autoStepSize","type":"const","value":True},        #set this to true to autoset the step size of the motif
                __functioncontrolfolder
            ]
        },
        {
            "name": "show",
            "type": "function",
            "functionPointer": "stumpyAlgorithm.show",  # filename.functionname
            "autoReload": True,  # set this to true to reload the module on each execution
            "children": [
                __functioncontrolfolder
            ]
        },
        {
            "name": "hide",
            "type": "function",
            "functionPointer": "stumpyAlgorithm.hide",  # filename.functionname
            "autoReload": True,  # set this to true to reload the module on each execution
            "children": [
                __functioncontrolfolder
            ]
        },
        {
            "name": "select",
            "type": "function",
            "functionPointer": "stumpyAlgorithm.select",  # filename.functionname
            "autoReload": True,  # set this to true to reload the module on each execution
            "children": [
                __functioncontrolfolder
            ]
        },
        {
            "name": "delete",
            "type": "function",
            "functionPointer": "stumpyAlgorithm.delete",  # filename.functionname
            "autoReload": True,  # set this to true to reload the module on each execution
            "children": [
                __functioncontrolfolder
            ]
        },
        {
            "name": "jump",
            "type": "function",
            "functionPointer": "stumpyAlgorithm.jump",  # filename.functionname
            "autoReload": True,  # set this to true to reload the module on each execution
            "children": [
                {"name":"match","type":"variable"},
                __functioncontrolfolder
            ]
        },
        {
            "name": "init",
            "type": "function",
            "functionPointer": "stumpyAlgorithm.init",  # filename.functionname
            "autoReload": True,  # set this to true to reload the module on each execution
            "children": [
                __functioncontrolfolder
            ]
        },
        {
            "name": "progress",
            "type": "observer",
            "children": [
                {"name": "enabled", "type": "const", "value": True},  # turn on/off the observer
                {"name": "triggerCounter", "type": "variable", "value": 0},  # increased on each trigger
                {"name": "lastTriggerTime", "type": "variable", "value": ""},  # last datetime when it was triggered
                {"name": "targets", "type": "referencer","references":["StumpyMiner.StumpyMASS.control.progress"]},  # pointing to the nodes observed
                {"name": "properties", "type": "const", "value": ["value"]},
                # properties to observe [“children”,“value”, “forwardRefs”]
                {"name": "onTriggerFunction", "type": "referencer"},  # the function(s) to be called when triggering
                {"name": "triggerSourceId", "type": "variable"},
                # the sourceId of the node which caused the observer to trigger
                {"name": "hasEvent", "type": "const", "value": True},
                # set to event string iftrue if we want an event as well
                {"name": "eventString", "type": "const", "value": "StumpyAlgorithm.progress"},  # the string of the event
                {"name": "eventData", "type": "const", "value": {"text": "observer status update"}}
                # the value-dict will be part of the SSE event["data"] , the key "text": , this will appear on the page,
            ]
        },
        {
            "name": "userInteraction",
            "type": "observer",
            "children": [
                {"name": "enabled", "type": "const", "value": False},  # turn on/off the observer
                {"name": "triggerCounter", "type": "variable", "value": 0},  # increased on each trigger
                {"name": "lastTriggerTime", "type": "variable", "value": ""},  # last datetime when it was triggered
                {"name": "targets", "type": "referencer"},  # pointing to the nodes observed
                {"name": "properties", "type": "const", "value": ["value"]},
                {"name": "onTriggerFunction", "type": "referencer"},  # the function(s) to be called when triggering
                {"name": "triggerSourceId", "type": "variable"},
                {"name": "hasEvent", "type": "const", "value": True},
                {"name": "eventString", "type": "const", "value": "global.timeSeries.values"},  # the string of the event
                {"name": "eventData", "type": "const", "value": {"text": ""}}
            ]
        },
        {
            "name": "userSelectMotif",
            "type": "observer",
            "children": [
                {"name": "enabled", "type": "const", "value": False},  # turn on/off the observer
                {"name": "triggerCounter", "type": "variable", "value": 0},  # increased on each trigger
                {"name": "lastTriggerTime", "type": "variable", "value": ""},  # last datetime when it was triggered
                {"name": "targets", "type": "referencer"},  # pointing to the nodes observed
                {"name": "properties", "type": "const", "value": ["forwardRefs"]},
                {"name": "onTriggerFunction", "type": "referencer"},  # the function(s) to be called when triggering
                {"name": "triggerSourceId", "type": "variable"},
                {"name": "hasEvent", "type": "const", "value": True},
                {"name": "eventString", "type": "const", "value": "StumpyMiner.selectMotif"},
                # the string of the event
                {"name": "eventData", "type": "const", "value": {"text": ""}}
            ]
        },
        {
            "name": "userChangeMotifSize",
            "type": "observer",
            "children": [
                {"name": "enabled", "type": "const", "value": False},  # turn on/off the observer
                {"name": "triggerCounter", "type": "variable", "value": 0},  # increased on each trigger
                {"name": "lastTriggerTime", "type": "variable", "value": ""},  # last datetime when it was triggered
                {"name": "targets", "type": "referencer"},  # pointing to the nodes observed
                {"name": "properties", "type": "const", "value": ["value"]},
                {"name": "onTriggerFunction", "type": "referencer","references":["StumpyMiner.recreate"]},  # the function(s) to be called when triggering
                {"name": "triggerSourceId", "type": "variable"},
                {"name": "hasEvent", "type": "const", "value": False},
                {"name": "eventString", "type": "const", "value": "StumpyMiner.motifSize"},
                # the string of the event
                {"name": "eventData", "type": "const", "value": {"text": ""}}
            ]
        },


        {"name":"defaultParameters","type":"const","value":{"filter":[0,20,2],"samplingPeriod":[1,60,10],"freedom":[0,1,0.3],"dynamicFreedom":[0,1,0.5],"numberSamples":[1,100,1],"step":[0,1,0.1]}}, # the default contain each three values: min,max,default
        {"name": "cockpit", "type": "const", "value": "/customui/stumpyminer.htm"}  #the cockpit for the motif miner
    ]
}
def my_date_format(epoch):
    dat = dates.epochToIsoString(epoch,zone='Europe/Berlin')
    my = dat[0:10]+"&nbsp&nbsp"+dat[11:19]
    return my

def stumpy_mass_min(querySeriesValues, timeSeriesValues):
    distance_profile = stp.core.mass(querySeriesValues, timeSeriesValues)
    min = numpy.argsort(distance_profile)
    return min

def stumpy_mass_hits(querySeriesValues, timeSeriesValues):
    """
    :param querySeries: a subsequence (e.g., motif annotation) of the full time series - named query
    :param timeSeries: a time series (full time series) - given as numpy series
    :return: distance profile - as numpy.ndarray
    """
    distance_profile = stp.core.mass(querySeriesValues, timeSeriesValues)
    print('finished - tpye:  ', type(distance_profile))
    idx = numpy.argmin(distance_profile)
    numpy.sort(distance_profile)
    idx_sorted = numpy.argsort(distance_profile)
    # nearest neightbor to query (subsequence) is at idx position
    #return idx
    return idx_sorted

    # optional usage for local plotting
def stumpy_stump_print_z_normalized(fullTimeSeriesValues, fullTimeSeriesTimes, patternLength, idxMotif, idxNearestN):
    """
    :param querySeries: a subsequence (motif), which is a subsequence of the full time series (like mass)
    :param timeSeries: a time series (full time series)  (like mass)
    :param idx: index - position nearest neightbor to query (result of stumpy_mass function
    :return:
    """
    #plt.rcParams["figure.figsize"] = [20, 6]  # width, height
    plt.rcParams['xtick.direction'] = 'out'
    motif1Values = fullTimeSeriesValues[idxMotif:idxMotif+patternLength]
    motif2Values = fullTimeSeriesValues[idxNearestN: idxNearestN+patternLength]
    motif1Norm = stp.core.z_norm(motif1Values)
    motif2Norm = stp.core.z_norm(motif2Values)
    fullTimeSeriesNorm = stp.core.z_norm(fullTimeSeriesValues)
    fig = plt.figure()
    plt.suptitle('Comparing all similarities', fontsize='30')
    plt.xlabel('Time', fontsize ='20')
    plt.ylabel('Motif Variable', fontsize='20')
    plt.plot(fullTimeSeriesNorm, lw=2, color = "grey", label="Time series")
    plt.plot(motif1Norm, lw=2, color="red", label="Motif")
    plt.plot(motif2Norm, lw=2, color="orange", label="Motif Nearest")
    plt.legend()
    plt.savefig('Stump_Motif.png')
    plt.close(fig)
    return True

    # optional usage for local plotting
def stumpy_print_z_normalized(querySeriesValues, timeSeriesValues, timeSeriesTimes, idx):
    """
    :param querySeries: a subsequence (motif), which is a subsequence of the full time series (like mass)
    :param timeSeries: a time series (full time series)  (like mass)
    :param idx: index - position nearest neightbor to query (result of stumpy_mass function
    :return:
    """
    plt.rcParams['xtick.direction'] = 'out'
    # Since MASS computes z-normalized Euclidean distances,
    # we should z-normalize our subsequences before plotting
    querylength = querySeriesValues.size
    querySeriesValues_norm = stp.core.z_norm(querySeriesValues)
    timeSeriesValues_norm = stp.core.z_norm(timeSeriesValues[idx:idx+querylength])
    fig = plt.figure()
    plt.suptitle('Comparing The Query To Its Nearest Neighbor', fontsize='30')
    plt.xlabel('Time', fontsize ='20')
    plt.ylabel('Motif Variable', fontsize='20')
    plt.plot(timeSeriesValues_norm, lw=2, color = "red", label="Nearest Neighbor")
    plt.plot(querySeriesValues_norm, lw=2, color="blue", label="Query , querySeries")
    plt.legend()
    plt.savefig('MassRest_Light.png')
    plt.close(fig)
    return True


def stumpy_print_z_normalized_labeled_2_axis(querySeriesValues, timeSeriesValues, timeSeriesTimes, idx, label, varName):
    """
    :param querySeries: a subsequence (motif), which is a subsequence of the full time series (like mass)
    :param timeSeries: a time series (full time series)  (like mass)
    :param idx: index - position nearest neightbor to query (result of stumpy_mass function
    :param label: string as a name or label for the figure
    :param varName: string that represents the name of the variable
    :return:
    """
    # Since MASS computes z-normalized Euclidean distances,
    # we should z-normalize our subsequences before plotting
    querylength = querySeriesValues.size

    querySeriesValues_z_norm = stp.core.z_norm(querySeriesValues)
    timeSeriesValues_z_norm = stp.core.z_norm(timeSeriesValues)
    timeSeriesValues = timeSeriesValues
    fig, ax1  = plt.subplots()
    ax1.set_xlabel('Time', fontsize ='12')
    ax1.set_ylabel('Motif / query ', fontsize='12', color = 'blue')
    ax1.plot(querySeriesValues_z_norm, lw=2, color="blue", label="Query z-norm")
    ax1.tick_params(axis='y', labelcolor='blue')

    ax2 = ax1.twinx()   ### instantiate a scondary axis that shares the same x-axis
    ax2.set_ylabel('TS match (excerpt TS)', fontsize='12', color = 'red')
    ax2.plot(timeSeriesValues_z_norm, lw=2, color = "red", label="TS z-norm")
    ax2.tick_params(axis='y', labelcolor='red')
    fig.tight_layout()   # otherwise the right y-label is slightly clipped

    plt.legend()
    plt.savefig('MASS_4/Z_norm_cross_norm' + varName + '_' + label + '.png')
    plt.close(fig)
    fig, ax1 = plt.subplots()
    ax1.set_xlabel('Time', fontsize='12')
    ax1.set_ylabel('Motif / query ', fontsize='12', color='blue')
    ax1.plot(querySeriesValues, lw=2, color="blue", label="Query z-norm")
    ax1.tick_params(axis='y', labelcolor='blue')

    ax2 = ax1.twinx()  ### instantiate a scondary axis that shares the same x-axis
    ax2.set_ylabel('TS match (excerpt TS)', fontsize='12', color='red')
    ax2.plot(timeSeriesValues[idx:idx+querylength], lw=2, color="red", label="TS z-norm")
    ax2.tick_params(axis='y', labelcolor='red')
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.legend()
    plt.savefig('MASS_4/ORIG_cross_norm' + varName + '_' + label + '.png')
    plt.close(fig)
    return True

def stumpy_print_z_normalized_labeled_1_axis(querySeriesValues, timeSeriesValues, timeSeriesTimes, idx, label, varName):
    querylength = querySeriesValues.size
    querySeriesValues_z_norm = stp.core.z_norm(querySeriesValues)
    timeSeriesValues_z_norm = stp.core.z_norm(timeSeriesValues)
    timeSeriesValues = timeSeriesValues
    fig = plt.figure()
    plt.suptitle('Comparing The Query To Its Nearest Neighbor', fontsize='11')
    plt.xlabel('Time', fontsize ='11')
    plt.ylabel('Motif Variable', fontsize='11')
    plt.plot(timeSeriesValues_z_norm, lw=2, color = "red", label="Nearest Neighbor")
    plt.plot(querySeriesValues_z_norm, lw=2, color="blue", label="Query , querySeries")
    plt.legend()
    plt.savefig('MASS_4/1_Axis_Z_norm_cross_norm' + varName + '_' + label + '.png')
    plt.close(fig)
    return True

def stumpy_stump(timeSeries, patternLength):
    """
    :param timeSeries: a time series given as numpy series
    :param patternLength: length of the pattern for similarity, i.e., the size of the search window (sliding window) as integer
    :return: the motif index
      Note: The motif index is the result based on
      the z-normalized matrix profile (first column: matrix profile, second column: indices of each profile,
               third column: indices of left (next) profile, fourth column: indices of right (next) profile
                       (--> all indices refer to the timeSeries, which is the full time series)
    """
    matrixProfile = stp.stump(timeSeries, patternLength)
    motifIndex = numpy.argsort(matrixProfile[:, 0])[0]
    #  sort all z-normalized distances (first column) and select the lowest value (--> best match)
    print('motif index is : ', motifIndex, ' and nearest neightbor is: ' ,matrixProfile[motifIndex,1])
    stumpy_stump_print_z_normalized(timeSeries, patternLength, motifIndex, matrixProfile[motifIndex,1])
    return motifIndex


def minerStump(functionNode):
    logger = functionNode.get_logger()
    logger.info("==>>>> in stumpy stump miner " + functionNode.get_browse_path())
    signal = functionNode.get_child("control.signal")
    progressNode = functionNode.get_child("control").get_child("progress")
    progressNode.set_value(0)
    signal.set_value(None)
    functionNode.get_child("results").set_value([])
    functionNode.get_child("results").set_value([])
    model=functionNode.get_model()  ## is occupancyDemo
    motifNode = functionNode.get_child("motif").get_target()
    varNode = motifNode.get_child("variable").get_target()   ### variable
    startTime = motifNode.get_child("startTime").get_value()
    endTime = motifNode.get_child("endTime").get_value()
    timeSeries = varNode.get_time_series(start=startTime, end=endTime)
    patternlength = functionNode.get_child("Patternlength").get_value()
    if functionNode.get_child("maxNumberOfMatches"):
        maxMatches = functionNode.get_child("maxNumberOfMatches").get_value()
    else:
        maxMatches = None
    fullTimeSeries = varNode.get_time_series()
    fullTimeSeriesValues = fullTimeSeries['values']
    stumpIndex = stumpy_stump(fullTimeSeriesValues, patternlength)
    print("index position:  ", stumpIndex)
    return True

    #  the modified implementation of the minerMass algorithm SPLITS the full time series
    # into the part before the motif and the part after the motif
def minerMass(functionNode):
    logger = functionNode.get_logger()
    logger.info("==>>>> in stumpy mass split miner " + functionNode.get_browse_path())
    progressNode = functionNode.get_child("control").get_child("progress")
    progressNode.set_value(0)
    signal = functionNode.get_child("control.signal")
    signal.set_value(None)
    functionNode.get_child("results").set_value([])
    motifNode = functionNode.get_child("motif").get_target()
    varNode = motifNode.get_child("variable").get_target()
    startTime = motifNode.get_child("startTime").get_value()
    endTime = motifNode.get_child("endTime").get_value()
    if functionNode.get_child("maxNumberOfMatches"):
        maxMatches = functionNode.get_child("maxNumberOfMatches").get_value()
    else:
        maxMatches = None
    maxMatches_before = round(maxMatches/4)   # roughly 25 % of the matches will be in the pattern before the motif
    maxMatches_after = round(maxMatches/4 * 3)     # the remaining matches are afterwards
    queryTimeSeries = varNode.get_time_series(start=startTime, end=endTime)
    fullTimeSeries = varNode.get_time_series()
    queryTimeSeriesTimes = queryTimeSeries['__time']
    fullTimeSeriesTimes = fullTimeSeries['__time']
    endLeftPartTs = (numpy.where(fullTimeSeriesTimes == queryTimeSeriesTimes[0]))[0][0]
    startRightPartTs = (numpy.where(fullTimeSeriesTimes == queryTimeSeriesTimes[len(queryTimeSeriesTimes) - 1]))[0][0]
    queryTimeSeriesValues = queryTimeSeries['values']
    queryLength = queryTimeSeriesValues.size
    fullTimeSeriesValues = fullTimeSeries['values']
    timeSeriesLeftValues = fullTimeSeriesValues[:endLeftPartTs]
    timeSeriesRightValues = fullTimeSeriesValues[startRightPartTs:]
    timeSeriesLeftTimes = fullTimeSeriesTimes[:endLeftPartTs]
    timeSeriesRightTimes = fullTimeSeriesTimes[startRightPartTs:]
    profile_before = stp.core.mass(queryTimeSeriesValues, timeSeriesLeftValues)
    profile_after = stp.core.mass(queryTimeSeriesValues, timeSeriesRightValues)
    maxValue_before = numpy.max(profile_before)
    profile_before = numpy.where(profile_before < 0.2, maxValue_before, profile_before)
    maxValue_after = numpy.max(profile_after)
    profile_after = numpy.where(profile_after < 0.2, maxValue_after, profile_after)
    # note: indexing on the right side starts at 0 --> thus we need an offset to add when moving back to the full sequence
    #   this offset is the index value in startRightPartTs   2.4
    peaks_before, _ = scy.signal.find_peaks(-profile_before, distance=round(queryLength / 2.4), width = round(queryLength / 13))
    peaks_after, _ = scy.signal.find_peaks(-profile_after, distance=round(queryLength / 2.4 ), width = round(queryLength / 13))
    profile_before_peaks = profile_before[peaks_before]
    profile_after_peaks = profile_after[peaks_after]
    sorted_peaks_before = numpy.argsort(profile_before_peaks)
    sorted_peaks_after = numpy.argsort(profile_after_peaks)
    # align peaks (before and after partitions) to the whole sequence
    sorted_peaks_full_before = []
    for idx_short in range(len(sorted_peaks_before)):
        sorted_peaks_full_before.append(peaks_before[sorted_peaks_before[idx_short]])
    sorted_peaks_full_after = []
    for idx_short in range(len(sorted_peaks_after)):
        sorted_peaks_full_after.append(peaks_after[sorted_peaks_after[idx_short]])
    matches = []
    i = 0
    last = 0
    below = 50
    above = 0
    for j in range(maxMatches_after):
        matches.append({
            "startTime": dates.epochToIsoString((timeSeriesRightTimes)[sorted_peaks_full_after[j]]),
            "endTime": dates.epochToIsoString((timeSeriesRightTimes)[sorted_peaks_full_after[j] + queryLength]),
            "match": (profile_after[peaks_after])[sorted_peaks_after[j]],
            #            "match": stp.core.z_norm((profile_after[peaks_after])[sorted_peaks_after[j]]),
            "epochStart": (timeSeriesRightTimes)[sorted_peaks_full_after[j]],
            "epochEnd": (timeSeriesRightTimes)[sorted_peaks_full_after[j] + queryLength],
            "offset": 0,
            "format": my_date_format(
                (timeSeriesRightTimes)[sorted_peaks_full_after[j]]) + "&nbsp&nbsp(match=%2.3f)" %
                      (profile_after[peaks_after])[sorted_peaks_after[j]]
        })
        progress = round(float(j) / maxMatches_after * 15)
        if progress != last:
            progressNode.set_value(float(j) / maxMatches_after)
            last = progress
        if signal.get_value() == "stop":
            break
    for j in range(maxMatches_before):
        matches.append({
            "startTime": dates.epochToIsoString((timeSeriesLeftTimes)[sorted_peaks_full_before[j]]),
            "endTime": dates.epochToIsoString((timeSeriesLeftTimes)[sorted_peaks_full_before[j] + queryLength]),
            #"match": (timeSeriesLeftValues)[sorted_peaks_before[j]],
            "match": (profile_before[peaks_before])[sorted_peaks_before[j]],
            #            "match": stp.core.z_norm((profile_before[peaks_before])[sorted_peaks_before[j]]),
            "epochStart": (timeSeriesLeftTimes)[sorted_peaks_full_before[j]],
            "epochEnd": (timeSeriesLeftTimes)[sorted_peaks_full_before[j] + queryLength],
            # "offset": fullTimeSeriesValuesMinima_norm[idxSortDistProfMinimaExc[j]],
            "offset": 0,
            "format": my_date_format(
                (timeSeriesLeftTimes)[sorted_peaks_full_before[j]]) + "&nbsp&nbsp(match=%2.3f)" %
                      (profile_before[peaks_before])[sorted_peaks_before[j]]
        })
        progress = round(float(j) / maxMatches_before * 15)
        if progress != last:
            progressNode.set_value(float(j) / maxMatches_before)
            last = progress
        if signal.get_value() == "stop":
            break
    functionNode.get_child("results").set_value(matches)
    show_timeseries_results(functionNode)
    progressNode.set_value(1)
    return True

def show_timeseries_results(functionNode):
    results = functionNode.get_child("results").get_value()
    motifNode = functionNode.get_child("motif").get_target()
    startTime = motifNode.get_child("startTime").get_value()
    endTime = motifNode.get_child("endTime").get_value()
    varNode = motifNode.get_child("variable").get_target()
    motifTimeSeries = varNode.get_time_series(start=startTime, end=endTime)
    varName = varNode.get_property("name")
    for child in functionNode.get_children():
        if child.get_name().endswith("_expected"):
            if not child.get_name().startswith(varName):
                child.delete()
    resultNode = functionNode.create_child(name=varName+'_expected', type="timeseries")
    resultNode.set_time_series([],[])
    cnt = 0
    for result in results:
        resultTimes = motifTimeSeries['__time']+result['epochStart']-date2secs(startTime)  # time + offset
        resultValues = (motifTimeSeries['values']).copy()
        lastIdx = len(resultTimes)-1
        ### for each result
        excerptFullTs = varNode.get_time_series(start=result['startTime'], end=result['endTime'])
        excerptFullTsValues = (excerptFullTs['values'])[:-1]
        excerptFullTsTimes = (excerptFullTs['__time'])[:-1]
        firstValueFullTs = excerptFullTsValues[0]
        firstValueMotif = resultValues[0]
        verticalDistance = firstValueFullTs - firstValueMotif
        #resultValuesNorm = min_max_norm_cross(resultValues, excerptFullTsValues, verticalDistance)
        #resultValuesNorm = resultValues + verticalDistanceAvg
        #resultValuesNorm = resultValues * verticalRatioAvg
        #resultValuesNorm = correlation_norm(resultValues, excerptFullTsValues)
        resultValuesNorm = mixed_norm_cross(resultValues, excerptFullTsValues)
        #resultValuesNorm = z_norm_cross(resultValues, excerptFullTsValues)
        #resultValuesNorm = min_max_norm_cross(resultValues, excerptFullTsValues, verticalDistance)
        # OPTIONAL - local plotting for debug
        #stumpy_print_z_normalized_labeled_2_axis(resultValuesNorm, excerptFullTsValues, excerptFullTsTimes, cnt, str(cnt), varName)
        #stumpy_print_z_normalized_labeled_1_axis(resultValuesNorm, excerptFullTsValues, excerptFullTsTimes, cnt, str(cnt), varName)
        resultValuesNormNan = resultValuesNorm.copy()
        resultValuesNormNan = numpy.insert(resultValuesNormNan,0, numpy.nan)
        resultValuesNormNan = numpy.append(resultValuesNormNan, numpy.nan)
        resultTimesNan = resultTimes.copy()
        resultTimesNan = numpy.insert(resultTimesNan, 0, resultTimes[0]+resultTimes[0]-resultTimes[1])
        resultTimesNan = numpy.append(resultTimesNan, resultTimes[lastIdx]+resultTimes[lastIdx]-resultTimes[lastIdx-1])
        cnt = cnt + 1
        resultNode.insert_time_series(values=resultValuesNormNan, times=resultTimesNan)
    widgetNode = functionNode.get_child("widget").get_target()
    widgetNode.get_child("selectedVariables").add_references(resultNode,allowDuplicates=False)

def hide_timeseries_results(functionNode, delete=False):
    for child in functionNode.get_children():
        if child.get_name().endswith("_expected"):
            widgetNode = functionNode.get_child("widget").get_target()
            widgetNode.get_child("selectedVariables").del_references(child)

def z_norm_cross(motifTsValues, excerptFullTsValues):
    avgFullTs = numpy.mean(excerptFullTsValues)
    varianceFullTs = numpy.var(excerptFullTsValues)
    return (motifTsValues - avgFullTs) / varianceFullTs

def correlation_norm(resultValues, excerptFullTsValues):
    cor = numpy.correlate(resultValues, excerptFullTsValues)
    cov = numpy.cov(resultValues, excerptFullTsValues)
    return (resultValues / cor)


def mixed_norm_cross(motifTsValues, excerptFullTsValues):
    avgFullTs = numpy.mean(excerptFullTsValues)
    medianFullTs = numpy.median(excerptFullTsValues)
    varianceFullTs = numpy.var(excerptFullTsValues)
    avgMotif = numpy.mean(motifTsValues)
    medianMotif = numpy.median(motifTsValues)
    varianceMotif = numpy.var(motifTsValues)
    cov = numpy.cov(motifTsValues, excerptFullTsValues, bias=True)[0][1]
    vertDist = motifTsValues - excerptFullTsValues
    #return (motifTsValues - (medianMotif - medianFullTs)) # / (varianceMotif) * (varianceFullTs)
    return (motifTsValues - (medianMotif - medianFullTs) - (vertDist - medianMotif + medianFullTs) * cov)
    #return (motifTsValues - (medianMotif - medianFullTs) - (vertDist - medianMotif + medianFullTs)/40)

def mean_norm(nanResultValues):
    averageVal = numpy.mean(nanResultValues)
    span = numpy.max(nanResultValues) - numpy.min(nanResultValues)
    res = nanResultValues - averageVal
    res = res / abs(span)
    return res

def min_max_norm(nanResultValues):
    v1 = nanResultValues - numpy.min(nanResultValues)
    divisor = (numpy.max(nanResultValues) - numpy.min(nanResultValues))
    res = v1 / divisor
    return res


def min_max_norm_cross(motifTsValues, excerptFullTsValues, verticalDistance):
    avgFullTs = numpy.mean(excerptFullTsValues)
    spanFullTs = numpy.max(excerptFullTsValues) - numpy.min(excerptFullTsValues)
    res = motifTsValues + verticalDistance
    res = res - avgFullTs
    res = res / abs(spanFullTs)
    return res


def enable_interaction_observer(functionNode):
    motif=functionNode.get_parent().get_child("StumpyMASS.motif").get_target()
    observer = functionNode.get_parent().get_child("userInteraction")
    observer.get_child("enabled").set_value(False)
    newRefs = [child for child in motif.get_child("envelope").get_children() if child.get_type()=="timeseries"]
    observer.get_child("targets").add_references(newRefs,deleteAll=True)
    observer.get_child("enabled").set_value(True)

def disable_interaction_observer(functionNode):
    observer = functionNode.get_parent().get_child("userInteraction")
    observer.get_child("enabled").set_value(False)

def enable_motif_select_observer(functionNode):
    disable_motif_select_observer(functionNode) #make sure all are initially off
    widget = functionNode.get_parent().get_child("StumpyMASS.widget").get_target()
    selected = widget.get_child("hasAnnotation.selectedAnnotations")
    selectObserver = functionNode.get_parent().get_child("userSelectMotif")
    selectObserver.get_child("targets").add_references([selected],deleteAll=True)
    selectObserver.get_child("enabled").set_value(True)
    #if there is a selected motif, initially trigger this to set the UI correctly
    if selected.get_targets()!=[]:
        model = functionNode.get_model()
        model.notify_observers(selected.get_id(), "forwardRefs")

def disable_motif_select_observer(functionNode):
    functionNode.get_parent().get_child("userSelectMotif").get_child("enabled").set_value(False)

def disable_motif_change_size_observer(functionNode):
    functionNode.get_parent().get_child("userChangeMotifSize").get_child("enabled").set_value(False)

def enable_motif_change_size_observer(functionNode,motif):
    observer = functionNode.get_parent().get_child("userChangeMotifSize")
    observer.get_child("enabled").set_value(False)
    observer.get_child("targets").add_references([motif.get_child("startTime")],deleteAll=True)
    observer.get_child("enabled").set_value(True)

def init(functionNode):
    logger = functionNode.get_logger()
    logger.debug("init")
    enable_motif_select_observer(functionNode)
    show_motifs(functionNode,True)
    return True

def hide_motif(functionNode):
    widget = functionNode.get_parent().get_child("StumpyMASS").get_child("widget").get_target()
    disable_interaction_observer(functionNode)
    disable_motif_select_observer(functionNode)
    disable_motif_change_size_observer(functionNode)
    #show_motifs(functionNode,False)
    motif = functionNode.get_parent().get_child("StumpyMASS").get_child("motif").get_target()
    return _connect(motif,widget,False)

def select(functionNode):
    logger = functionNode.get_logger()
    widget = functionNode.get_parent().get_child("StumpyMASS").get_child("widget").get_target()
    newMotif = widget.get_child("hasAnnotation").get_child("selectedAnnotations").get_target()
    if not newMotif:
        logger.error("no new motif given")
        return False
    motifPointer = functionNode.get_parent().get_child("StumpyMASS").get_child("motif")
    #if motifPointer.get_target():
    #    hide_motif(functionNode)
    motifPointer.add_references(newMotif,deleteAll=True)

    return True

def jump(functionNode):
    widget = functionNode.get_parent().get_child("StumpyMASS").get_child("widget").get_target()
    widgetStartTime = dates.date2secs(widget.get_child("startTime").get_value())
    widgetEndTime = dates.date2secs(widget.get_child("endTime").get_value())
    #now get the user selection, it will be the index of the results list
    matchIndex=int(functionNode.get_child("match").get_value())
    if matchIndex==-1:
        motif = functionNode.get_parent().get_child("StumpyMASS").get_child("motif").get_target()
        match = {}
        match["epochStart"] = dates.date2secs(motif.get_child("startTime").get_value())
        match["epochEnd"] = dates.date2secs(motif.get_child("endTime").get_value())
    else:
        results = functionNode.get_parent().get_child("StumpyMASS").get_child("results").get_value()
        match = results[matchIndex]
    middle = match["epochStart"]+(match["epochEnd"]-match["epochStart"])/2
    newStart = middle - (widgetEndTime-widgetStartTime)/2
    newEnd = middle + (widgetEndTime - widgetStartTime) / 2
    widget.get_child("startTime").set_value(dates.epochToIsoString(newStart))
    widget.get_child("endTime").set_value(dates.epochToIsoString(newEnd))
    return True

def display_matches(functionNode,on=True):
    return #Albert: we currently do not support display of annotations

def enable_show_motifs(functionNode):
    #switch on the motfs in the context menu
    widget = functionNode.get_parent().get_child("StumpyMASS.widget").get_target()

def show_motifs(functionNode,show):
    widget = functionNode.get_parent().get_child("StumpyMASS.widget").get_target()
    visibleElements = widget.get_child("visibleElements").get_value()
    if "motifs" not in visibleElements:
        return
    if show != visibleElements["motifs"]:
        visibleElements["motifs"]=show
        widget.get_child("visibleElements").set_value(visibleElements)
    return

def hide(functionNode):
    miningNode = functionNode.get_parent().get_child("StumpyMASS")
    hide_timeseries_results(miningNode)
    #hide_motif(functionNode)
    show_motifs(functionNode, False)

def _create_annos_from_matches(annoFolder,matches,maxMatches=None):
    for child in annoFolder.get_children():
        child.delete()
    if maxMatches == 0:
        return  #we don't write any annotation
    if maxMatches and maxMatches<len(matches):
        matches = matches[0:maxMatches]
    for m in matches:
        newAnno = annoFolder.create_child(type="annotation")
        anno = {"type":"time",
                "startTime":m["startTime"],
                "endTime":m["endTime"],
                "tags":["pattern_match"]}
        for k, v in anno.items():
            newAnno.create_child(properties={"name": k, "value": v, "type": "const"})

def delete(functionNode):
    hide_motif(functionNode)
    motif = functionNode.get_parent().get_child("StumpyMASS").get_child("motif").get_target()
    #motif.get_child("envelope").delete()
    #remove all envelope info from the motif
    return True

def _connect(motif,widget,connect=True):
    """
        we expect to find min and max, expected is optional
        connect = True for connect, False for disconnect
    """
    if not motif or not widget:
        return False
    try:
        lMax = None
        lMin = None
        exPe = None
        #children = motif.get_children()
        if motif.get_child("envelope"):
            for child in motif.get_child("envelope").get_children():
                if "_limitMax" in child.get_name():
                    lMax = child
                elif "_limitMin" in child.get_name():
                    lMin = child
                elif "_expected" in child.get_name():
                    exPe = child
            if connect:
                if lMax and lMin:
                    if exPe:
                        widget.get_child("selectedVariables").add_references([exPe,lMin,lMax],allowDuplicates=False)
                    else:
                        widget.get_child("selectedVariables").add_references([lMin, lMax],allowDuplicates=False)
            else:
                #disconnect
                elems = [elem for elem in [lMin,lMax,exPe] if elem] #remove the nones
                if elems:
                    widget.get_child("selectedVariables").del_references(elems)
        return True
    except Exception as ex:
        import traceback
        print(traceback.format_exc())
        return True

def update(functionNode,startTime=0):
    if functionNode.get_name()!="update":
        functionNode = functionNode.get_parent().get_child("update")
    motif = functionNode.get_parent().get_child("StumpyMASS").get_child("motif").get_target()
    widget = functionNode.get_parent().get_child("StumpyMASS").get_child("widget").get_target()
    logger = functionNode.get_logger()
    start = dates.date2secs(motif.get_child("startTime").get_value())
    end = dates.date2secs(motif.get_child("endTime").get_value())
    times = numpy.arange(start, end)
    ts = motif.get_child("variable").get_target().get_time_series(start,end,resampleTimes = times)
    data = ts["values"]
    if startTime!=0:
        diff = startTime-start
        times=times+diff
        #value offset
        ts =  motif.get_child("variable").get_target().get_time_series(resampleTimes = times)
        dataDiff = ts["values"][0]-data[0]
        data = data +dataDiff
    return True

def debug_help_vis(distance_profile, minimaRelPeakWD, idxSortDistProfMinimaExc):
    numpy.savetxt("profile.txt", distance_profile, delimiter=',')
    numpy.savetxt("minRelPeakWD.txt", minimaRelPeakWD, delimiter=',')
    numpy.savetxt("idxSotedProfExc.txt", idxSortDistProfMinimaExc, delimiter=',')
    return True


    #### currently as back-up

    #  the core / base  Stumpy MASS algorithm:
    #TODO rename  or remove -  original minerMass implementation without split
def minerMass_tmp(functionNode):
    logger = functionNode.get_logger()
    logger.info("==>>>> in stumpy mass restsequence miner " + functionNode.get_browse_path())
    progressNode = functionNode.get_child("control").get_child("progress")
    progressNode.set_value(0)
    signal = functionNode.get_child("control.signal")
    signal.set_value(None)
    functionNode.get_child("results").set_value([])
    update(functionNode)
    motifNode = functionNode.get_child("motif").get_target()
    varNode = motifNode.get_child("variable").get_target()
    startTime = motifNode.get_child("startTime").get_value()
    endTime = motifNode.get_child("endTime").get_value()
    timeSeries = varNode.get_time_series(start=startTime, end=endTime)
    fullTimeSeries = varNode.get_time_series()
    if functionNode.get_child("maxNumberOfMatches"):
        maxMatches = functionNode.get_child("maxNumberOfMatches").get_value()
    else:
        maxMatches = None
    queryLength = timeSeries['values'].size
    profile = stp.core.mass(timeSeries['values'], fullTimeSeries['values'])
    maxValue = numpy.max(profile)
    # remove 0 values
    profile = numpy.where(profile < 0.5, maxValue, profile) #
    # remove profile values of search pattern
    idx = numpy.argsort(profile, 10)[:10]
    idxs = idx[numpy.argsort(profile[idx])]
    peaks,_ = scy.signal.find_peaks(-profile, distance= round(queryLength / 4), width = round(numpy.median(profile)- 3*min(profile)))
    profile_peaks = profile[peaks]
    sorted_peaks =  numpy.argsort(profile_peaks)
    # iterate over all sorted peak indices to refer to the long indices (full time series):
    sorted_peaks_full_seq = []
    for idx_short in range(len(sorted_peaks)):
        sorted_peaks_full_seq.append(peaks[idx_short])
    # DEBUG HELP
    profile_idx_data = pd.DataFrame({"peaks": peaks, "profile_peaks": profile_peaks, "sorted_peaks": sorted_peaks, "sorted_peaks_full": sorted_peaks_full_seq})
    profile_idx_data.to_csv('DEBUG_index_profile_val.csv', decimal = ',',  sep = ';' , index=False)
    pd.DataFrame(profile).to_csv('DEBUG_complete_profile.csv', decimal = ',', sep = ';', index=False)


    matches = []
    i = 0
    last = 0
    below = 50
    above = 0
    for j in range(maxMatches):
        #fullTimeSeriesValuesMinima_norm = stp.core.z_norm(
        #    (fullTimeSeries['values'])[idxSortDistProfMinimaExc[j]:idxSortDistProfMinimaExc[j] + queryLength])
        #matches.append({
        #     "startTime": dates.epochToIsoString((fullTimeSeries['__time'])[peaked_profile[j]]),
        #     "endTime": dates.epochToIsoString((fullTimeSeries['__time'])[peaked_profile[j]+queryLength]),
        #     "match": profile[peaked_profile[j]],
        #     "epochStart": (fullTimeSeries['__time'])[peaked_profile[j]],
        #     "epochEnd": (fullTimeSeries['__time'])[peaked_profile[j]+queryLength],
        #     #"offset": fullTimeSeriesValuesMinima_norm[idxSortDistProfMinimaExc[j]],
        #     "offset": 0,
        #     "format": my_date_format((fullTimeSeries['__time'])[peaked_profile[j]])+"&nbsp&nbsp(match=%2.3f)"%profile[peaked_profile[j]]
        # })
        matches.append({
            "startTime": dates.epochToIsoString((fullTimeSeries['__time'])[sorted_peaks_full_seq[j]]),
            "endTime": dates.epochToIsoString((fullTimeSeries['__time'])[sorted_peaks_full_seq[j]+queryLength]),
            "match": (profile[peaks])[sorted_peaks[j]],
            "epochStart": (fullTimeSeries['__time'])[sorted_peaks_full_seq[j]],
            "epochEnd": (fullTimeSeries['__time'])[sorted_peaks_full_seq[j]+queryLength],
            #"offset": fullTimeSeriesValuesMinima_norm[idxSortDistProfMinimaExc[j]],
            "offset": 0,
            "format": my_date_format((fullTimeSeries['__time'])[sorted_peaks_full_seq[j]])+"&nbsp&nbsp(match=%2.3f)"%(profile[peaks])[sorted_peaks[j]]
        })
        progress = round(float(j)/maxMatches * 20)
        if progress != last:
            progressNode.set_value(float(j)/maxMatches)
            last = progress
        if signal.get_value() == "stop":
            break
    functionNode.get_child("results").set_value(matches)
    show_timeseries_results(functionNode)
    progressNode.set_value(1)
    return True
