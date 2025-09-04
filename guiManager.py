from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QTextEdit
import warnings_1

from imprimirConsola import imprimirConsola
import matriz
import sys
from fractions import Fraction

class guiManager:

    def __init__(self, entradaFilas, entradaColumnas, layout, botonCalcular, texto):
        self.entradaFilas = entradaFilas
        self.entradaColumnas = entradaColumnas
        self.layout = layout
        self.botonCalcular = botonCalcular
        self.texto = texto

    matriz2d = []

    def crearMatriz(self):
        while True:
            filas = 0
            columnas = 0
            try: filas = int(self.entradaFilas.text())
            except ValueError:
                self.entradaFilas.clear()
                self.entradaColumnas.clear()
                warnings_1.mostrarAviso(str(filas) if filas else 0)
                return
                

            try: columnas = int(self.entradaColumnas.text()) + 1
            except ValueError:
                self.entradaColumnas.clear()
                self.entradaFilas.clear()
                warnings_1.mostrarAviso(str(filas) if filas else 0)
                return

            self.matriz2d.clear()

            for i in range(columnas -1):
                incognitasX = QLabel("X" + str(i+1))
                self.layout.addWidget(incognitasX, 4, i, 1, 1)
                
            for i in range(filas):
                fila = []
                for j in range(columnas):
                    
                    
                    entradaMatriz = QLineEdit()  
                    self.layout.addWidget(entradaMatriz, 5 + i, j, 1, 1)
                    fila.append(entradaMatriz)
                self.matriz2d.append(fila)

            self.layout.removeWidget(self.botonCalcular)
            self.layout.addWidget(self.botonCalcular, 5 + filas, 0, 1, columnas)
            break

    def resolverMatriz(self):
        while True:
            matrizValores = []
            Vector = []
            
            for fila in self.matriz2d:
                filaValores = []
                for celda in fila:
                    try:
                        valor = 0
                        valor = Fraction(celda.text())
                    except ValueError:
                        warnings_1.mostrarAviso(valor)
                        return
                    filaValores.append(valor)
                matrizValores.append(filaValores)

            ultimaColumna = len(matrizValores[0]) - 1

            for fila in matrizValores:
                Vector.append(fila.pop(ultimaColumna))

            self.texto.clear()
            
            sys.stdout = imprimirConsola(self.texto)

            matriz.gauss_elimination(matrizValores, Vector)
            break
        
        