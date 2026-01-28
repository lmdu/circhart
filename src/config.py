import os
from pathlib import Path

import yaml
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
	'APP_CITATION',
	'APP_ORG_NAME',
	'APP_ORG_DOMAIN',
	'CIRCOS_COMMAND',
	'CIRCOS_PATH',
	'CIRCOS_PARAMS'
]

ROOT_PATH = Path(__file__).parent

APP_NAME = "Circhart"
APP_BUILD = "20260120"
APP_VERSION = "0.1.0"

APP_DEBUG = False

APP_ISSUE_URL = "https://github.com/lmdu/circhart/issues"
APP_DOCUMENT_URL = "https://circhart.readthedocs.io"
APP_UPDATE_URL = "https://github.com/lmdu/circhart/releases"

APP_DESCRIPTION = """
<p>Circhart is a user-friendly graphical tool for assisting circos
running.</p>
"""

APP_CITATION = """
<p>Krzywinski M, Schein J, Birol I, et al. Circos: an information
aesthetic for comparative genomics. Genome Research. 2009;19(9):1639-1645.</p>
<p>Challis R, Richards E, Rajan J, Cochrane G, Blaxter M. BlobToolKit -
Interactive Quality Assessment of Genome Assemblies. G3 (Bethesda). 2020;10(4):1361-1374.</p>
"""

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
