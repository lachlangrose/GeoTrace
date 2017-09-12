# GeoTrace
GeoTrace is a a QGIS plugin containing some helpful tools for extracting and analysing the orientations of geological structures. It can
be used to rapidly digitize structural traces in raster data, estimate their 3D orientations using an associated DEM, and then visualise
the results on stereonets and rose diagrams.

The trace extraction method (*Trace* tab) uses a least-cost path algorithm to "follow" linear features in the raster. This relies on a 
single-channel cost raster in which the structures of interest are represented by low values, and the background by high values. A variety of
functions for quickly calculating such a cost function have been included in the *Cost Calculator* tab.

# Installation
The plugin can be in two ways.
1. The prefered option is to use the QGIS plugin repository as this will retrieve the most recent stable version of the plugin. To do this use the plugin manager in QGIS and select experimental plugins. 
2. Clone (or download and unzip) the GeoTrace directory into your QGIS plugin path.
    * On windows, this path will be something like `C:/Users/USERNAME/.qgs2/python/plugins`. Note that you may need to create the `plugins` folder.
    * On Linux the plugin can be cloned to any directory and then the relevant files are copied to the correct locations using the by running the command 'make deploy' 
## Dependencies
GeoTrace uses `Numpy`, `Matplotlib`, `mplstereonet` and `scikit-image`, so you will need to make sure these are installed for your python distribution.
QGis should come bundled with `Numpy` and `Matplotlib`. The other packages can be installed using pip. 

### Detailed instructions for MS Windows users
Installing `mplstereonet` and `scikit-image` on Windows can be a little tricky, as *skimage* contains uncompiled c-code. The following instructions should work
in most cases however:
1. Open the start menu and search for *OSGeo4W Shell*. Right-click on it and select *Run as administrator*. This tool gives you access to the qGIS version of python
2. Check pip (a python package manager) is up to date with the following: `python -m pip install --upgrade setuptools`
3. Install *mplstereonet* first, using the following command: `python -m pip install mplstereonet`
4. Download precompiled 32 or 64 bit (depending on your version of QGIS) python wheels for *cython* and *scikit-image* 2.7 (otherwise you need to install a c-compiler) from:
	- http://www.lfd.uci.edu/~gohlke/pythonlibs/#cython (32 Bit: `Cython-0.26-cp27-cp27m-win32.whl`, 64 Bit: `Cython‑0.26.1‑cp27‑cp27m‑win_amd64.whl`)
	- http://www.lfd.uci.edu/~gohlke/pythonlibs/#scikit-image (32 Bit: `scikit_image-0.13.0-cp27-cp27m-win32.whl`, 64 Bit: `scikit_image‑0.13.0‑cp27‑cp27m‑win_amd64.whl`)
	
5. Navigate the console to the directory containing these downloaded wheels (e.g. `cd C:/SOME_DIRECTORY_NAME/`)
6. Install each package using pip: `python -m pip install Cython-0.26-cp27-cp27m-win32.whl` and `python -m pip install scikit_image-0.13.0-cp27-cp27m-win32.whl` (n.b. if you downloaded the 64 bit files the filename will change from `-win32.whl` to `-win_amd64.whl`)
7. Start/restart QGIS

Assuming these all installed correctly, you should now be set to use the plugin.
### Linux
1. Open a terminal window 'ctrl+alt+t'
2. Install *mplstereonet* first, using the following command: `sudo pip install mplstereonet` 
3. Install *scikit-image* using the following command: 'sudo pip install scikit-image'  
4. Start/restart QGIS

# Usage Instructions
On launching QGIS for the first time, the plugin needs to be activated using the QGIS plugin manager (*Plugins->Manage and Install Plugins...*). Providing the plugin has been
installed to the correct directory (see above), `GeoTrace` should appear in the list of available plugins. Make sure it's checked, and with some luck QGIS won't complain about it
(throw errors).

Assuming this worked, a friendly compass icon should appear in the toolbar somewhere. Click this to launch the plugin. A window-pane should then appear, containing plugin GUI. This
is organised into 5 tabs, each of which is described below.

## Trace tab

The trace tab is used for computer-assisted digitization. Before starting, select:
	- An output layer (polyline .shp file) to write digitized traces to
	- mA point layer to store the control points in (optional)
	- A cost layer. This must be a one-channel raster, in which traces will *follow* low values. (Though the *Invert Cost* check will make the trace follow high values). The 'Cost Calculator* tab can be used to assist creation of the single-channel cost raster.
	- A DEM layer, used to estimate 3D orientations from the traces (optional)

Once the relevent information has been set, start interpreting by clicking the `Start Digitizing` button.
Left-click adds control points to your trace and Right-Click completes a trace. Hit *Backspace* to undo.

## Advanced Trace

The Advanced trace tab is used to generate traces from predefined control points. This uses a *Cost layer* and writes to an *Output layer*, as above, but rather than requiring manually 
inserted control points it takes a point feature layer (*Control Points*) and ID field defining which trace each point belongs to (*Unique ID Field*), and will then automatically generate traces
on clicking `Run`.

## Cost Calculator

This tab wraps a variety of python functions from the scikit-image package for easy generation of cost rasters. Please refer to the scikit-image (http://scikit-image.org/) website for detailed
descriptions of each of these functions.

## Stereonet

The stereonet tab can be used to plot stereonets of planar orientation estimates (strike/dip or dip/dip direction) created using this plugin, or otherwise. Simply select the layer
and associated fields containing the orientation estimates and then use the plotting tools to draw the stereonet.

## Rose

This tab works as above, but creates a rose diagram rather than a stereonet.

# Licence
GeoTrace is free software licenced under the GNU licence v2


# Further Reading and Citation

If you found this tool useful, please cite *Thiele et al., 2017*. The publication (currently under review) also contains a more detailed description of the methods employed by this plugin.

Thiele, S. T., Grose, L., Samsu, A., Micklethwaite, S., Vollgger, S. A., and Cruden, A. R.: Rapid, semi-automatic fracture and contact mapping for point clouds, images and geophysical data, Solid Earth Discuss., https://doi.org/10.5194/se-2017-83, In Review, 2017 

