import sys
import os
import warnings 
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QGridLayout, QTextEdit, QVBoxLayout, QHBoxLayout, QFrame, QGroupBox
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from guiManager import guiManager


class GraphCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.figure.add_subplot(111)
        super().__init__(self.figure)
        self.setParent(parent)

def main():
    app = QApplication(sys.argv)

    ventana = QWidget()
    ventana.setWindowTitle("🔢 Calculadora de Ecuaciones Lineales — Visual")
    ventana.setMinimumSize(1000, 700)
    ventana.setStyleSheet("""
        QWidget {
            background: qlineargradient(
                spread:pad, x1:0, y1:0, x2:1, y2:1,
                stop:0 #e8f0ff, stop:1 #ffffff
            );
            font-family: Segoe UI, Arial;
        }
        QLabel { font-size: 14px; font-weight: bold; color: #2c3e50; }
        QLineEdit { padding: 6px; border: 1px solid #bbb; border-radius: 6px; background-color: #fff; }
        QPushButton {
            background-color: #2e86de; color: white; padding: 10px 16px; border-radius: 8px;
            font-size: 13px; font-weight: bold;
        }
        QPushButton:hover { background-color: #1f6fb1; }
        QTextEdit { border: 1px solid #ccc; border-radius: 6px; padding: 8px; background-color: #fff; font-size: 13px; }
        QGroupBox { font-size: 14px; font-weight: bold; color: #2c3e50; border: 1px solid #bbb; border-radius: 8px; margin-top: 10px; }
        QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
    """)

    layoutPrincipal = QVBoxLayout()

    # Logo
    logo_path = os.path.join(os.path.dirname(__file__), "calculadora-cientifica.png")
    if os.path.exists(logo_path):
        logo = QLabel()
        pixmap = QPixmap(logo_path).scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignCenter)
        layoutPrincipal.addWidget(logo)
    else:
        logo = QLabel("🧮")
        logo.setFont(QFont("Arial", 48))
        logo.setAlignment(Qt.AlignCenter)
        layoutPrincipal.addWidget(logo)

    titulo = QLabel("🔢 Calculadora de Sistemas de Ecuaciones Lineales (con gráfico)")
    titulo.setFont(QFont("Arial", 18, QFont.Bold))
    titulo.setAlignment(Qt.AlignCenter)
    layoutPrincipal.addWidget(titulo)

    separador = QFrame()
    separador.setFrameShape(QFrame.HLine)
    separador.setFrameShadow(QFrame.Sunken)
    layoutPrincipal.addWidget(separador)

    entradaLayout = QHBoxLayout()
    entradaFilas = QLineEdit()
    entradaFilas.setPlaceholderText("Número de filas (ej: 3)")
    entradaColumnas = QLineEdit()
    entradaColumnas.setPlaceholderText("Número de columnas (ej: 3)")
    entradaLayout.addWidget(QLabel("Filas:"))
    entradaLayout.addWidget(entradaFilas)
    entradaLayout.addSpacing(20)
    entradaLayout.addWidget(QLabel("Columnas:"))
    entradaLayout.addWidget(entradaColumnas)
    layoutPrincipal.addLayout(entradaLayout)

    botonesLayout = QHBoxLayout()
    botonGenerar = QPushButton("➕ Generar Matriz")
    botonResolver = QPushButton("✅ Resolver y Graficar")
    botonResolver.hide()  # Oculta el botón al inicio
    botonesLayout.addStretch()
    botonesLayout.addWidget(botonGenerar)
    botonesLayout.addWidget(botonResolver)
    botonesLayout.addStretch()
    layoutPrincipal.addLayout(botonesLayout)

    grupoMatriz = QGroupBox("📐 Matriz del sistema (última columna = términos independientes)")
    layoutCentral = QGridLayout()
    grupoMatriz.setLayout(layoutCentral)
    layoutPrincipal.addWidget(grupoMatriz)

    layoutPrincipal.addWidget(QLabel("📄 Resultados:"))
    texto = QTextEdit()
    texto.setReadOnly(True)
    texto.setFixedHeight(200)
    layoutPrincipal.addWidget(texto)

    layoutPrincipal.addWidget(QLabel("📊 Gráfico:"))
    grafico = GraphCanvas()
    toolbar = NavigationToolbar(grafico, ventana)
    layoutPrincipal.addWidget(toolbar)
    layoutPrincipal.addWidget(grafico, stretch=1)

    Manager = guiManager(entradaFilas, entradaColumnas, layoutCentral, botonResolver, texto, grafico)

    def mostrar_boton_resolver():
        botonResolver.show()

    botonGenerar.clicked.connect(Manager.crearMatriz)
    botonGenerar.clicked.connect(mostrar_boton_resolver)
    botonResolver.clicked.connect(Manager.resolverMatriz)

    ventana.setLayout(layoutPrincipal)
    ventana.show()
    sys.exit(app.exec_())

if __name__== "__main__":
    main()