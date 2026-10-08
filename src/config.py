import os
import sys
from pathlib import Path

import apsw
import yaml
import pygros
import pyfastx
import PySide6
from PySide6.QtCore import *

__all__ = [
	'APP_ID',
	'APP_NAME',
	'APP_BUILD',
	'APP_VERSION',
	'APP_DEBUG',
	'APP_ISSUE_URL',
	'APP_DOCUMENT_URL',
	'APP_UPDATE_URL',
	'APP_DESCRIPTION',
	'APP_ACKNOWLEDGE',
	'APP_CITATION',
	'APP_ORG_NAME',
	'APP_ORG_DOMAIN',
	'CIRCOS_COMMAND',
	'CIRCOS_PATH',
	'CIRCOS_PARAMS'
]

ROOT_PATH = Path(__file__).parent

APP_NAME = "Circhart"
APP_BUILD = "20261008"
APP_VERSION = "0.8.0"

APP_DEBUG = False

APP_ISSUE_URL = "https://github.com/lmdu/circhart/issues"
APP_DOCUMENT_URL = "https://circhart.readthedocs.io"
APP_UPDATE_URL = "https://github.com/lmdu/circhart/releases"

APP_DESCRIPTION = """
<h2>Circhart</h2>
<p><b>Version</b> {} <b>Build</b> {}</p>
<p>Circhart is a user-friendly and flexible graphical tool for facilitating the creation of circos
and snail plots.</p>
""".format(APP_VERSION, APP_BUILD)

APP_CITATION = """
<p>If you use the following features in this application, please cite the corresponding papers.</p>
<p><b>Circos Plot</b></p>
<p>Please cite: Krzywinski M, et al. Circos: an information aesthetic for comparative genomics. 
Genome Research. 2009. 19(9):1639-1645. 
<a href="https://doi.org/10.1101/gr.092759.109">doi:10.1101/gr.092759.109</a></p>
<p><b>Snail Plot</b></p>
<p>Please cite: Challis R, et al. BlobToolKit - Interactive Quality Assessment of Genome Assemblies. 
G3 (Bethesda). 2020. 10(4):1361-1374. 
<a href="https://doi.org/10.1534/g3.119.400908">doi:10.1534/g3.119.400908</a></p>
"""

APP_ACKNOWLEDGE = """
<table cellspacing="10" align="left">
	<tr>
		<th>Name</th> 
		<th>Version</th>
		<th>Description</th>
	</tr>
	<tr>
		<td>
			<a href="https://www.python.org/">Python</a>
		</td>
		<td>v{python}</td>
		<td>A popular programming language</td>
	</tr>
	<tr>
		<td>
			<a href="https://github.com/rogerbinns/apsw">APSW</a>
		</td>
		<td>v{apsw}</td>
		<td>Another Python SQLite wrapper</td>
	</tr>
	<tr>
		<td>
			<a href="https://doc.qt.io/qtforpython-6/index.html">PySide6</a>
		</td>
		<td>v{pyside}</td>
		<td>Qt for Python offers the official Python bindings for Qt</td>
	</tr>
	<tr>
		<td>
			<a href="https://github.com/lmdu/pyfastx">pyfastx</a>
		</td>
		<td>v{pyfastx}</td>
		<td>A package for parsing FASTA formatted file</td>
	</tr>
	<tr>
		<td>
			<a href="https://github.com/yaml/pyyaml">PyYAML</a>
		</td>
		<td>v{pyyaml}</td>
		<td>A full-featured YAML processing framework for Python</td>
	</tr>
	<tr>
		<td>
			<a href="https://github.com/lmdu/pygros">pygros</a>
		</td>
		<td>v{pygros}</td>
		<td>A package for finding genomic range overlaps based on cgranges</td>
	</tr>
	<tr>
		<td>
			<a href="https://github.com/lh3/cgranges">cgranges</a>
		</td>
		<td>v0.1.1</td>
		<td>A small C library for genomic interval overlap queries</td>
	</tr>
	<tr>
		<td>
			<a href="https://www.circos.ca/">circos</a>
		</td>
		<td>v0.69-10</td>
		<td>A software package for visualizing data and information</td>
	</tr>
	<tr>
		<td>
			<a href="https://github.com/genomehubs/blobtk">blobtk</a>
		</td>
		<td>v0.8.3</td>
		<td>A library used for generating snail plots</td>
	</tr>
</table>
""".format(
	python = sys.version.split()[0],
	pyside = PySide6.__version__,
	pyfastx = pyfastx.__version__,
	pygros = pygros.__version__,
	pyyaml = yaml.__version__,
	apsw = apsw.apswversion()
)

APP_ORG_NAME = "DuLab"
APP_ORG_DOMAIN = "big.cdu.edu.cn"

APP_ID = "{}.{}.{}.{}".format(APP_ORG_NAME, APP_NAME, APP_NAME, APP_VERSION)

CIRCOS_PATH = ROOT_PATH / 'circos'

if os.name == 'nt':
	CIRCOS_COMMAND = str(CIRCOS_PATH / 'bin' / 'circos.exe')
else:
	CIRCOS_COMMAND = str(CIRCOS_PATH / 'bin' / 'circos')

file = QFile(':/plots.yml')
file.open(QIODevice.ReadOnly | QIODevice.Text)
stream = QTextStream(file)
CIRCOS_PARAMS = yaml.safe_load(stream.readAll())
