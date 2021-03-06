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

${commonheader("Storm Dashboard", app_name, user) | n,unicode}

<%namespace name="storm" file="navigation_bar.mako" />
<%namespace name="graphsHUE" file="common_dashboard.mako" />
<%namespace name="Templates" file="templates.mako" />
<%namespace name="JavaScript" file="js.mako" />


<link href="${ static('storm/css/storm.css') }" rel="stylesheet" >
<link href="${ static('desktop/ext/css/hue-filetypes.css') }" rel="stylesheet" >

${ graphsHUE.import_charts() }
${ JavaScript.import_js() }

<script type='text/javascript'>    
   $(document).ready(function() {                           
      $('#tblTopology').dataTable({
        "sPaginationType": "bootstrap",
	    	"bLengthChange": true,
	    	"autoWidth": true,
	        "sDom": "<'row-fluid'<l><f>r>t<'row-fluid'<'dt-pages'p><'dt-records'i>>",
          "oLanguage":{
              "sLengthMenu":"${_('Show _MENU_ entries')}",
              "sSearch":"${_('Search')}",
              "sEmptyTable":"${_('No data available')}",
              "sInfo":"${_('Showing _START_ to _END_ of _TOTAL_ entries')}",
              "sInfoEmpty":"${_('Showing 0 to 0 of 0 entries')}",
              "sInfoFiltered":"${_('(filtered from _MAX_ total entries)')}",
              "sZeroRecords":"${_('No matching records')}",
              "oPaginate":{
                  "sFirst":"${_('First')}",
                  "sLast":"${_('Last')}",
                  "sNext":"${_('Next')}",
                  "sPrevious":"${_('Previous')}"
              }
        }        
	    });

   var dataTopologyStats = [ { "label": "${ _('Actives') }",                               
                               "value" : "${Data['actives']}"
                             },
                             { "label": "${ _('Inactives') }",                               
                               "value" : "${Data['inactives']}"
                             }
                           ];
                  
   nv.addGraph(function() {
                  var chart = nv.models.pieChart()
                                       .x(function(d) { return d.label })
                                       .y(function(d) { return d.value })
                                       .valueFormat(d3.format(".0f"))
                                       .color(['#46A546', '#F89406'])
                                       .showLabels(false);
                  d3.select("#pieTopologyStats svg")
                    .datum(dataTopologyStats)
                    .transition().duration(350)
                    .call(chart);
 
                  return chart;
   });

   var dataExecWorkers = [ { "label": "${ _('Executors') }",
                             "value" : "${Data['executors']}"
                           },
                           { "label": "${ _('Workers') }",
                             "value" : "${Data['workers']}"
                           },
                           { "label": "${ _('Tasks') }",
                             "value" : "${Data['tasks']}"
                           }
                         ];
                           
   nv.addGraph(function() {
                  var chart = nv.models.pieChart()
                                       .x(function(d) { return d.label })
                                       .y(function(d) { return d.value })
                                       .valueFormat(d3.format(".0f"))
                                       .showLabels(false);
                  d3.select("#pieExecWorkers svg")
                    .datum(dataExecWorkers)
                    .transition().duration(350)
                    .call(chart);
 
                  return chart;
   });
   });            
</script>

${ storm.menubar(section = 'Storm Dashboard')}

% if Data['error'] == 1:
  <div class="container-fluid">
    <div class="card">
      <div class="card-body">
        <div class="alert alert-error">
          <h2>${ _('Error connecting to the Storm UI server:') } <b>${Data['storm_ui']}</b></h2>
          <h3>${ _('Please contact your administrator to solve this.') }</h3>
        </div>
      </div>
    </div>
  </div>  
% else:
  <%
      _breadcrumbs = [
        [_('Storm Dashboard'), url('storm:storm_dashboard')]
      ]
  %>
  
  ${Templates.tblSubmitTopology(Data['frmNewTopology'])}
  ${Templates.tblSaveTopology(Data['frmHDFS'])}
  ${ storm.header(_breadcrumbs) }

  % if not Data['topologies']['topologies']: 
    ${Templates.divWithoutData()}
  %else:
    <div class="container-fluid">
     <div class="card">        
       <div class="card-body">              
          <table width="100%" height="100%" border="0" cellpadding="6" cellspacing="0">             
             <tr valign="top">
                <td width="33%" rowspan="3">
                   <div class="col-lg-4">
                      <div class="panel panel-default">
                         <div class="panel-heading">
                          <i class="fa fa-database fa-fw"></i> ${ _('Topologies Stats') }                            
                         </div>
                         <div class="panel-body">
                            <div id="pieTopologyStats"><svg style="min-height: 240px; margin: 10px auto"></svg></div>
                         </div>                        
                      </div>
                   </div> 
                </td>
                <td width="33%" rowspan="3">
                   <div class="col-lg-4">
                      <div class="panel panel-default">
                         <div class="panel-heading">                            
                          <table width="100%">             
                            <tr>
                              <td>                            
                                <i class="fa fa-database fa-fw"></i> ${ _('Topologies: Executors/Tasks') }
                              </td>
                              <td>
                                
                              </td>
                            </tr>
                          </table>
                         </div>
                         <div class="panel-body">
                            <div id="pieExecWorkers"><svg style="min-height: 240px; margin: 10px auto"></svg></div>
                         </div>                        
                      </div>
                   </div>
                </td>                                
                <td width="34%">
                   <%
                   iMax = 0
                   iMin = 0
                   iTemp = 0
                   sNameMin = ""
                   sNameMax = ""
                   sIdMax = ""
                   sIdMin = ""
                   sUptimeMin = ""
                   sUptimeMax = ""
                   iCount = 0
                   while (iCount < len(Data['topologies']['topologies'])):
                    iTemp = Data['topologies']['topologies'][iCount]['seconds']
                    if (iTemp >= iMax):
                      iMax = iTemp
                      sUptimeMax = Data['topologies']['topologies'][iCount]["uptime"]
                      sNameMax = Data['topologies']['topologies'][iCount]["name"]
                      sIdMax = Data['topologies']['topologies'][iCount]["id"]
                      if (iMin == 0):
                        iMin = iMax
                        sUptimeMin = sUptimeMax
                        sNameMin = sNameMax
                        sIdMin = sIdMax
                      else:
                        if (iTemp < iMin):
                          iMin = iTemp
                          sUptimeMin = Data['topologies']['topologies'][iCount]["uptime"]
                          sNameMin = Data['topologies']['topologies'][iCount]["name"]
                          sIdMin = Data['topologies']['topologies'][iCount]["id"]
                      iCount+=1                                                                                
                   %>
                                                  
                   <div class="panel panel-primary">
                      <div class="panel-heading">
                         <div class="row">
                            <div class="col-xs-3">
                               <i class="fa fa-plus-circle fa-3x"></i>
                            </div>
                            <div class="col-xs-9 text-right">
                               <div class="huge">${sUptimeMax}</div>
                               <div>${ _('Max Uptime') }</div>
                            </div>
                         </div>
                      </div>
                      <a href="${url('storm:detail_dashboard', topology_id = sIdMax, system_id = 0)}">                               
                         <div class="panel-footer">
                            <span class="pull-left">${sNameMax}</span>
                            <span class="pull-right"><i class="fa fa-arrow-circle-right"></i></span>
                            <div class="clearfix"></div>
                         </div>
                      </a>
                   </div>
                </td>             
             </tr>             
             <tr valign="top">
                <td>
                   <div class="panel panel-primary">
                      <div class="panel-heading">
                         <div class="row">
                            <div class="col-xs-3">
                               <i class="fa fa-minus-circle fa-3x"></i>
                            </div>
                            <div class="col-xs-9 text-right">
                               <div class="huge">${sUptimeMin}</div>
                               <div>${ _('Min Uptime') }</div>
                            </div>
                         </div>
                      </div>
                      <a href="${url('storm:detail_dashboard', topology_id = sIdMin, system_id = 0)}">                               
                         <div class="panel-footer">
                            <span class="pull-left">${sNameMin}</span>
                            <span class="pull-right"><i class="fa fa-arrow-circle-right"></i></span>
                            <div class="clearfix"></div>
                         </div>
                      </a>
                   </div>                                                       
                </td>             
             </tr>
             <tr valign="top">
                <td>
                   <div class="panel panel-green">
                      <div class="panel-heading">
                         <div class="row">
                            <div class="col-xs-3">
                               <i class="fa fa-check-circle fa-3x"></i>
                            </div>
                            <div class="col-xs-9 text-right">
                               <div class="huge">0 ${ _('Failed') }</div>
                               <div>${ _('Topology Stats') }</div>
                            </div>
                         </div>
                      </div>
                      <a href="${url('storm:detail_dashboard', topology_id = sIdMax, system_id = 0)}">
                         <div class="panel-footer">
                            <span class="pull-left">${ _('View Details') }</span>
                            <span class="pull-right"><i class="fa fa-arrow-circle-right"></i></span>
                            <div class="clearfix"></div>
                         </div>
                      </a>
                   </div>
                </td>
             <tr>
             <tr>
                <td colspan="3">
                   <div class="col-lg-4">
                      <div class="panel panel-default">
                         <div class="panel-heading">                            
                          <table width="100%">             
                            <tr>
                              <td>                            
                                <i class="fa fa-table fa-fw"></i> ${ _('Topology Summary') }
                              </td>
                              <td>
                                ${Templates.frmExport(Data['topologies']['topologies'])}
                              </td>
                            </tr>
                          </table>
                         </div>
                         <div class="panel-body">
                            <table class="table datatables table-striped table-hover table-condensed" id="tblTopology" data-tablescroller-disable="true">
                               <thead>
                                  <tr>
                                     <th> ${ _('Name') } </th>
                                     <th> ${ _('Id.') } </th>
                                     <th> ${ _('Status') } </th>
                                     <th> ${ _('Uptime') } </th>
                                     <th> ${ _('Num.Workers') } </th>
                                     <th> ${ _('Num.Executors') } </th>
                                     <th> ${ _('Num.Tasks') } </th>
                                  </tr>
                               </thead>        
                               <tbody> 
                                  % for row in Data['topologies']['topologies']:                                  
                                     <tr>
                                        <td>
                                           <a href="${url('storm:detail_dashboard', topology_id = row['id'], system_id = 0)}"> ${row["name"]} </a>   
                                        </td>
                                        <td>${row["id"]}</td>                                                        
                                        <td>
                                           % if row["status"] == "ACTIVE":
                                              <span class="label label-success"> ${row["status"]} </span>
                                           % else:
                                              <span class="label label-warning"> ${row["status"]} </span>
                                           % endif
                                        </td>
                                        <td>${row["uptime"]}</td>
                                        <td>${row["workersTotal"]}</td>
                                        <td>${row["executorsTotal"]}</td>
                                        <td>${row["tasksTotal"]}</td>
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
  % endif
% endif

${commonfooter(messages) | n,unicode}
