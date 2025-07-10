import os
from pathlib import Path

import PySide6

__all__ = [
	'CIRCHART_BUILD',
	'CIRCHART_VERSION',
	'CIRCHART_DEBUG',
	'CIRCOS_COMMAND',
]

ROOT_PATH = Path(__file__).parent

CIRCHART_BUILD = "20250702"
CIRCHART_VERSION = "0.1.0"

CIRCHART_DEBUG = True

if os.name == 'nt':
	CIRCOS_COMMAND = str(ROOT_PATH / 'circos' / 'bin' / 'circos.exe')
else:
	CIRCOS_COMMAND = str(ROOT_PATH / 'circos' / 'bin' / 'circos')
