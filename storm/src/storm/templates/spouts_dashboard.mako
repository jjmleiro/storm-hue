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

<%!
from desktop.views import commonheader, commonfooter 
from django.utils.translation import ugettext as _
%>

${commonheader("Spouts Detail", app_name, user) | n,unicode}

<%namespace name="storm" file="navigation_bar.mako" />
<%namespace name="Templates" file="templates.mako" />
<%namespace name="JavaScript" file="js.mako" />
<%namespace name="graphsHUE" file="common_dashboard.mako" />

## Use double hashes for a mako template comment
## Main body

<link href="/storm/static/css/storm.css" rel="stylesheet">

${ JavaScript.import_js() }
${ graphsHUE.import_charts() }

<script type="text/javascript" charset="utf-8"> 
   $(document).ready(function() {
      var StormModel = new StormViewModel();
      ko.applyBindings(StormModel);
      
      $('#tblTopologySpouts').dataTable( {	    
	    	"sPaginationType": "bootstrap",
	    	"bLengthChange": true,
	    	"autoWidth": true,
	        "sDom": "<'row-fluid'<l><f>r>t<'row-fluid'<'dt-pages'p><'dt-records'i>>"        
	    } );
   });
   
   var dataPieSpouts1 = [];
   var dataBarSpouts1 = [];
   var iTasks = 0;
   var iExecutors = 0;
   
   var sData = "${jSpouts}";   
   var swData = sData.replace(/&quot;/ig,'"')   
   var jsonSpouts = JSON.parse(swData);
   
   for (var i=0; i<Object.keys(jsonSpouts).length; i++) {
      iTasks+=jsonSpouts[i].tasks;
      iExecutors+=jsonSpouts[i].executors;     
      dataBarSpouts1.push({"key": jsonSpouts[i].spoutId, "values": [ {"x": "${ _('Emitted') }", "y": jsonSpouts[i].emitted},
                                                                     {"x": "${ _('Transferred') }", "y": jsonSpouts[i].transferred},
                                                                     {"x": "${ _('Acked') }", "y": jsonSpouts[i].acked},
                                                                     {"x": "${ _('Failed') }", "y": jsonSpouts[i].failed}
                                                                   ]
                          });
      dataPieSpouts1.push({"label": "${ _('Tasks') }", "value" : iTasks}, {"label": "${ _('Executors') }", "value" : iExecutors});                    
      
   };                   
   
   nv.addGraph(function() {
                  var chart = nv.models.pieChart()
                                       .x(function(d) { return d.label })
                                       .y(function(d) { return d.value })
                                       .valueFormat(d3.format(".0f"))
                                       .color(['#468847', '#f89406'])
                                       .showLabels(false);

                  d3.select("#pieSpouts1 svg")
                    .datum(dataPieSpouts1)
                    .transition().duration(350)
                    .call(chart);
 
                  return chart;
   });   
   
   nv.addGraph(function() {
                 var graphSpouts1 = nv.models.multiBarChart()
                                           .transitionDuration(350)
                                           .reduceXTicks(true)   //If 'false', every single x-axis tick label will be rendered.
                                           .rotateLabels(0)      //Angle to rotate x-axis labels.                                           
                                           .groupSpacing(0.1)    //Distance between each group of bars.                                
                                           .showControls(true);
                                  
                                  graphSpouts1.multibar.stacked(false);         
    
                                  graphSpouts1.yAxis
                                            .tickFormat(d3.format('d'));
        
                                  d3.select('#barSpouts1 svg')
                                    .datum(dataBarSpouts1)
                                    .call(graphSpouts1);

                                  nv.utils.windowResize(graphSpouts1.update);

                                  return graphSpouts1;
   });
</script>

<%
  _breadcrumbs = [
    [_('Storm Dashboard'), url('storm:storm_dashboard')],    
    [_('Topology ') + Topology[0] + _(' Detail'), url('storm:detail_dashboard', topology_id = Topology[0], system_id = 0)],
    [_('Spouts Detail'), url('storm:spouts_dashboard', topology_id = Topology[0])]
  ]
%>

${ storm.header(_breadcrumbs) }

${ storm.menubar(section = 'Spouts Detail')}

${Templates.tblSubmitTopology(frmNewTopology)}
${Templates.tblSaveTopology(frmHDFS)}

<div id="divPrincipal" class="container-fluid">
  <div class="card">        
    <div class="card-body">
       <table width="100%" height="100%" border="0" cellpadding="6" cellspacing="0">   
          ${Templates.ControlPanelTopology("spouts_dashboard")}
          <tr>
             <td colspan="2">                
                ${Templates.tblRebalanceTopology(Topology[1])}
             </td>
          </tr>  
          <tr valign="top">
             <td>
                <div class="col-lg-4">
                   <div class="panel panel-default">
                      <div class="panel-heading">
                         <i class="fa fa-bar-chart fa-fw"></i> Stats
                      </div>
                      <div class="panel-body">
                         <div id="barSpouts1"><svg style="min-height: 220px; margin: 10px auto"></svg></div>
                      </div>                        
                   </div>
                </div>
             </td>
             <td>
                <div class="col-lg-4">
                   <div class="panel panel-default">
                      <div class="panel-heading">
                         <i class="fa fa-pie-chart fa-fw"></i> ${ _('Executors/Tasks') }
                      </div>
                      <div class="panel-body">
                         <div id="pieSpouts1"><svg style="min-height: 240px; margin: 10px auto"></svg></div>
                      </div>                        
                   </div>
                </div>
             </td>             
          </tr>  
          <tr valign="top">
             <td colspan="2">
                <div class="col-lg-4">
                   <div class="panel panel-default">
                      <div class="panel-heading">
                         <i class="fa fa-bar-chart fa-fw"></i> ${ _('Summary') }
                      </div>
                      <div class="panel-body">
                         <table class="table datatables table-striped table-hover table-condensed" id="tblTopologySpouts" data-tablescroller-disable="true">
                            <thead>
                               <tr>
                                  <th> ${ _('Id.') } </th>
                                  <th> ${ _('Executors') } </th>
                                  <th> ${ _('Tasks') } </th>
                                  <th> ${ _('Emitted') } </th>
                                  <th> ${ _('Transferred') } </th>
                                  <th> ${ _('Complete Latency (ms)') } </th>                         
                                  <th> ${ _('Acked') } </th>
                                  <th> ${ _('Failed') } </th>
                                  <th> ${ _('Last Error') } </th>
                               </tr>
                            </thead>
                            <tbody>
                               % for row in Spouts:
                                  <tr>                                     
                                     <td>
                                        <a class="fa fa-tachometer" href="${url('storm:components_dashboard', topology_id = Topology[0], component_id = row["spoutId"], system_id = 0)}"></a>                                                 
                                        <a href="${url('storm:components', topology_id = Topology[0], component_id = row["spoutId"], system_id = 0)}"> ${row["spoutId"]} </a>
                                     </td>
                                     <td>${row["executors"]}</td>                                                        
                                     <td>${row["tasks"]}</td>
                                     <td>${row["emitted"]}</td>
                                     <td>${row["transferred"]}</td>
                                     <td>${row["completeLatency"]}</td>
                                     <td>
                                        <span style="color: green; font-weight: bold">
                                           ${row["acked"]}
                                        </span>
                                     </td>
                                     <td>
                                        <span style="color: red; font-weight: bold">
                                           ${row["failed"]}
                                        </span>
                                     </td>
                                     % if (row["lastError"] == ""):
                                        <td></td>
                                     % else:   
                                        <td>
                                           <span class="label label-important">
                                              <a href="#" data-target="#divERROR" data-toggle="modal">                                                          
                                                 ${ _('ERROR') }
                                              </a>
                                           </span>                                                                                                        
                                           ${Templates.divERROR(row["lastError"])}
                                        </td>
                                     % endif
                                  </tr>
                               % endfor
                            </tbody>
                         </table>                                  
                      </div>                        
                   </div>
                </div>
             </td>
          </tr>
       </table>             
    </div>
  </div>
</div>
  
${commonfooter(messages) | n,unicode}
