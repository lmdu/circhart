from PySide6 import QtWidgets
import qt_parameters

app = QtWidgets.QApplication()

editor = qt_parameters.ParameterEditor()

# Add simple parameters
editor.add_parameter(qt_parameters.FloatParameter('float'))
editor.add_parameter(qt_parameters.StringParameter('string'))
editor.add_parameter(qt_parameters.PathParameter('path'))

# Customize parameter properties
parm = qt_parameters.PointFParameter('pointf')
parm.set_line_min(1)
parm.set_line_max(7)
parm.set_decimals(3)
editor.add_parameter(parm)

editor.show()

# Access the parameter values
print(editor.values())

app.exec()