# warnings_1.py
from PyQt5.QtWidgets import QMessageBox

def mostrarAviso(mensaje, titulo="Aviso"):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setWindowTitle(titulo)
    msg.setText(str(mensaje))
    msg.exec_()
