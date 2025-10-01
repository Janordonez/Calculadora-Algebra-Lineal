from PyQt5.QtWidgets import QLineEdit

class guiManager:
    def __init__(self, entradaFilas, entradaColumnas, layoutCentral, botonResolver, texto, grafico):
        self.entradaFilas = entradaFilas
        self.entradaColumnas = entradaColumnas
        self.layoutCentral = layoutCentral
        self.botonResolver = botonResolver
        self.texto = texto
        self.grafico = grafico
        self.matriz_inputs = []

    def crearMatriz(self):
        try:
            filas = int(self.entradaFilas.text())
            columnas = int(self.entradaColumnas.text())
        except Exception:
            self.texto.setText("Error: Ingrese números válidos.")
            return
        for i in reversed(range(self.layoutCentral.count())):
            self.layoutCentral.itemAt(i).widget().setParent(None)
        self.matriz_inputs = []
        for i in range(filas):
            fila_inputs = []
            for j in range(columnas):
                e = QLineEdit()
                e.setFixedWidth(60)
                self.layoutCentral.addWidget(e, i, j)
                fila_inputs.append(e)
            self.matriz_inputs.append(fila_inputs)
        self.texto.clear()

    def resolverMatriz(self):
        try:
            matriz = []
            for fila in self.matriz_inputs:
                matriz.append([float(e.text()) for e in fila])
            texto = f"Método seleccionado: Gauss-Jordan\n"
            resultado, info = self.gauss_jordan(matriz)
            texto += info
            texto += "\nMatriz final:\n"
            for fila in resultado:
                texto += str([round(x, 3) for x in fila]) + "\n"
            self.texto.setText(texto)
            self.grafico.axes.clear()
            self.grafico.draw()
        except Exception:
            self.texto.setText("Error al leer la matriz.")

    def gauss_jordan(self, matriz):
        A = [row[:] for row in matriz]
        filas = len(A)
        cols = len(A[0])
        info = ""
        for i in range(filas):
            max_row = max(range(i, filas), key=lambda r: abs(A[r][i]))
            if abs(A[max_row][i]) < 1e-12:
                continue
            if max_row != i:
                A[i], A[max_row] = A[max_row], A[i]
                info += f"Intercambio fila {i+1} con fila {max_row+1}\n"
                info += self.matriz_a_texto(A)
            pivote = A[i][i]
            if abs(pivote) > 1e-12:
                for k in range(i, cols):
                    A[i][k] /= pivote
                info += f"F{i+1} = F{i+1} / {pivote:.2f}\n"
                info += self.matriz_a_texto(A)
                for j in range(filas):
                    if j != i:
                        factor = A[j][i]
                        for k in range(i, cols):
                            A[j][k] -= factor * A[i][k]
                        info += f"F{j+1} = F{j+1} - ({factor:.2f})*F{i+1}\n"
                        info += self.matriz_a_texto(A)
        info += self.analisis_sistema(A)
        return A, info

    def matriz_a_texto(self, A):
        texto = ""
        for fila in A:
            texto += str([round(x, 3) for x in fila]) + "\n"
        texto += "\n"
        return texto

    def analisis_sistema(self, A):
        filas = len(A)
        cols = len(A[0])
        info = ""
        rango_coef = 0
        rango_ext = 0
        for fila in A:
            if any(abs(x) > 1e-12 for x in fila[:-1]):
                rango_coef += 1
            if any(abs(x) > 1e-12 for x in fila):
                rango_ext += 1
        n_vars = cols - 1
        if rango_coef < rango_ext:
            info += "\nSistema inconsistente (sin solución).\n"
        elif rango_coef < n_vars:
            info += "\nSistema compatible indeterminado (variables libres).\n"
        else:
            info += "\nSistema compatible determinado (solución única).\n"
        return info
# Example usage:
# gui = guiManager(entradaFilas, entradaColumnas, layoutCentral, botonResolver  , texto, grafico), texto, grafico)
# gui.crearMatriz()