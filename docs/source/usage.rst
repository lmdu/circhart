Draw circos plot
================

Data types
----------

Prior to drawing circos plot, you should prepare data for plotting. Circhart has five data types including karyotype (band) data, plot data, link data, loci data, text data.

Karyotype data
^^^^^^^^^^^^^^

The karyotype data defines the chromosomes and cytogenetic bands. It has seven columns: type, parent, name, label, start, end, color. The columns are generally separated by a white space. The name column is an unique id for each chromosome or band. The name is very important, as the other data types must use this name to distinguish different chromosomes.

The description of each column:

.. list-table::
	:header-rows: 1
	:align: center

	* - Column
	  - Description
	* - type
	  - chr (for karyotype) or band (for band data)
	* - parent
	  - \- (for karyotype) or chromosome name (for band data)
	* - label
	  - chromosome or band label
	* - start
	  - start position
	* - end
	  - end position
	* - color
	  - color name

The karyotype data example:

.. code::

	chr - hs1 NC_060925.1 0 248387328 chr1
	chr - hs2 NC_060926.1 0 242696752 chr2
	chr - hs3 NC_060927.1 0 201105948 chr3
	...

The band data example:

.. code::

	band hs1 p36.33 p36.33 0 1735965 gneg
	band hs1 p36.32 p36.32 1735965 4816989 gpos25
	band hs1 p36.31 p36.31 4816989 6629068 gneg
	band hs1 p36.23 p36.23 6629068 8634052 gpos25
	band hs1 p36.22 p36.22 8634052 12044143 gneg
	...

Plot data
^^^^^^^^^

The plot data has four columns: chrom, start, end, value. The plot data is used to plot line, scatter, histogram and heatmap tracks.

The description of each column:

.. list-table::
	:header-rows: 1
	:align: center

	* - Column
	  - Description
	* - chrom
	  - chromosome name
	* - start
	  - start position
	* - end
	  - end position
	* - value
	  - integer or decimal

Plot data example:

.. code::

	hs1 1000 2000 0.546
	hs1 2000 3000 0.423
	hs2 4000 6000 0.379
	...

Text data
^^^^^^^^^

The text data has the same columns with the plot data. The only difference is that the value column contains text instead of numbers. The text data is used to plot text track.

Text data example:

.. code::

	hs1 144134 146717 SEPTIN14P14
	hs1 148562 152332 CICP3
	hs1 372945 388041 NOC2L
	...

Loci data
^^^^^^^^^

The loci data has three columns: chrom, start, end. Each row defines an interval in a chromosome. The loci data used to plot tile, connector and highlight tracks.

Loci data example:

.. code::

	hs1 144134 146717
	hs1 148562 152332
	hs1 372945 388041
	...

Link data
^^^^^^^^^

The link data has six columns: chrom1, start1, end1, chrom2, start2, end2. Each row has two intervals on the same or different chromosomes. The link data used to plot link track.

Link data example:

.. code::

	hs1 1000 3000 hs10 2500 3800
	hs3 7000 9500 hs8 4000 7000
	hs7 500 1500 hs12 5000 6000
	...

Prepare data
------------

