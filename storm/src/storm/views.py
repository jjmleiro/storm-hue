#encoding:utf-8

#!/usr/bin/env python
## Licensed to the Apache Software Foundation (ASF) under one
## or more contributor license agreements.  See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  The ASF licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
## http:# www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.

try:
    import simplejson as json
except ImportError:
    import json
    print ImportError

import os
import commands
import requests
from django.template import RequestContext
from django.core.files.base import ContentFile
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse, HttpResponseRedirect
from desktop.lib.django_util import render  
from desktop.lib.exceptions_renderable import PopupException
from storm import settings
from storm.conf import SERVER
from storm.forms import UploadFileForm, UploadFileFormHDFS 

SYSTEM_STATS = "?sys=1"
API_URL = "/api/v1"
LOG_URL_PATH = "/log?file=worker-"
STORM_UI_SERVER = "http://" + SERVER.STORM_UI_SERVER.get() + ":" + SERVER.STORM_UI_PORT.get()
STORM_UI = STORM_UI_SERVER + API_URL
TOPOLOGIES_URL = STORM_UI + SERVER.STORM_UI_TOPOLOGIES.get()
TOPOLOGY_URL = STORM_UI + SERVER.STORM_UI_TOPOLOGY.get()
CLUSTER_URL = STORM_UI + SERVER.STORM_UI_CLUSTER.get()
SUPERVISOR_URL = STORM_UI + SERVER.STORM_UI_SUPERVISOR.get()
CONFIGURATION_URL = STORM_UI + SERVER.STORM_UI_CONFIGURATION.get()
LOG_URL = "http://" + SERVER.STORM_UI_SERVER.get() + ":" + SERVER.STORM_UI_LOG_PORT.get() + LOG_URL_PATH

# *************************************************************************************************************************
# **********                                                                                                     **********
# **********                                                                                                     **********
# **********                                          VIEWS.                                                     **********
# **********                                                                                                     **********
# **********                                                                                                     **********
# *************************************************************************************************************************

# storm_dashboard *********************************************************************************************************
# Rev Date       Author
# --- ---------- ----------------------------------------------------------------------------------------------------------
# 001 2014-11-11 Jose Juan
#
# Index of application.
#
# @author Jose Juan
# @date 2014-11-11
# @param request, HTTPRequest.
# @return -
# @remarks -
#
def storm_dashboard(request):
    sStatus = ""  
    iActive = 0
    iInactive = 0
    iExecutors = 0
    iWorkers = 0
    iTasks = 0      
    form = ""
    aData = []        
  
    jsonTopology = get_json(TOPOLOGIES_URL)    
    
    if (len(jsonTopology) > 0):
  
        try:
            aData = jsonTopology["topologies"]        
        except:
            aData = []
     
        if (len(aData) > 0):                           
            for row in aData:       
                row.update({'seconds': get_seconds_from_strdate(row["uptime"]) })
                sStatus = row["status"]
                                        
                if (sStatus == "ACTIVE"):
                    iActive += 1
                else:   
                    iInactive += 1
       
                iExecutors += row["executorsTotal"]
                iWorkers += row["workersTotal"]
                iTasks += row["tasksTotal"]                                                              
  
  
    return render('storm_dashboard.mako', request, {'user': request.user,
                                                    'Topologies': aData,
                                                    'Active': iActive,
                                                    'Inactive': iInactive,
                                                    'Executors': iExecutors,
                                                    'Workers': iWorkers,
                                                    'Tasks': iTasks,
                                                    'frmNewTopology': get_newform(request, UploadFileForm),
                                                    'frmHDFS': get_newform(request, UploadFileFormHDFS)                                                  
                                                    })
#
# storm_dashboard *********************************************************************************************************

# detail_dashboard ********************************************************************************************************
# Rev Date       Author
# --- ---------- ----------------------------------------------------------------------------------------------------------
# 001 2014-11-19 Jose Juan
#
# Control Panel of a topology (Dashboard).
#
# @author Jose Juan
# @date 2014-11-19
# @param request, HTTPRequest.
# @param topology_id, topology id.
# @param system_id, show/hide system stats.
# @return -
# @remarks -
#
def detail_dashboard(request, topology_id, system_id):
    aTopology = []
    aStats = []
    aSpouts = []
    aBolts = []
    aEmitted = []
    aTransferred = []
    aAcked = []
    aFailed = []
    iEmitted = 0
    iTransferred = 0
    iAcked = 0
    iFailed = 0    
    iSystem = int(system_id) if system_id is not None else 0
  
    jsonTopology = get_json(TOPOLOGY_URL + topology_id + SYSTEM_STATS) if (iSystem == 1) else get_json(TOPOLOGY_URL + topology_id)      
  
    iSystem = 1 if (iSystem == 0) else 0
  
    jsonTopologyVisualization = get_json(TOPOLOGY_URL + topology_id + '/visualization')
    jsonVisualization = get_dumps(jsonTopologyVisualization)        
  
    if (len(jsonTopology) > 0):     
        aTopology = get_topology(topology_id)
     
        try:
            aStats = jsonTopology["topologyStats"]
        
            if (len(aStats) == 1):        
                if (aStats[0]["failed"] is None):
                    aStats = []        
        except:
            aStats = []
     
        try:   
            aSpouts = jsonTopology["spouts"]
            
            if (aSpouts[0]["transferred"] is None):
                aSpouts = []
                    
        except:
            aSpouts = []
        
        try:
            aBolts = jsonTopology["bolts"]
            
            if (aBolts[0]["transferred"] is None):
                aBolts = []
                              
        except:
            aBolts = []
             
        for p in aStats:       
            iEmitted+=p["emitted"] if p["emitted"] is not None else 0
            iTransferred+=p["transferred"] if p["transferred"] is not None else 0
            iAcked+=p["acked"] if p["acked"] is not None else 0
            iFailed+=p["failed"] if p["failed"] is not None else 0
     
        aEmitted.append(iEmitted)     
        aTransferred.append(iTransferred)     
        aAcked.append(iAcked)     
        aFailed.append(iFailed)     
          
        iEmitted = 0
        iTransferred = 0
        iAcked = 0
        iFailed = 0
     
        for p in aSpouts:       
            iEmitted+=p["emitted"] if p["emitted"] is not None else 0
            iTransferred+=p["transferred"] if p["transferred"] is not None else 0
            iAcked+=p["acked"] if p["acked"] is not None else 0
            iFailed+=p["failed"] if p["failed"] is not None else 0
     
        aEmitted.append(iEmitted)     
        aTransferred.append(iTransferred)     
        aAcked.append(iAcked)     
        aFailed.append(iFailed)
     
        iEmitted = 0
        iTransferred = 0
        iAcked = 0
        iFailed = 0
     
        for p in aBolts:       
            iEmitted+=p["emitted"] if p["emitted"] is not None else 0
            iTransferred+=p["transferred"] if p["transferred"] is not None else 0
            iAcked+=p["acked"] if p["acked"] is not None else 0
            iFailed+=p["failed"] if p["failed"] is not None else 0
       
        aEmitted.append(iEmitted)     
        aTransferred.append(iTransferred)     
        aAcked.append(iAcked)     
        aFailed.append(iFailed)                
    
    return render('detail_dashboard.mako', request, {'user':request.user,
                                                     'Topology': aTopology,
					                                 'Visualization': jsonVisualization,
                                                     'Stats': aStats,
                                                     'Spouts': aSpouts,
                                                     'Bolts': aBolts,
                                                     'jStats': get_dumps(aStats),
                                                     'jSpouts': get_dumps(aSpouts),
                                                     'jBolts': get_dumps(aBolts),
                                                     'Emitted': aEmitted,
                                                     'Transferred': aTransferred,
                                                     'Acked': aAcked,
                                                     'Failed': aFailed,
                                                     'ShowSystem': iSystem,
                                                     'frmNewTopology': get_newform(request, UploadFileForm),
                                                     'frmHDFS': get_newform(request, UploadFileFormHDFS)
                                                     })
#
# detail_dashboard ********************************************************************************************************

# topology_dashboard ******************************************************************************************************
# Rev Date       Author
# --- ---------- ----------------------------------------------------------------------------------------------------------
# 001 2014-12-03 Jose Juan
#
# Topology Stats Dashboard (bolts & spouts).
#
# @author Jose Juan
# @date 2014-12-03
# @param request, HTTPRequest.
# @param topology_id, topology id.
# @param window, window stats (bolts & spouts).
# @return -
# @remarks -
#
def topology_dashboard(request, topology_id, window_id):
    aTopology = []  
  
    jsonStats = get_json(TOPOLOGY_URL + topology_id + '?window=' + window_id)
    jsonTopology = get_json(TOPOLOGY_URL + topology_id)
  
    if (len(jsonStats) > 0):
        jsonDumpsStats = get_dumps(jsonStats["topologyStats"])
        jsonDumpsSpouts = get_dumps(jsonStats["spouts"])
        jsonDumpsBolts = get_dumps(jsonStats["bolts"])
        aTopology = get_topology(topology_id)                             
     
        aSpouts = jsonTopology["spouts"]
        aBolts = jsonTopology["bolts"]
     
    return render('topology_dashboard.mako', request, {'jStats': jsonDumpsStats,
                                                       'jSpouts': jsonDumpsSpouts,
                                                       'jBolts': jsonDumpsBolts,
                                                       'windowId': window_id,
                                                       'Topology': aTopology,
                                                       'Spouts': aSpouts,
                                                       'Bolts': aBolts,
                                                       'frmNewTopology': get_newform(request, UploadFileForm),
                                                       'frmHDFS': get_newform(request, UploadFileFormHDFS)
                                                       })
#
# topology_dashboard ******************************************************************************************************

# components_dashboard ****************************************************************************************************
# Rev Date       Author
# --- ---------- ----------------------------------------------------------------------------------------------------------
# 001 2014-12-03 Jose Juan
#
# Components Dashboard (bolt & spout).
#
# @author Jose Juan
# @date 2014-12-03
# @param request, HTTPRequest.
# @param topology_id, topology id.
# @param component_id, component id (bolt & spout).
# @param system_id, show/hide system stats.
# @return -
# @remarks -
#
def components_dashboard(request, topology_id, component_id, system_id):
    aTopology = []
    aComponent = []
    aComponentStats = []
    jsonDumpsOutput = []
    jsonDumpsInput = []
    jsonDumpsExecutors = []
    jsonDumpsErrors = []
    iBolt = -1
    iSystem = int(system_id) if system_id is not None else 0     
    
    jsonTopology = get_json(TOPOLOGY_URL + topology_id + SYSTEM_STATS) if (iSystem == 1) else get_json(TOPOLOGY_URL + topology_id)

    iSystem = 1 if (iSystem == 0) else 0
  
    jsonComponents = get_json(TOPOLOGY_URL + topology_id + '/component/' + component_id)
  
    if (len(jsonTopology) > 0):
        aTopology = get_topology(topology_id)
  
        aSpouts = jsonTopology["spouts"]
        aBolts = jsonTopology["bolts"]
     
    if (len(jsonComponents) > 0):
        aComponent = [component_id, 
                      jsonComponents["name"], 
                      jsonComponents["executors"], 
                      jsonComponents["tasks"],
                      jsonComponents["componentType"].upper()
                      ]
     
        if (aComponent[4] == "BOLT"):     
            aComponentStats = jsonComponents["boltStats"]        
            iBolt = 1
        else:
            aComponentStats = jsonComponents["spoutSummary"]
  
        jsonDumpsComponentStats = get_dumps(aComponentStats)
     
        if ("outputStats") in jsonComponents:     
            jsonDumpsOutput = get_dumps(jsonComponents["outputStats"])            
     
        if ("inputStats") in jsonComponents:     
            jsonDumpsInput = get_dumps(jsonComponents["inputStats"])             
        
        if ("executorStats") in jsonComponents:     
            jsonDumpsExecutors = get_dumps(jsonComponents["executorStats"])             
     
        if ("componentErrors") in jsonComponents:     
            jsonDumpsErrors = get_dumps(jsonComponents["componentErrors"])
     
    return render('components_dashboard.mako', request, {'componentId': component_id,
                                                         'ShowSystem': iSystem,
                                                         'Topology': aTopology,
                                                         'Component': aComponent,
                                                         'Components': jsonDumpsComponentStats,
                                                         'Output': jsonDumpsOutput,
                                                         'Input': jsonDumpsInput,
                                                         'Executors': jsonDumpsExecutors,
                                                         'Errors': jsonDumpsErrors,
                                                         'isBolt': iBolt,
                                                         'Spouts': aSpouts,
                                                         'Bolts': aBolts,
                                                         'frmNewTopology': get_newform(request, UploadFileForm),
                                                         'frmHDFS': get_newform(request, UploadFileFormHDFS)
                                                         })
#
# components_dashboard ****************************************************************************************************

# spouts_dashboard ********************************************************************************************************
# Rev Date       Author
# --- ---------- ----------------------------------------------------------------------------------------------------------
# 001 2014-12-09 Jose Juan
#
# Control Panel of Spouts (Dashboard).
#
# @author Jose Juan
# @date 2014-12-09
# @param request, HTTPRequest.
# @param topology_id, topology id.
# @return -
# @remarks -
#
def spouts_dashboard(request, topology_id):
    aTopology = []
    aSpouts = []
  
    jsonTopology = get_json(TOPOLOGY_URL + topology_id)
  
    if (len(jsonTopology) > 0):     
        aTopology = get_topology(topology_id)
        jsonDumpsSpouts = get_dumps(jsonTopology["spouts"])
        aSpouts = jsonTopology["spouts"]
        aBolts = jsonTopology["bolts"]
  
    return render('spouts_dashboard.mako', request, {'Topology': aTopology,
                                                     'jSpouts': jsonDumpsSpouts,
                                                     'Spouts': aSpouts,
                                                     'Bolts': aBolts,
                                                     'frmNewTopology': get_newform(request, UploadFileForm),
                                                     'frmHDFS': get_newform(request, UploadFileFormHDFS)
                                                     })
#
# spouts_dashboard ********************************************************************************************************

# bolts_dashboard *********************************************************************************************************
# Rev Date       Author
# --- ---------- ----------------------------------------------------------------------------------------------------------
# 001 2014-12-09 Jose Juan
#
# Control Panel of Bolts (Dashboard).
#
# @author Jose Juan
# @date 2014-12-09
# @param request, HTTPRequest.
# @param topology_id, topology id.
# @return -
# @remarks -
#
def bolts_dashboard(request, topology_id):
    aTopology = []
    aBolts = []
  
    jsonTopology = get_json(TOPOLOGY_URL + topology_id)
  
    if (len(jsonTopology) > 0):            
        aTopology = get_topology(topology_id)    
        jsonDumpsBolts = get_dumps(jsonTopology["bolts"])
        aBolts = jsonTopology["bolts"]
        aSpouts = jsonTopology["spouts"]
     
    return render('bolts_dashboard.mako', request, {'Topology': aTopology,
                                                    'jBolts': jsonDumpsBolts,
                                                    'Bolts': aBolts,
                                                    'Spouts': aSpouts,
                                                    'frmNewTopology': get_newform(request, UploadFileForm),
                                                    'frmHDFS': get_newform(request, UploadFileFormHDFS)
                                                    })
#
# bolts_dashboard *********************************************************************************************************

# cluster_summary *********************************************************************************************************
# Rev Date       Author
# --- ---------- ----------------------------------------------------------------------------------------------------------
# 001 2014-11-19 Jose Juan
#
# Storm cluster summary
#
# @author Jose Juan
# @date 2014-11-19
# @param request, HTTPRequest.
# @return -
# @remarks -
#
def cluster_summary(request):  
    aSupervisor = []
  
    jsonCluster = get_json(CLUSTER_URL)
    jsonSupervisor = get_json(SUPERVISOR_URL)                  
  
    if (len(jsonSupervisor) > 0):        
        aSupervisor = jsonSupervisor["supervisors"]
    
    return render('cluster_summary.mako', request, {'Cluster': jsonCluster,
                                                    'Supervisor': aSupervisor,
                                                    'frmNewTopology': get_newform(request, UploadFileForm),
                                                    'frmHDFS': get_newform(request, UploadFileFormHDFS)
                                                    })  
#
# cluster_summary *********************************************************************************************************

# nimbus_configuration ****************************************************************************************************
# Rev Date       Author
# --- ---------- ----------------------------------------------------------------------------------------------------------
# 001 2014-11-19 Jose Juan
#
# Nimbus settings.
#
# @author Jose Juan
# @date 2014-11-19
# @param request, HTTPRequest.
# @return -
# @remarks -
#
def nimbus_configuration(request):
    aConf = []
  
    jsonConf = get_json(CONFIGURATION_URL)
  
    if (len(jsonConf) > 0):        
        for prop in jsonConf:                  
            aConf.append({'key': prop,
                          'value': jsonConf[prop]
                          });             
    
    return render('nimbus_configuration.mako', request, {'Conf': aConf,
                                                         'frmNewTopology': get_newform(request, UploadFileForm),
                                                         'frmHDFS': get_newform(request, UploadFileFormHDFS) 
                                                         })  
#
# nimbus_configuration ****************************************************************************************************

# topology ****************************************************************************************************************
# Rev Date       Author
# --- ---------- ----------------------------------------------------------------------------------------------------------
# 001 2014-11-26 Jose Juan
#
# Topology Stats Windows (bolts & spouts).
#
# @author Jose Juan
# @date 2014-11-26
# @param request, HTTPRequest.
# @param topology_id, topology id.
# @param window_id, window stats (bolts & spouts).
# @return -
# @remarks -
#
def topology(request, topology_id, window_id):
    aTopology = []
    aStat = []
    aStats = []
    aSpouts = []
    aBolts = []  
  
    jsonStats = get_json(TOPOLOGY_URL + topology_id + '?window=' + window_id)
    aTopology = get_topology(topology_id)
  
    if (len(jsonStats) > 0):         
        aStats = jsonStats["topologyStats"]          
     
        for stat in aStats:
            if (stat["window"] == window_id):
	               aStat = stat               
     
        aSpouts = jsonStats["spouts"]
        aBolts = jsonStats["bolts"]                    
     
    return render('topology.mako', request, {'Topology': aTopology,
                                             'Stats': aStat,
                                             'Spouts': aSpouts,
                                             'Bolts': aBolts,
                                             'ShowSystem': 0
                                             })
#
# topology ****************************************************************************************************************

# components **************************************************************************************************************
# Rev Date       Author
# --- ---------- ----------------------------------------------------------------------------------------------------------
# 001 2014-11-26 Jose Juan
#
# Storm Topology's Components (bolts & spouts stats).
#
# @author Jose Juan
# @date 2014-11-26
# @param request, HTTPRequest.
# @param topology_id, topology id.
# @param component_id, component (bolts & spouts).
# @return -
# @remarks -
#
def components(request, topology_id, component_id, system_id): 
    aTopology = []
    aComponent = []
    aStats = []
    aOutput = []
    aInput = []
    aExecutors = []
    aErrors = []   
    iBolt = -1    
    iSystem = int(system_id) if system_id is not None else 0       
  
    jsonComponents = get_json(TOPOLOGY_URL + topology_id + '/component/' + component_id + SYSTEM_STATS) if (iSystem == 1) else get_json(TOPOLOGY_URL + topology_id + '/component/' + component_id)
  
    iSystem = 1 if (iSystem == 0) else 0
  
    aTopology = get_topology(topology_id)
  
    if (len(jsonComponents) > 0):
        aComponent = [component_id, 
                      jsonComponents["name"], 
		              jsonComponents["executors"], 
		              jsonComponents["tasks"],
		              jsonComponents["componentType"].upper()
		              ]
     
        if (aComponent[4] == "BOLT"):     
            aStats = jsonComponents["boltStats"]
            iBolt = 1
        else:
            aStats = jsonComponents["spoutSummary"]                     
        
        if ("outputStats") in jsonComponents:     
            aOutput = jsonComponents["outputStats"]             
     
        if ("inputStats") in jsonComponents:     
            aInput = jsonComponents["inputStats"]             
        
        if ("executorStats") in jsonComponents:     
            aExecutors = jsonComponents["executorStats"]             
     
        if ("componentErrors") in jsonComponents:     
            aErrors = jsonComponents["componentErrors"]                 
  
    return render('components.mako', request, {'Server_Log': LOG_URL,
                                               'ShowSystem': iSystem,
                                               'idComponent': component_id,
                                               'Topology': aTopology,
                                               'Component': aComponent,
                                               'Stats': aStats,
                                               'Output': aOutput,
                                               'Input': aInput,
                                               'Executors': aExecutors,
                                               'Errors': aErrors,
                                               'iBolt': iBolt
                                               })
#
# components **************************************************************************************************************

# failed ******************************************************************************************************************
# Rev Date       Author
# --- ---------- ----------------------------------------------------------------------------------------------------------
# 001 2015-01-08 Jose Juan
#
# Resumme of failed components.
#
# @author Jose Juan
# @date 2015-01-08
# @param request, HTTPRequest.
# @param topology_id, topology id.
# @param component_id, component id (spout&bolt).
# @param system_id, show/hide system stats.
# @return -
# @remarks -
#
def failed(request, topology_id, component_id, system_id):    
    aComponent = []  
  
    iSystem = int(system_id) if system_id is not None else 0  
    jsonTopology = get_json(TOPOLOGY_URL + topology_id + SYSTEM_STATS) if (iSystem == 1) else get_json(TOPOLOGY_URL + topology_id)

    if (int(component_id) == 1):
        aComponent = jsonTopology["topologyStats"]
     
    if (int(component_id) == 2):
        aComponent = jsonTopology["spouts"]
     
    if (int(component_id) == 3):
        aComponent = jsonTopology["bolts"]    
  
    return render('failed.mako', request, {'Component': aComponent,
                                           'idTopology': topology_id,
                                           'idComponent': int(component_id)
                                           })  
#
# failed ******************************************************************************************************************

# *************************************************************************************************************************
# **********                                                                                                     **********
# **********                                                                                                     **********
# **********                                      FUNCTIONS.                                                     **********
# **********                                                                                                     **********
# **********                                                                                                     **********
# *************************************************************************************************************************

# get_json ****************************************************************************************************************
# Rev Date       Author
# --- ---------- ----------------------------------------------------------------------------------------------------------
# 001 2014-12-16 Jose Juan
#
# Get JSON from a URL.
#
# @author Jose Juan
# @date 2014-12-16
# @param psUrl, JSON's URL.
# @return JSON Object.
# @remarks -
#
def get_json(psUrl):
    rJSON = requests.get(psUrl)
    jsonObject = rJSON.json()      
  
    if (len(jsonObject) > 0):     
        return jsonObject      
    else:     
        return []    
#
# get_json ****************************************************************************************************************

# get_dumps ***************************************************************************************************************
# Rev Date       Author
# --- ---------- ----------------------------------------------------------------------------------------------------------
# 001 2014-12-23 Jose Juan
#
# Convert string literal to raw string literal.
#
# @author Jose Juan
# @date 2014-12-23
# @param psObject, string literal.
# @return raw string literal.
# @remarks -
#
def get_dumps(psObject):    
    jsonDumps = json.dumps(psObject).replace("\\", "\\\\")
  
    return jsonDumps
#
# get_dumps ***************************************************************************************************************

# get_topology ************************************************************************************************************
# Rev Date       Author
# --- ---------- ----------------------------------------------------------------------------------------------------------
# 001 2014-12-03 Jose Juan
#
# Storm Topology's.
#
# @author Jose Juan
# @date 2014-12-03
# @param topology_id, Topology Id.
# @return Array with topology status.
# @remarks -
#
def get_topology(topology_id):  
    aTopology = []  
  
    rTopology = requests.get(TOPOLOGY_URL + topology_id)
    jsonTopology = rTopology.json()  
  
    if (len(jsonTopology) > 0):
        nameTopology = jsonTopology["name"]
        idTopology = jsonTopology["id"]
        statusTopology = jsonTopology["status"]
        uptimeTopology = jsonTopology["uptime"]
        workersTopology = jsonTopology["workersTotal"]
        executorsTopology = jsonTopology["executorsTotal"]
        tasksTopology = jsonTopology["tasksTotal"]
     
        aTopology = [idTopology, nameTopology, statusTopology, uptimeTopology, workersTopology, executorsTopology, tasksTopology]
     
    return aTopology   
#
# get_topology ************************************************************************************************************

# get_newform *************************************************************************************************************
# Rev Date       Author
# --- ---------- ----------------------------------------------------------------------------------------------------------
# 001 2014-12-29 Jose Juan
#
# Get new form.
#
# @author Jose Juan
# @date 2014-12-29
# @param psObject, form.
# @return New class form.
# @remarks -
#
def get_newform(request, pfForm):
    if request.method == 'POST':
        form = pfForm(request.POST, request.FILES)
    else:   
        form = pfForm()
     
    return form
#
# get_newform *************************************************************************************************************

# changeTopologyStatus ****************************************************************************************************
# Rev Date       Author
# --- ---------- ----------------------------------------------------------------------------------------------------------
# 001 2014-11-25 Jose Juan
#
# Activa una topología del clúster STORM.
#
# @author Jose Juan
# @date 2014-11-25
# @param request, HTTPRequest.
# @return -
# @remarks -
#
@csrf_exempt
def changeTopologyStatus(request):
    iResult = -1
    sId = ""
    sAction = ""
    bWait = False
    iWait = -1    
  
    if request.method == 'POST':
        sId = request.POST['sId']      
        sAction = request.POST['sAction']
        bWait = request.POST['bWait']
        iWait = request.POST['iWait']
     
        if (bWait == "true"):
            post_response = requests.post(TOPOLOGY_URL + sId + '/' + sAction + '/' + iWait)
        else:
            post_response = requests.post(TOPOLOGY_URL + sId + '/' + sAction)            
      
        iResult =  post_response.status_code            
      
    return HttpResponse(iResult, mimetype = "application/javascript") 
#
# changeTopologyStatus ****************************************************************************************************
    
# set_topology_status *****************************************************************************************************
# Rev Date       Author
# --- ---------- ----------------------------------------------------------------------------------------------------------
# 001 2014-11-25 Jose Juan
# 001 2015-01-20 Jose Juan (Add submit topology)
#
# Management of Storm Topology.
#
# @author Jose Juan
# @date 2014-11-25
# @param request, HTTPRequest.
# @return -
# @remarks -
#
@csrf_exempt
def set_topology_status(request):  
    sAction = ""   
    sExecute = ""
    iNumWorkers = 0
    sOptions = ""
    sWaitSecs = ""
    sNumWorkers = ""
    sNumExecutors = ""
    msg = ""
    sTopologyName = ""
    response = {'status': -1, 'output': -1, 'data': ''}  
    sScript = "storm"                           

    if request.method == 'POST':
        sAction = request.POST['psAction']             
          
        if (sAction == "rebalance"):                   
            sNameTopology = request.POST['psNameTopology'] 
            iNumWorkers = request.POST['piNumWorkers'] if (request.POST['piNumWorkers'] <> "") else 0                        
            iWaitSecs = request.POST['piWaitSecs'] if (request.POST['piWaitSecs'] <> "") else 0                        
            aComponent = request.POST.getlist('paComponents[]')
            
            if (iWaitSecs > 0):
                sOptions += " -w " + iWaitSecs        
	  
            if (iNumWorkers > 0):
                sOptions += " -n " + iNumWorkers
            
            iMod = 0
            
            if (aComponent <> []):    
                while (iMod < len(aComponent)):
                    if(iMod%2 == 0):     
                        sOptions += " -e " + aComponent[iMod] + "="
                    else:                           
                        sOptions+=aComponent[iMod]
                        
                    iMod+=1
                
            sExecute = sScript + " " + sAction + " " + sNameTopology + " " + sOptions                                
                    
        if (sAction == "submitTopology"):            
            sURL = request.POST['psURL']
            form = UploadFileForm(request.POST, request.FILES)

            if form.is_valid():                                            
                sServer = STORM_UI_SERVER                       
                sClass = request.POST['class_name'] if (request.POST['class_name'] <> "") else ""
                sTopologyName = request.POST['topology_name'] if (request.POST['topology_name'] <> "") else ""
                sFile = request.FILES['file']
                sFileName = sFile.name                                                        
                sClass = request.POST['class_name']  
                sPath = settings.UPLOAD_ROOT + '/' + sFileName
                    
                if not (os.path.isfile(sPath)):
                    path = default_storage.save(settings.UPLOAD_ROOT + '/' + sFileName, ContentFile(sFile.read()))
                    sPath = os.path.join(settings.UPLOAD_ROOT, path)
                    
                sExecute = sScript + " " + "jar -c nimbus.host=" + sServer + " " + sPath + " " + sClass + " " + sTopologyName
                response['status'] = 0
                        
            else:
                #raise PopupException(_("Error in upload form: %s") % (form.errors,))
                msg = _("Error in upload form: %s.\n") % form.errors
                response['error'] = form.errors
                response['status'] = -1
              
        if (sAction == "saveTopology"):
            sURL = request.POST['psURL']
            form = UploadFileFormHDFS(request.POST, request.FILES)
            
            if request.META.get('upload_failed'):
                raise PopupException(request.META.get('upload_failed'))
            
            try:
                sFileHDFS = request.FILES['hdfs_file']
            except:
                sFileHDFS = ""
            
            try:    
                if (sFileHDFS <> ""):
                    username = request.user.username
                    sFileNameHDFS = sFileHDFS.name
                    sPathHDFS = "/user/" + username                 
                    sPathHDFS = request.fs.join(sPathHDFS, sFileNameHDFS)                    
                    tmp_file = sFileHDFS.get_temp_path()
                    request.fs.do_as_user(username, request.fs.rename, tmp_file, sPathHDFS)                        
                    
                    return HttpResponseRedirect(sURL)
                else:        
                    msg = _('HDFS File must not be empty.\n')
                    raise PopupException(msg)
                           
            except IOError, ex:
                already_exists = False
                response['status'] = -1
                    
                try:
                    already_exists = request.fs.exists(sPathHDFS)
                except Exception:
                    pass
         
                if already_exists:
                    msg = _('Destination %(name)s already exists.\n')  % {'name': sPathHDFS}
                else:
                    msg = _('Copy to %(name)s failed: %(error)s.\n') % {'name': sPathHDFS, 'error': ex}    
                
                raise PopupException(msg)
                          
    status, output = commands.getstatusoutput(sExecute)      
  
    response['output'] = output
            
    if (sAction == "submitTopology"):
        try:
            os.remove(sPath)
        except:
            msg += "Exception raised while deleting temp file.\n"
        pass

        if (("Finished submitting topology: " + sTopologyName) in response['output']):
            output = None
            
        if ((output is None) and (response['status'] == 0)):
            return HttpResponseRedirect(sURL)
        else:
            if (output is None):
                msg += "Topology submitted OK.\n"
            else:
                msg += "Error submitting topology.\n"
                    
            raise PopupException(msg)
            
    return HttpResponse(json.dumps(response), content_type="text/plain")            
#
# set_topology_status ***************************************************************************************************** 
      
# get_seconds_from_strdate ************************************************************************************************
# Rev Date       Author
# --- ---------- ----------------------------------------------------------------------------------------------------------
# 001 2014-12-11 Jose Juan
#
# Get seconds from a date in string type.
#
# @author Jose Juan
# @date 2014-12-11
# @param psDate, Topology Id.
# @return Array with topology status.
# @remarks -
#
def get_seconds_from_strdate(psDate):
    iSeconds = 0
    
    try:
        aDate = psDate.split(" ")   
        iLen = len(aDate) if len(psDate) is not None else 0
    except:
        iLen = 0
        
    if (iLen == 1):
        try:
            iSeconds = int(aDate[0][:-1])
        except:
            iSeconds = 0    
   
    if (iLen == 2):
        try:
            iSeconds = (int(aDate[0][:-1]) * 60) + int(aDate[1][:-1])
        except:
            iSeconds = 0    
   
    if (iLen == 3):
        try:
            iSeconds = (int(aDate[0][:-1]) * 3600) + (int(aDate[1][:-1]) * 60) + int(aDate[2][:-1])
        except:
            iSeconds = 0   
   
    if (iLen == 4):     
        try:
            iSeconds = (int(aDate[0][:-1]) * 86400) + (int(aDate[1][:-1]) * 3600) + (int(aDate[2][:-1]) * 60) + int(aDate[3][:-1])
        except:
            iSeconds = 0       
   
    return iSeconds
#  
# get_seconds_from_strdate *************************************************************************************************
