# ArcGIS Modelling-Toolbox

## General Description

An ArcGIS python-script based toolbox for basic data storage and processing of geological base data.

## Installation

The scripts in this ArcGIS-Toolbox need SQLAlchemy, numpy and arcpy modules to work properly. Whereas arcpy and numpy are part of the ArcGIS python installation, SQLAlchemy has to be install manually. I recommend to use pip for the installation. Therefore open a terminal / command line and install SQLAlchemy with following command:

  
```
pip install SQLAlchemy
```

If the installation doesn't work, try to check for multiple python installations and run pip in the python.exe containing directory of your ArcGIS installation.

After the installation of SQLAlchemy you have to add this toolbox to your ArcToolbox section. Therefore open the ArcToolbox section if it isn't open yet (Geoprocessing -> ArcToolbox), right click on ArcToolbox (the folder on top of the list inside the ArcToolbox section) and select "Add Toolbox". In the following "Add Toolbox" window you have to select the "Modelling-Toolbox.tbx" file in this directory.

## System Requirements

This toolbox was tested with ArcMap version 10.2.2 and version 10.5

## Detailed Description

The ArcGIS-Toolbox is divided in four parts:

1. Import
2. Data processing
3. Export
4. Miscellaneous

#### 1. Import

The scripts in the Toolbox can handle following geological objects:
- point sets
- lines
- wells

Polygons can be stored as closed lines. 

#### 2. Data Processing

--- in preparation ---

#### 3. Export

The geological data can be exported to Midland Valley Move files as well as SKUA-GOCAD Ascii files.

#### 4. Miscellaneous

--- in preparation ---