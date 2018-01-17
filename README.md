# ArcGIS Modelling-Toolbox

## General Description

An ArcGIS python-script based toolbox for basic data storage and processing of geological base data.

## Installation

To ensure the correct functionality of the scripts, you have to add the directory containing the ModellingToolbox folder to the PYTHONPATH environment variable. You can therefore execute following command in a commandline window (press win+R, type "cmd" and press enter):

```
SetX PYTHONPATH '%PYTHONPATH%;_PATH_TO_SOURCE_DIR_'
```

You have to replace **\_PATH_TO_SOURCE_DIR\_** with the path to the directory containing the ModellingToolbox folder.

The scripts in this ArcGIS-Toolbox need SQLAlchemy, numpy and arcpy modules to work properly. Whereas arcpy and numpy are part of the ArcGIS python installation, SQLAlchemy, typing and scipy has to be install manually. I recommend to use pip for the installation. Therefore open a terminal / command line and install SQLAlchemy with following command:

  
```
pip install SQLAlchemy
pip install typing
pip install scipy
```

Whereas SQLAlchemy and typing are installed without failures normally, scipy may cause problems, because scipy requires a pre-installation of blast or boost libraries. If this occurs to you, you can look for a binary compilation of the scipy package or try the following code:

```
python.exe -m pip install --user numpy scipy matplotlib
```

If none of the installations work, try to check for multiple python installations and run the pip command with the python.exe inside your python directory of your ArcGIS installation.

Additionally you can find installation hints for scipy on the [scipy website](https://www.scipy.org/install.html).

After the installation of SQLAlchemy you have to add this toolbox to your ArcToolbox section. Therefore open the ArcToolbox section if it isn't open yet (Geoprocessing -> ArcToolbox), right click on ArcToolbox (the folder on top of the list inside the ArcToolbox section) and select "Add Toolbox". In the following "Add Toolbox" window you have to select the "Modelling Toolbox.tbx" file in this directory.

The documentation uses the basicstrap sphinx template package. This can be installed as follows:

```
pip install sphinxjp.themes.basicstrap
```

More information to configure the documentation theme can be found on the [theme homepage](https://pythonhosted.org/sphinxjp.themes.basicstrap/index.html).

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