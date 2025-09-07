from fractions import Fraction

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

        if filas < 1 or filas > 25 or columnas < 1 or columnas > 25:
            self.texto.setPlainText("El número máximo es 25x25 y mínimo 1x1.")
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
        # Solo muestra el botón si todo está lleno
        for fila in self.matrizWidgets:
            for celda in fila:
                val = celda.text().strip()
                if val == "":
                    self.botonResolver.hide()
                    return
        self.texto.setPlainText("Matriz lista. Puedes resolver y graficar.")
        self.botonResolver.show()

    def gauss_jordan_pasos(self, A, b):
        def matriz_str(mat):
            col_widths = [max(len(f"{float(fila[j]):.4f}") for fila in mat) for j in range(len(mat[0]))]
            lines = []
            for fila in mat:
                fila_str = " | ".join(f"{float(v):.4f}".rjust(col_widths[j]) for j, v in enumerate(fila))
                lines.append(fila_str)
            return "\n".join(lines)

        def nombre_incognita(idx):
            subindices = "₁₂₃₄₅₆₇₈₉"
            return f"x{subindices[idx] if idx < len(subindices) else str(idx+1)}"

        filas = len(A)
        columnas = len(A[0]) if A else 0
        n = min(filas, columnas)
        aug = [list(map(float, row)) + [float(b[i])] for i, row in enumerate(A)]

        pasos = []
        pasos.append("--- Matriz aumentada inicial ---\n" + matriz_str(aug) + "\n")
        pasos.append("--- Eliminación hacia adelante ---\n")

        # Eliminación hacia adelante
        for i in range(n):
            # Pivoteo parcial
            max_row = max(range(i, filas), key=lambda r: abs(aug[r][i]))
            if abs(aug[max_row][i]) < 1e-12:
                pasos.append(f"No se puede continuar, pivote nulo en columna {i+1}. El sistema puede ser singular o tener infinitas soluciones.\n")
                return "\n".join(pasos), None
            if max_row != i:
                pasos.append(f"f{i+1} <--> f{max_row+1}\n{matriz_str(aug)}\n")
                aug[i], aug[max_row] = aug[max_row], aug[i]
            pivot = aug[i][i]
            if abs(pivot - 1.0) > 1e-12:
                pasos.append(f"f{i+1} --> (1/{pivot:.4f})*f{i+1}\n")
                aug[i] = [x / pivot for x in aug[i]]
                pasos.append(matriz_str(aug) + "\n")
            for j in range(i+1, filas):
                factor = aug[j][i]
                if abs(factor) > 1e-12:
                    pasos.append(f"f{j+1} --> f{j+1} + ({-factor:.4f})*f{i+1}\n")
                    aug[j] = [aug[j][k] - factor * aug[i][k] for k in range(columnas+1)]
                    pasos.append(matriz_str(aug) + "\n")

        pasos.append("--- Sustitución hacia atrás ---\n")
        x = [0.0] * columnas
        for i in range(n-1, -1, -1):
            suma = sum(aug[i][j] * x[j] for j in range(i+1, columnas))
            x[i] = aug[i][columnas] - suma
            incog = nombre_incognita(i)
            sum_str = " + ".join(f"({aug[i][j]:.4f}*{nombre_incognita(j)})" for j in range(i+1, columnas))
            pasos.append(f"{incog} = {aug[i][columnas]:.4f} - [{sum_str if sum_str else '0'}] = {x[i]:.4f}\n")

        pasos.append("--- Matriz final escalonada ---\n" + matriz_str(aug) + "\n")
        pasos.append("--- Solución final ---")
        for i in range(n):
            pasos.append(f"{nombre_incognita(i)} = {x[i]:.4f}")

        # Detectar pivotes y variables básicas/libres
        pivotes = []
        variables_basicas = []
        variables_libres = []
        for j in range(columnas):
            es_pivote = False
            for i in range(filas):
                fila = aug[i]
                if abs(fila[j] - 1.0) < 1e-8 and all(abs(fila[k]) < 1e-8 for k in range(j)) and all(abs(fila[k]) < 1e-8 for k in range(j+1, columnas)):
                    es_pivote = True
                    break
            if es_pivote:
                pivotes.append(j)
                variables_basicas.append(f"x{j+1}")
            else:
                variables_libres.append(f"x{j+1}")

        pasos.append(f"Pivotes en columnas: {', '.join(str(p+1) for p in pivotes)}")
        pasos.append(f"Variables básicas: {', '.join(variables_basicas) if variables_basicas else 'Ninguna'}")
        pasos.append(f"Variables libres: {', '.join(variables_libres) if variables_libres else 'Ninguna'}")

        return "\n".join(pasos), x[:filas] if filas == columnas else None

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
                    fila.append(Fraction(val))
                A.append(fila)
                b_val = self.matrizWidgets[i][columnas].text()
                if b_val.strip() == "":
                    raise ValueError(f"Celda vacía en término independiente de fila {i+1}")
                b.append(Fraction(b_val))
        except Exception as e:
            self.texto.setPlainText(f"Error en la entrada de datos: {e}")
            return

        # Resolver sistema mostrando pasos
        try:
            pasos, sol = self.gauss_jordan_pasos(A, b)
            self.texto.setPlainText(pasos)
            if sol is not None:
                self._graficar(A, b, sol)
        except Exception as e:
            self.texto.setPlainText(f"Error al resolver el sistema: {e}")

    def _graficar(self, A, b, sol):
        """Dibuja los ejes, las rectas de cada ecuación y la solución si existe (sin numpy ni scipy)"""
        self.grafico.axes.clear()
        self.grafico.axes.axhline(0, color='black', linewidth=1.5)
        self.grafico.axes.axvline(0, color='black', linewidth=1.5)
        self.grafico.axes.set_xlim(-10, 10)
        self.grafico.axes.set_ylim(-10, 10)
        self.grafico.axes.grid(True, which='both', color='gray', linestyle='--', linewidth=0.5, alpha=0.7)

        filas = len(A)
        cols = len(A[0])
        colores = ["b", "g", "m", "c", "y", "k", "orange", "purple", "brown", "pink"]

        # Dibuja las rectas de cada ecuación (solo para sistemas de 2 variables)
        if cols == 2:
            x_vals = [x/20.0*20 for x in range(-200, 201)]  # de -10 a 10 en pasos de 0.1
            for i in range(filas):
                a, b_coef = float(A[i][0]), float(A[i][1])
                if abs(b_coef) > 1e-12:
                    y_vals = [ (float(b[i]) - a*x)/b_coef for x in x_vals ]
                    self.grafico.axes.plot(x_vals, y_vals, color=colores[i % len(colores)], label=f"Ecuación {i+1}", linewidth=2)
        # Para sistemas de 3 variables, dibuja proyección en XY (z=0)
        elif cols == 3:
            x_vals = [x/20.0*20 for x in range(-200, 201)]
            for i in range(filas):
                a, b_coef, c = float(A[i][0]), float(A[i][1]), float(A[i][2])
                if abs(b_coef) > 1e-12:
                    y_vals = [ (float(b[i]) - a*x - c*0)/b_coef for x in x_vals ]
                    self.grafico.axes.plot(x_vals, y_vals, color=colores[i % len(colores)], label=f"Ecuación {i+1}", linewidth=2)

        # Dibuja el punto de solución si existe
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