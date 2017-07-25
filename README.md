# GeoTools
GeoTools is a a QGIS plugin containing some helpful tools for extracting and analysing the orientations of geological structures. It can
be used to rapidly digitize structural traces in raster data, estimate their 3D orientations using an associated DEM, and then visualise
the results on stereonets and rose diagrams.

The trace extraction method (*Trace* tab) uses a least-cost path algorithm to "follow" linear features in the raster. This relies on a 
single-channel cost raster in which the structures of interest are represented by low values, and the background by high values. A variety of
functions for quickly calculating such a cost function have been included in the *Cost Calculator* tab.

# Installation
Clone GeoTools into your QGIS plugin path or create link to this directory. 

## Dependencies
GeoTools uses `Numpy`, `Matplotlib`, `mplstereonet` and `scikit-image`, so you will need to make sure these are installed for your python distribution.
QGis should come bundled with `Numpy` and `Matplotlib`. The other packages can be installed using pip. 

### Detailed instructions for MS Windows users
Installing `mplstereonet` and `scikit-image` on Windows can be a little tricky, as *skimage* contains uncompiled c-code. The following instructions should work
in most cases however:
1. Open the start menu and search for *OSGeo4W Shell*. Right-click on it and select *Run as administrator*. This tool gives you access to the qGIS version of python
2. Check pip (a python package manager) is up to date with the following: `python -m pip install --upgrade setuptools`
3. Install *mplstereonet* first, using the following command: `python -m pip install mplstereonet`
4. Download precompiled 32 bit python wheels for *cython* and *scikit-image* 2.7 (otherwise you need to install a c-compiler) from:
	* [cython] (http://www.lfd.uci.edu/~gohlke/pythonlibs/#cython) 
	* [scikit-image] (http://www.lfd.uci.edu/~gohlke/pythonlibs/#scikit-image)
5. Navigate the console to the directory containing these downloaded wheels: `cd C:/DirectoryName/Wheels`
6. Install each package using pip: `python -m pip install Cython-0.26-cp27-cp27m-win32.whl` and `python -m pip install scikit_image-0.13.0-cp27-cp27m-win32.whl`

Assuming these all installed correctly, you should now be set to use the plugin.

These can be 
# Licence
GeoTools is free software licenced under the GNU licence v2


# Further Reading and Citation

If you found this tool useful, please cite *Thiele et al., 2017*. The publication (currently in prep.) also contains a more detailed description of the methods employed by this plugin.

Thiele, ST., Grose, L., Samsu, A., Micklethwaite, S., Vollgger, SA. & Cruden, S., 2017, 'Rapid, semi-automatic fracture and contact mapping for the digital age', (In prep.)