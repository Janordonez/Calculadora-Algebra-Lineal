import sys
import matriz
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QGridLayout

app = QApplication(sys.argv)

matriz2d = []

def crearMatriz():
    filas = int(entradaFilas.text())
    columnas = int(entradaColumnas.text()) + 1
    matriz2d.clear()

    for i in range(filas):
        incognitasX = QLabel("X" + str(i+1))
        layout.addWidget(incognitasX, 4, i, 1, 1)
        fila = []
        for j in range(columnas):
            entradaMatriz = QLineEdit()
            entradaMatriz.setFixedWidth(100)
            layout.addWidget(entradaMatriz, 5 + i, j, 1, 1)
            fila.append(entradaMatriz)
        matriz2d.append(fila)

    botonCalcular = QPushButton(text="Calcular")
    botonCalcular.clicked.connect(resolverMatriz)
    layout.addWidget(botonCalcular, 5 + filas, 0, 1, columnas)

def resolverMatriz():
    matrizValores = []
    Vector = []
    
    for fila in matriz2d:
        filaValores = []
        for celda in fila:
            try:
                valor = int(celda.text())
            except ValueError:
                valor = 0
            filaValores.append(valor)
        matrizValores.append(filaValores)

    ultimaColumna = len(matrizValores[0]) - 1

    for i in range(len(matrizValores)):
        for j in range(len(matrizValores[i])):
            print(matrizValores[i][j])

    for fila in matrizValores:
        Vector.append(fila.pop(ultimaColumna))

    matriz.gauss_elimination(matrizValores, Vector)

    

    

    




ventana = QWidget()
ventana.setWindowTitle("Ejemplo Grid en PyQt")

layout = QGridLayout()

# Widgets
titulo = QLabel("Calculadora de Sistemas de ecuaciones lineales.")
entradaFilas = QLineEdit()
entradaColumnas = QLineEdit()
boton = QPushButton("Calcular")
boton.clicked.connect(crearMatriz)

# Posicionamiento
layout.addWidget(titulo, 0, 0, 1, 5)       # fila 0, columna 0, ocupa 1 fila y 2 columnas
layout.addWidget(QLabel("Número de filas:"), 1, 0)
layout.addWidget(entradaFilas, 1, 1)
layout.addWidget(QLabel("Número de columnas:"), 2, 0)
layout.addWidget(entradaColumnas, 2, 1)
layout.addWidget(boton, 3, 0, 1, 2)        # botón ocupa 2 columnas

ventana.setLayout(layout)
ventana.show()
sys.exit(app.exec_())
