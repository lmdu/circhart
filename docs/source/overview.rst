Overview
========

.. figure:: _static/overview.svg
	:width: 700
	:align: center

	The graphical user interface of circhart

Toolbar
-------

.. list-table:: The description of each icon in the toolbar
	:header-rows: 1
	:align: center

	* - Icon
	  - Function
	* - |prepdata|
	  - menus for preparing plotting data
	* - |newcircos|
	  - open circos plot creation dialog
	* - |addtrack|
	  - add circos plot track
	* - |newsnail|
	  - open snail plot creation dialog
	* - |zoomin|
	  - zoom in plot
	* - |zoomout|
	  - zoom out plot
	* - |export|
	  - save plot to image file
	* - |citation|
	  - view the tool citations
	* - |update|
	  - redraw the circos or snail plot

Data List
---------

The ``name`` and ``type`` of imported or prepared data will be displayed in **Data List**.

#. You can click data name to view the data contents.

#. You can change the data name using right click menu *Rename*.

#. You can delete the data from list using right click menu *Delete*.

#. For data imported from file, you can change the file path of data using right click menu *Change Path*.

We use two icons to distinguish between different data types:

.. list-table:: The description of each icon in the data list
	:header-rows: 1
	:align: center

	* - Icon
	  - Description
	* - |pdata|
	  - imported or generated data that can be used directly for plotting is stored entirely within ``Circhart``, with no dependency on external files
	* - |dfile|
	  - imported file, only the first few rows are imported for preview, relies on external file path during use, When using the same project file on different operating systems

Plot List
---------

The ``name`` and ``type`` of generated plots will be displayed in **Plot List**.

#. You can click plot name to view the plot image.

#. You can change the plot name using right click menu *Rename*.

#. You can delete the plot from list using right click menu *Delete*.

We also use two icons to represent different plot types:

.. list-table:: The description of each icon in the plot list
	:header-rows: 1
	:align: center

	* - Icon
	  - Description
	* - |circos|
	  - circos plot
	* - |snail|
	  - snail plot

Data and Plot Viewer
--------------------

The data content or plot image will be displayed in this viewer. For plot viewer, you can use mouse wheel to zoom in or zoom out plot.

Parameter Panel
---------------

You can adjust the plotting parameters in parameter panel.


.. |prepdata| image:: _static/data.svg
	:width: 24
	:height: 24

.. |newcircos| image:: _static/new.svg
	:width: 24
	:height: 24

.. |addtrack| image:: _static/track.svg
	:width: 24
	:height: 24

.. |newsnail| image:: _static/spiral.svg
	:width: 24
	:height: 24

.. |zoomin| image:: _static/zoomin.svg
	:width: 24
	:height: 24

.. |zoomout| image:: _static/zoomout.svg
	:width: 24
	:height: 24

.. |export| image:: _static/save.svg
	:width: 24
	:height: 24

.. |citation| image:: _static/citation.svg
	:width: 24
	:height: 24

.. |update| image:: _static/refresh.svg
	:width: 24
	:height: 24

.. |pdata| image:: _static/pdata.svg
	:width: 24
	:height: 24

.. |dfile| image:: _static/file.svg
	:width: 24
	:height: 24

.. |circos| image:: _static/circos.svg
	:width: 24
	:height: 24

.. |snail| image:: _static/snail.svg
	:width: 24
	:height: 24
