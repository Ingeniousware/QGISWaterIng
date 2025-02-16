"""
***************************************************************************
    customdialog.py
    ---------------------
    Date                 : Enero 2025
    Copyright            : (C) 2025 by Ingeniowarest
    Email                : 
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Ingenioware                                                       *
*                                                                         *
***************************************************************************
"""

"""
Ejemplo 1: Mensaje de Información

    import sys
    from PyQt5.QtWidgets import QApplication, QMessageBox

    app = QApplication(sys.argv)

    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setText("Este es un mensaje de información.")
    msg.setWindowTitle("Información")
    msg.setStandardButtons(QMessageBox.Ok)

    msg.exec_()
    
Ejemplo 2: Mensaje de Advertencia

    import sys
    from PyQt5.QtWidgets import QApplication, QMessageBox

    app = QApplication(sys.argv)

    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText("Este es un mensaje de advertencia.")
    msg.setWindowTitle("Advertencia")
    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

    retval = msg.exec_()
    print("Valor de retorno:", retval)
    
Ejemplo 3: Mensaje de Error

    import sys
    from PyQt5.QtWidgets import QApplication, QMessageBox

    app = QApplication(sys.argv)

    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText("Este es un mensaje de error.")
    msg.setWindowTitle("Error")
    msg.setStandardButtons(QMessageBox.Retry | QMessageBox.Abort | QMessageBox.Ignore)

    retval = msg.exec_()
    print("Valor de retorno:", retval)
    
Ejemplo 4: Mensaje con Pregunta

    import sys
    from PyQt5.QtWidgets import QApplication, QMessageBox

    app = QApplication(sys.argv)

    msg = QMessageBox()
    msg.setIcon(QMessageBox.Question)
    msg.setText("¿Deseas continuar?")
    msg.setWindowTitle("Pregunta")
    msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msg.setDefaultButton(QMessageBox.No)

    retval = msg.exec_()
    if retval == QMessageBox.Yes:
        print("El usuario seleccionó 'Sí'.")
    else:
        print("El usuario seleccionó 'No'.")
        

    import sys
    from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox
    from PyQt5.QtGui import QIcon
    from PyQt5.QtCore import pyqtSlot

    def window():
    app = QApplication(sys.argv)
    win = QWidget()
    button1 = QPushButton(win)
    button1.setText("Show dialog!")
    button1.move(50,50)
    button1.clicked.connect(showDialog)
    win.setWindowTitle("Click button")
    win.show()
    sys.exit(app.exec_())
        
    def showDialog():
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Information)
    msgBox.setText("Message box pop up window")
    msgBox.setWindowTitle("QMessageBox Example")
    msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    msgBox.buttonClicked.connect(msgButtonClick)

    returnValue = msgBox.exec()
    if returnValue == QMessageBox.Ok:
        print('OK clicked')
    
    def msgButtonClick(i):
    print("Button clicked is:",i.text())
   
    
"""
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QFormLayout, QPushButton, QMessageBox # type: ignore


class CustomDialog(QDialog):
    def __init__(self, title="", description="", parent=None):
        super().__init__(parent)
        self.Title = title
        self.Description = description
        self.setWindowTitle(self.Title)
        layout = QVBoxLayout()
        label = QLabel(self.Description)
        layout.addWidget(label)
        close_button = QPushButton('Aceptar')
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)
        self.setLayout(layout)
        
        #Esto es bueno para mandar un cuadro de dialogo a traer información.
        # self.setWindowTitle('Cuadro de Diálogo Editable')
        # self.layout = QFormLayout()
        # self.title_input = QLineEdit(self)
        # self.title_input.setPlaceholderText('Ingresa el título del cuadro de diálogo')
        # self.layout.addRow('Título:', self.title_input)
        # self.message_input = QLineEdit(self)
        # self.message_input.setPlaceholderText('Ingresa el mensaje del cuadro de diálogo')
        # self.layout.addRow('Mensaje:', self.message_input)
        # self.update_button = QPushButton('Actualizar')
        # self.update_button.clicked.connect(self.update_dialog)
        # self.layout.addWidget(self.update_button)
        # self.setLayout(self.layout)
    
    def update_dialog(self):
        self.setWindowTitle(self.title_input.text())
        self.layout.itemAt(2).widget().setText(self.message_input.text())

class InputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Cuadro de Diálogo de Entrada')
        self.layout = QFormLayout()
        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText('Ingresa tu nombre')
        self.layout.addRow('Nombre:', self.name_input)
        self.age_input = QLineEdit(self)
        self.age_input.setPlaceholderText('Ingresa tu edad')
        self.layout.addRow('Edad:', self.age_input)
        self.submit_button = QPushButton('Enviar')
        self.submit_button.clicked.connect(self.submit_data)
        self.layout.addWidget(self.submit_button)
        self.setLayout(self.layout)
    
    def submit_data(self):
        name = self.name_input.text()
        age = self.age_input.text()
        self.close()
        # QMessageBox.information(self, 'Datos Ingresados', f'Nombre: {name}\nEdad: {age}')
        # QMessageBox.error(self, 'Datos Ingresados')


def show_custom_dialog(title="", description=""):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle(title)
    msg.setText(description)
    msg.setStandardButtons(QMessageBox.Ok)

    msg.exec_()
    # dialog = CustomDialog(title, description)
    # dialog.exec_()
    
def show_input_dialog():
    dialog = InputDialog()
    dialog.exec_()