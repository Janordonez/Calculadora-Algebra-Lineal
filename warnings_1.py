from PyQt5.QtWidgets import QMessageBox

def mostrarAviso(valor):
    msg = QMessageBox()
    msg.setWindowTitle("Error!")
    msg.setText("Campo vacio o Caracter inválido!" + " " + str(valor))
    msg.exec_()