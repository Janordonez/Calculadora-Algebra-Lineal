from PyQt5.QtWidgets import QMessageBox

def mostrarAviso(valor):
    msg = QMessageBox()
    msg.setWindowTitle("Error!")
    msg.setText("Numero Invalido!" + " " + str(valor))
    msg.exec_()