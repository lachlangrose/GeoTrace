# GeoTools
GeoTools is a a QGIS plugin containing some helpful tools for extracting and analysing the orientations of geological structures. It can
be used to rapidly digitize structural traces in raster data, estimate their 3D orientations using an associated DEM, and then visualise
the results on stereonets and rose diagrams.

The trace extraction method (*Trace* tab) uses a least-cost path algorithm to "follow" linear features in the raster. This relies on a 
single-channel cost raster in which the structures of interest are represented by low values, and the background by high values. A variety of
functions for quickly calculating such a cost function have been included in the *Cost Calculator* tab.

#Installation
Clone GeoTools into your QGIS plugin path or create link to this directory. 

##Dependencies
GeoTools uses Numpy, Matplotlib, mplstereonet so you will need to make sure these are installed for your python distribution.

#Licence
GeoTools is free software licenced under the GNU licence v2


#Further Reading and Citation

If you found this tool useful, please cite *Thiele et al., 2017*. The publication (currently in prep.) also contains a more detailed description of the methods employed by this plugin.

Thiele, ST., Grose, L., Samsu, A., Micklethwaite, S., Vollgger, SA. & Cruden, S., 2017, 'A computer-assisted approach to structural interpretation of point clouds and rasters', Journal TBA