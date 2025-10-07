import sys
import os

# Asegura que el directorio 'gui' esté en el path
sys.path.append(os.path.join(os.path.dirname(__file__), "gui"))

from PyQt6.QtWidgets import QApplication
from gui.EntradaGui import EntradaGui

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EntradaGui()
    window.show()
    sys.exit(app.exec())