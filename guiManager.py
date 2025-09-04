from fractions import Fraction
from matriz import gauss_elimination

class guiManager:
    def __init__(self, entradaFilas, entradaColumnas, layoutCentral, botonResolver, texto, grafico):
        self.entradaFilas = entradaFilas
        self.entradaColumnas = entradaColumnas
        self.layoutCentral = layoutCentral
        self.botonResolver = botonResolver
        self.texto = texto
        self.grafico = grafico
        self.matrizWidgets = []

    def crearMatriz(self):
        # Limpia la matriz anterior
        for widgetsFila in self.matrizWidgets:
            for widget in widgetsFila:
                widget.deleteLater()
        self.matrizWidgets = []

        # Limpia el gráfico
        self.grafico.axes.clear()
        self.grafico.draw()

        # Oculta el botón de resolver
        self.botonResolver.hide()

        try:
            filas = int(self.entradaFilas.text())
            columnas = int(self.entradaColumnas.text())
        except ValueError:
            self.texto.setPlainText("Por favor, ingresa números válidos para filas y columnas.")
            return

        if filas < 1 or filas > 10 or columnas < 1 or columnas > 10:
            self.texto.setPlainText("El número máximo es 10x10 y mínimo 1x1.")
            return

        # Si todo está bien, crea la matriz
        for i in range(filas):
            filaWidgets = []
            for j in range(columnas + 1): 
                from PyQt5.QtWidgets import QLineEdit
                celda = QLineEdit()
                celda.setPlaceholderText(f"A{i+1},{j+1}" if j < columnas else f"b{i+1}")
                self.layoutCentral.addWidget(celda, i, j)
                filaWidgets.append(celda)
            self.matrizWidgets.append(filaWidgets)
        self.texto.setPlainText("Matriz generada. Ingresa los valores (no puede haber vacíos ni ceros en la matriz).")

        # Conecta para mostrar el botón solo si todo está lleno y válido
        for fila in self.matrizWidgets:
            for celda in fila:
                celda.textChanged.connect(self._verificar_matriz_llena)

    def _verificar_matriz_llena(self):
        # Solo muestra el botón si todo está lleno y válido
        for i, fila in enumerate(self.matrizWidgets):
            for j, celda in enumerate(fila):
                val = celda.text().strip()
                if val == "":
                    self.botonResolver.hide()
                    return
                if j < len(fila) - 1:  # Solo para la matriz, no el término independiente
                    try:
                        if Fraction(val) == 0:
                            self.texto.setPlainText(f"No se permite 0 en la matriz (error en fila {i+1}, columna {j+1}).")
                            self.botonResolver.hide()
                            return
                    except Exception:
                        self.texto.setPlainText(f"Valor inválido en fila {i+1}, columna {j+1}.")
                        self.botonResolver.hide()
                        return
        self.texto.setPlainText("Matriz lista. Puedes resolver y graficar.")
        self.botonResolver.show()

    def resolverMatriz(self):
        if not self.matrizWidgets:
            self.texto.setPlainText("Primero genera la matriz.")
            return

        filas = len(self.matrizWidgets)
        columnas = len(self.matrizWidgets[0]) - 1  # última columna es b

        A = []
        b = []
        try:
            for i in range(filas):
                fila = []
                for j in range(columnas):
                    val = self.matrizWidgets[i][j].text()
                    if val.strip() == "":
                        raise ValueError(f"Celda vacía en fila {i+1}, columna {j+1}")
                    if Fraction(val) == 0:
                        raise ValueError(f"No se permite 0 en la matriz (error en fila {i+1}, columna {j+1})")
                    fila.append(Fraction(val))
                A.append(fila)
                b_val = self.matrizWidgets[i][columnas].text()
                if b_val.strip() == "":
                    raise ValueError(f"Celda vacía en término independiente de fila {i+1}")
                b.append(Fraction(b_val))
        except Exception as e:
            self.texto.setPlainText(f"Error en la entrada de datos: {e}")
            return

        # Resolver sistema
        try:
            import io
            import contextlib
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                sol = gauss_elimination(A, b)
            resultado = buffer.getvalue()
            self.texto.setPlainText(resultado)
            if sol is not None:
                self._graficar(A, b, sol)
        except Exception as e:
            self.texto.setPlainText(f"Error al resolver el sistema: {e}")

    def _graficar(self, A, b, sol):
        """Dibuja la proyección XY de los planos del sistema"""
        import numpy as np

        self.grafico.axes.clear()
        filas = len(A)
        cols = len(A[0])

        x = np.linspace(-10, 10, 400)

        colores = ["b", "g", "m", "c", "y", "k"]
        for i in range(filas):
            # Proyección en XY: z=0 si hay al menos 2 columnas
            if cols >= 2 and A[i][1] != 0:
                y = (float(b[i]) - float(A[i][0])*x - (float(A[i][2])*0 if cols > 2 else 0)) / float(A[i][1])
                self.grafico.axes.plot(x, y, color=colores[i % len(colores)], label=f"Ecuación {i+1}", linewidth=2)
                idx = -1 if y[-1] < y[0] else 0
                self.grafico.axes.annotate(
                    '', xy=(x[idx], y[idx]), xytext=(x[idx-20], y[idx-20]),
                    arrowprops=dict(facecolor=colores[i % len(colores)], arrowstyle='->', lw=2)
                )
        self.grafico.axes.axhline(0, color='black', linewidth=1.5)
        self.grafico.axes.axvline(0, color='black', linewidth=1.5)
        self.grafico.axes.set_xticks(np.arange(-10, 11, 1))
        self.grafico.axes.set_yticks(np.arange(-10, 11, 1))
        self.grafico.axes.grid(True, which='both', color='gray', linestyle='--', linewidth=0.5, alpha=0.7)
        self.grafico.axes.set_xlim(-10, 10)
        self.grafico.axes.set_ylim(-10, 10)
        if sol is not None and len(sol) >= 2:
            self.grafico.axes.plot(float(sol[0]), float(sol[1]), "ro", markersize=8, label="Solución (proyección XY)")
            self.grafico.axes.annotate(
                f"({float(sol[0]):.2f}, {float(sol[1]):.2f})",
                (float(sol[0]), float(sol[1])),
                textcoords="offset points", xytext=(10,10), ha='left', color='blue', fontsize=12
            )
        self.grafico.axes.set_title("Proyección en plano XY (z=0)")
        self.grafico.axes.legend()
        self.grafico.axes.set_aspect('equal', adjustable='box')
        self.grafico.draw()