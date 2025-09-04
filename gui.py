import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QGridLayout, QTextEdit
from guiManager import guiManager

app = QApplication(sys.argv)

ventana = QWidget()
ventana.setWindowTitle("Calculadora")

layout = QGridLayout()

# Widgets
titulo = QLabel("Calculadora de Sistemas de ecuaciones lineales.")
entradaFilas = QLineEdit()
entradaColumnas = QLineEdit()
boton = QPushButton("Calcular")
botonCalcular = QPushButton(text="Calcular")
texto = QTextEdit()
texto.setFixedWidth(600)

Manager = guiManager(entradaFilas, entradaColumnas, layout,botonCalcular,texto)

botonCalcular.clicked.connect(Manager.resolverMatriz)
boton.clicked.connect(Manager.crearMatriz)

# Posicionamiento
# Título
layout.addWidget(titulo, 0, 0, 1, 3)  # fila 0, columna 0, ocupa 2 columnas

# Etiquetas y entradas
layout.addWidget(QLabel("Número de filas:"), 1, 0, 1, 1)
layout.addWidget(entradaFilas, 1, 1, 1, 1)

layout.addWidget(QLabel("Número de columnas:"), 2, 0, 1, 1)
layout.addWidget(entradaColumnas, 2, 1, 1, 1)

# Botón
layout.addWidget(boton, 3, 0, 1, 2)  # ocupa 2 columnas para centrar

# Widget para mostrar resultados
layout.addWidget(texto, 18, 0, 1, 2)  # ocupa 2 columnas debajo del botón

            

texto.setReadOnly(True)
ventana.setLayout(layout)
ventana.show()
sys.exit(app.exec_())
