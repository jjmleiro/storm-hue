Storm-HUE: Apache Storm HUE Application
=======================================

Storm-HUE is a [HUE](http://www.gethue.com) application to admin and manage a pool of [Apache Storm](http://storm.apache.org/) topologies. 

Features
--------
   * Management operations (Start & Stop topologies, Rebalances).
   * Custom Dashboards based on retrieving metrics data
   * Config validator at HUE start

Requirements
------------
- [HUE 3.8](http://www.gethue.com) or higher.
- Storm Client in the same Hue Server.
- [ReportLab 2.X](http://www.reportlab.com/) for Python 2.5 or 2.6. ReportLab 3.X requires Python versions 2.7 or higher.

Main Stack
----------
   * Python 
   * Django 
   * Mako
   * jQuery
   * Bootstrap

Installation
------------
To get the Storm-HUE app integrated and running in your HUE deployment:

    For Python 2.5 or 2.6
    $ sudo $HUE_HOME/build/env/bin/python $HUE_HOME/build/env/bin/pip install "reportlab<3.0"
    
    For Python 2.7 or higher.
    $ sudo $HUE_HOME/build/env/bin/python $HUE_HOME/build/env/bin/pip install reportlab
    
    $ git clone https://github.com/keedio/storm-hue.git
    $ mv storm-hue/storm $HUE_HOME/apps
    $ cd $HUE_HOME/apps
    $ sudo ../tools/app_reg/app_reg.py --install storm --relative-paths
    $ chown -R hue: storm/

Modify the hue.ini config file as follows and restart HUE. 

HUE.ini Config section
----------------------
Configs needed in hue.ini config file.

    [storm]
        # The URL of the STORM REST service
        # default 
        # storm_ui_server=localhost
        # storm_ui_port=8080
        # storm_ui_log_port=8000
        storm_ui_server=localhost
        storm_ui_port=8080
        storm_ui_log_port=8000
        
        # Storm-UI URL paths. Uncomment to modify them if necessary. 
        ## storm_ui_cluster=/cluster/summary
        ## storm_ui_supervisor=supervisor/summary
        ## storm_ui_topologies=/topology/summary
        ## storm_ui_topology=/topology/
        ## storm_ui_configuration=/cluster/configuration

Compile locales
---------------
To compile the locales:

Set the ROOT variable in the Makefile file pointing to the HUE installation path.

Compile with make.

    $ cd $HUE_HOME/apps/storm
    $ sudo make compile-locale

Restart HUE.

License
-------
Apache License, Version 2.0
http://www.apache.org/licenses/LICENSE-2.0

--
Jose Juan Martínez <jjmartinez@keedio.com>

