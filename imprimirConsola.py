from PyQt5.QtWidgets import QApplication

class imprimirConsola:
    """Clase para redirigir print a un QTextEdit"""
    def __init__(self, widget):
        self.widget = widget

    def write(self, mensaje):
        self.widget.append(mensaje)  # agrega el texto al QTextEdit
        QApplication.processEvents()  # actualiza la GUI inmediatamente

    def flush(self):
        pass  # necesario para compatibilidad con sys.stdout