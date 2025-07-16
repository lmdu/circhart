import os
from pathlib import Path

import PySide6

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
	'APP_ORG_NAME',
	'APP_ORG_DOMAIN',
	'CIRCOS_COMMAND',
]

ROOT_PATH = Path(__file__).parent

APP_NAME = "Circhart"
APP_BUILD = "20250702"
APP_VERSION = "0.1.0"

APP_DEBUG = True

APP_ISSUE_URL = "https://github.com/lmdu/circhart/issues"
APP_DOCUMENT_URL = "https://circhart.readthedocs.io"
APP_UPDATE_URL = "https://github.com/lmdu/circhart/releases"

APP_DESCRIPTION = """
<p>Circhart is a user-friendly graphical tool for assisting circos
running.</p>
"""

APP_ORG_NAME = "DuLab"
APP_ORG_DOMAIN = "big.cdu.edu.cn"

APP_ID = "{}.{}.{}.{}".format(APP_ORG_NAME, APP_NAME, APP_NAME, APP_VERSION)

if os.name == 'nt':
	CIRCOS_COMMAND = str(ROOT_PATH / 'circos' / 'bin' / 'circos.exe')
else:
	CIRCOS_COMMAND = str(ROOT_PATH / 'circos' / 'bin' / 'circos')


