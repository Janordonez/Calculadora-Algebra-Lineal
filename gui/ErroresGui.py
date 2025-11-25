# gui/ErroresGui.py
import math

from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLineEdit, QTextEdit, QTabWidget, QTableWidget, QTableWidgetItem,
    QDoubleSpinBox, QMessageBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt


class ErroresGui(QWidget):
    """
    Interfaz gráfica para:
      - Notación posicional (base 10 y base 2)
      - Ejemplo de punto flotante (a + b == c, editable; default 0.1,0.2,0.3)
      - Cálculo de error absoluto y relativo usando f(x)=sin(x)+x^2
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Errores Numéricos")
        self.resize(960, 640)

        self.setStyleSheet("""
            QWidget {
                background-color: #020617;
                color: #e5e7eb;
                font-family: 'Segoe UI', 'Inter', 'Arial';
                font-size: 14px;
            }
            QLineEdit, QDoubleSpinBox, QTextEdit {
                background-color: #020617;
                border: 1px solid #1f2933;
                border-radius: 6px;
                padding: 4px 6px;
                color: #e5e7eb;
            }
            QTabWidget::pane {
                border: 1px solid #1f2933;
                border-radius: 8px;
            }
            QTabBar::tab {
                background: #020617;
                padding: 8px 18px;
                border: 1px solid #1f2933;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #0f172a;
                color: #f9fafb;
            }
            QPushButton {
                background-color: #325475;
                color: #ffffff;
                border-radius: 18px;
                border: 1px solid #325475;
                padding: 8px 22px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #3b6b9a;
            }
            QTableWidget {
                background-color: #020617;
                gridline-color: #1f2933;
                border: 1px solid #1f2933;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(16)

        titulo = QLabel("Módulo de Errores Numéricos", self)
        titulo.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        titulo.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        main_layout.addWidget(titulo)

        # Tabs
        self.tabs = QTabWidget(self)
        main_layout.addWidget(self.tabs)

        # --- Tab 1: Notación posicional ---
        self._crear_tab_notacion()

        # --- Tab 2: Punto flotante / explicación ---
        self._crear_tab_flotante()

        # --- Tab 3: Errores y propagación ---
        self._crear_tab_errores()

        # Botón inferior para volver al menú
        bottom = QHBoxLayout()
        bottom.addStretch()
        self.btn_regresar = QPushButton("Volver al menú", self)
        self.btn_regresar.clicked.connect(self.volver_menu)
        bottom.addWidget(self.btn_regresar)
        main_layout.addLayout(bottom)

    # ======================================================
    # TAB 1: NOTACIÓN POSICIONAL
    # ======================================================
    def _crear_tab_notacion(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)

        desc = QLabel(
            "Descomposición posicional en base 10 y base 2.\n"
            "Ejemplo teórico: 84506 = 8·10⁴ + 4·10³ + 5·10² + 0·10¹ + 6·10⁰\n"
            "                1111001₂ = 1·2⁶ + 1·2⁵ + 1·2⁴ + 1·2³ + 0·2² + 0·2¹ + 1·2⁰",
            tab
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)

        # Entrada para base 10
        grid.addWidget(QLabel("Número en base 10:"), 0, 0)
        self.txt_base10 = QLineEdit()
        self.txt_base10.setPlaceholderText("Ej: 84506")
        grid.addWidget(self.txt_base10, 0, 1)

        btn_des10 = QPushButton("Descomponer base 10")
        btn_des10.clicked.connect(self.descomponer_base10)
        grid.addWidget(btn_des10, 0, 2)

        # Entrada para base 2
        grid.addWidget(QLabel("Número en base 2:"), 1, 0)
        self.txt_base2 = QLineEdit()
        self.txt_base2.setPlaceholderText("Ej: 1111001")
        grid.addWidget(self.txt_base2, 1, 1)

        btn_des2 = QPushButton("Descomponer base 2")
        btn_des2.clicked.connect(self.descomponer_base2)
        grid.addWidget(btn_des2, 1, 2)

        layout.addLayout(grid)

        self.txt_salida_notacion = QTextEdit()
        self.txt_salida_notacion.setReadOnly(True)
        layout.addWidget(self.txt_salida_notacion)

        self.tabs.addTab(tab, "Notación posicional")

    def descomponer_base10(self):
        texto = self.txt_base10.text().strip()
        if not texto:
            QMessageBox.warning(self, "Aviso", "Escribe un número entero en base 10.")
            return
        try:
            numero = int(texto)
        except ValueError:
            QMessageBox.warning(self, "Aviso", "El valor debe ser un entero (sin decimales).")
            return

        signo = -1 if numero < 0 else 1
        num_abs = abs(numero)
        cad = str(num_abs)
        n = len(cad)

        lineas = [f"Descomposición de {numero} en base 10:"]
        terminos = []
        for i, ch in enumerate(cad):
            d = int(ch)
            pos = n - i - 1
            pot = 10 ** pos
            term = d * pot
            terminos.append(term)
            lineas.append(f"{d} × 10^{pos} = {term}")
        suma = sum(terminos) * signo

        expr = " + ".join(f"{cad[i]}×10^{n-i-1}" for i in range(n))
        if signo < 0:
            expr = "-(" + expr + ")"

        lineas.append("")
        lineas.append(f"Forma desarrollada: {expr}")
        lineas.append(f"Suma final: {suma}")

        self.txt_salida_notacion.setPlainText("\n".join(lineas))

    def descomponer_base2(self):
        texto = self.txt_base2.text().strip()
        if not texto:
            QMessageBox.warning(self, "Aviso", "Escribe un número en binario (solo 0 y 1).")
            return
        if any(c not in "01" for c in texto):
            QMessageBox.warning(self, "Aviso", "La base 2 solo permite dígitos 0 y 1.")
            return

        binario = texto
        n = len(binario)
        lineas = [f"Descomposición de {binario} en base 2:"]
        terminos = []
        for i, ch in enumerate(binario):
            bit = int(ch)
            pos = n - i - 1
            pot = 2 ** pos
            term = bit * pot
            terminos.append(term)
            lineas.append(f"{bit} · 2^{pos} = {term}")
        suma = sum(terminos)
        expr = " + ".join(f"{binario[i]}·2^{n-i-1}" for i in range(n))

        lineas.append("")
        lineas.append(f"Forma desarrollada: {expr}")
        lineas.append(f"Suma final en decimal: {suma}")

        self.txt_salida_notacion.setPlainText("\n".join(lineas))

    # ======================================================
    # TAB 2: PUNTO FLOTANTE (MEJORADA)
    # ======================================================
    def _crear_tab_flotante(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)

        desc = QLabel(
            "Ejemplo de error de representación en punto flotante.\n"
            "Por defecto se usa a = 0.1, b = 0.2 y c = 0.3 (ejemplo obligatorio),\n"
            "pero puedes cambiar los valores y ver qué ocurre con a + b == c.",
            tab
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(6)

        grid.addWidget(QLabel("a:"), 0, 0)
        self.spn_a = QDoubleSpinBox()
        self.spn_a.setRange(-1e9, 1e9)
        self.spn_a.setDecimals(15)
        self.spn_a.setValue(0.1)    # valor obligatorio por defecto
        grid.addWidget(self.spn_a, 0, 1)

        grid.addWidget(QLabel("b:"), 1, 0)
        self.spn_b = QDoubleSpinBox()
        self.spn_b.setRange(-1e9, 1e9)
        self.spn_b.setDecimals(15)
        self.spn_b.setValue(0.2)    # valor obligatorio por defecto
        grid.addWidget(self.spn_b, 1, 1)

        grid.addWidget(QLabel("c (comparación):"), 2, 0)
        self.spn_c = QDoubleSpinBox()
        self.spn_c.setRange(-1e9, 1e9)
        self.spn_c.setDecimals(15)
        self.spn_c.setValue(0.3)    # valor obligatorio por defecto
        grid.addWidget(self.spn_c, 2, 1)

        self.btn_eval_float = QPushButton("Evaluar a + b == c", tab)
        self.btn_eval_float.clicked.connect(self.evaluar_flotante)
        grid.addWidget(self.btn_eval_float, 0, 2, 3, 1)

        layout.addLayout(grid)

        self.txt_flotante = QTextEdit(tab)
        self.txt_flotante.setReadOnly(True)
        layout.addWidget(self.txt_flotante)

        self.tabs.addTab(tab, "Punto flotante")

    def evaluar_flotante(self):
        a = float(self.spn_a.value())
        b = float(self.spn_b.value())
        c = float(self.spn_c.value())

        suma = a + b
        resultado = (suma == c)

        lineas = []
        lineas.append("Evaluando: a + b == c")
        lineas.append(f"a = {a:.17f}")
        lineas.append(f"b = {b:.17f}")
        lineas.append(f"c = {c:.17f}")
        lineas.append("")
        lineas.append(f"a + b = {suma:.17f}")
        lineas.append(f"¿a + b == c?  ->  {resultado}")
        lineas.append("")
        lineas.append(
            "En aritmética de punto flotante los números se representan en base 2\n"
            "con una cantidad finita de bits. Muchos decimales (como 0.1 o 0.2)\n"
            "no se pueden representar exactamente, solo aproximar.\n"
            "Al operar con ellos, los pequeños errores de representación se\n"
            "acumulan y hacen que comparaciones aparentemente 'obvias' como\n"
            "0.1 + 0.2 == 0.3 resulten False."
        )

        self.txt_flotante.setPlainText("\n".join(lineas))

    # ======================================================
    # TAB 3: ERRORES Y PROPAGACIÓN
    # ======================================================
    def _crear_tab_errores(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)

        desc = QLabel(
            "Cálculo de error absoluto y error relativo\n"
            "para la función f(x) = sin(x) + x². Ingresa el valor verdadero (x_v)\n"
            "y el valor aproximado (x_a).",
            tab
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)

        grid.addWidget(QLabel("Valor verdadero (x_v):"), 0, 0)
        self.spn_xv = QDoubleSpinBox()
        self.spn_xv.setDecimals(10)
        self.spn_xv.setRange(-1e9, 1e9)
        grid.addWidget(self.spn_xv, 0, 1)

        grid.addWidget(QLabel("Valor aproximado (x_a):"), 1, 0)
        self.spn_xa = QDoubleSpinBox()
        self.spn_xa.setDecimals(10)
        self.spn_xa.setRange(-1e9, 1e9)
        grid.addWidget(self.spn_xa, 1, 1)

        self.btn_calcular = QPushButton("Calcular errores", tab)
        self.btn_calcular.clicked.connect(self.calcular_errores)
        grid.addWidget(self.btn_calcular, 0, 2, 2, 1)

        layout.addLayout(grid)

        # ----- Bloque de resultados dividido verticalmente -----
        resultados_layout = QHBoxLayout()
        resultados_layout.setSpacing(12)

        # Tabla (lado izquierdo)
        self.tabla = QTableWidget(0, 2, tab)
        self.tabla.setHorizontalHeaderLabels(["Magnitud", "Valor"])
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setMinimumWidth(380)
        resultados_layout.addWidget(self.tabla, 1)

        # Paso a paso (lado derecho)
        self.txt_pasos = QTextEdit(tab)
        self.txt_pasos.setReadOnly(True)
        resultados_layout.addWidget(self.txt_pasos, 1)

        layout.addLayout(resultados_layout)

        # Interpretación general
        self.lbl_interpretacion = QLabel("", tab)
        self.lbl_interpretacion.setWordWrap(True)
        layout.addWidget(self.lbl_interpretacion)

        self.tabs.addTab(tab, "Errores y propagación")

    def f(self, x: float) -> float:
        return math.sin(x) + x**2

    def f_derivada(self, x: float) -> float:
        return math.cos(x) + 2*x

    def calcular_errores(self):
        x_v = float(self.spn_xv.value())
        x_a = float(self.spn_xa.value())

        # Errores en x
        error_abs_x = abs(x_v - x_a)
        error_rel_x = error_abs_x / abs(x_v) if x_v != 0 else float("inf")

        # Evaluación de la función
        f_v = self.f(x_v)
        f_a = self.f(x_a)

        # ---------- Tabla: solo filas 1 a 6 ----------
        datos = [
            ("x verdadero (x_v)", f"{x_v:.10f}"),
            ("x aproximado (x_a)", f"{x_a:.10f}"),
            ("Error absoluto en x (E_a)", f"{error_abs_x:.10e}"),
            ("Error relativo en x (E_r)", f"{error_rel_x:.10e}"),
            ("f(x_v)", f"{f_v:.10f}"),
            ("f(x_a)", f"{f_a:.10f}"),
        ]

        self.tabla.setRowCount(len(datos))
        for i, (nombre, valor) in enumerate(datos):
            self.tabla.setItem(i, 0, QTableWidgetItem(nombre))
            self.tabla.setItem(i, 1, QTableWidgetItem(valor))

        porcentaje_rel_x = error_rel_x * 100 if math.isfinite(error_rel_x) else float("inf")

        # ---------- Paso a paso con nombres claros ----------
        pasos = []
        pasos.append("1) Definición de los valores de referencia")
        pasos.append(f"   x_v  = {x_v:.10f}   (valor verdadero)")
        pasos.append(f"   x_a  = {x_a:.10f}   (valor aproximado)")
        pasos.append("")
        pasos.append("2) Cálculo del error absoluto en x")
        pasos.append(
            "   Restamos el valor aproximado al valor verdadero:\n"
            f"      x_v - x_a = {x_v:.10f} - {x_a:.10f}"
        )
        pasos.append(
            "   Luego tomamos el valor absoluto de esa diferencia:\n"
            f"      E_a = |x_v - x_a| = |{x_v:.10f} - {x_a:.10f}| = {error_abs_x:.10e}"
        )
        pasos.append("")
        pasos.append("3) Cálculo del error relativo en x")
        if math.isfinite(error_rel_x):
            pasos.append(
                "   Dividimos el error absoluto entre el valor verdadero en magnitud:\n"
                f"      E_r = E_a / |x_v| = {error_abs_x:.10e} / |{x_v:.10f}| = {error_rel_x:.10e}\n"
                f"   Esto equivale aproximadamente a {porcentaje_rel_x:.4f} % de error relativo."
            )
        else:
            pasos.append(
                "   Como x_v = 0, no se puede dividir entre |x_v| para obtener el error relativo.\n"
                "   En este caso se dice que el error relativo tiende a infinito (no está definido)."
            )

        pasos.append("")
        pasos.append("4) Evaluación de la función f(x) = sin(x) + x²")
        pasos.append(
            "   Primero evaluamos la función en el valor verdadero x_v:\n"
            f"      f(x_v) = sin(x_v) + x_v² = sin({x_v:.10f}) + ({x_v:.10f})² = {f_v:.10f}"
        )
        pasos.append(
            "   Luego evaluamos la misma función en el valor aproximado x_a:\n"
            f"      f(x_a) = sin(x_a) + x_a² = sin({x_a:.10f}) + ({x_a:.10f})² = {f_a:.10f}"
        )
        pasos.append("")
        pasos.append(
            "   Si f(x_a) está muy cerca de f(x_v), significa que el error en x no se ha amplificado "
            "demasiado al pasar por la función. Si están muy separados, la función es sensible a "
            "los cambios en x (propagación del error)."
        )

        self.txt_pasos.setPlainText("\n".join(pasos))

        # ---------- Interpretación general (solo en términos de x y valores de f) ----------
        texto = (
            f"El error relativo en x es aproximadamente {porcentaje_rel_x:.4f} %. "
            "Este porcentaje indica qué tan grande es la diferencia entre el valor aproximado "
            "x_a y el valor verdadero x_v, comparada con el propio valor verdadero. "
            "Al comparar f(x_v) y f(x_a) puedes observar visualmente si la función "
            "f(x) = sin(x) + x² amplifica o no el error que había originalmente en x."
        )
        self.lbl_interpretacion.setText(texto)

    # ======================================================
    # Volver al menú
    # ======================================================
    def volver_menu(self):
        """Cierra esta ventana y vuelve al menú principal."""
        try:
            from gui.MenuGui import MenuGui
            self.menu = MenuGui()
            self.menu.show()
        except Exception:
            # Si falla el import, simplemente cerramos esta ventana.
            pass
        self.close()


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    w = ErroresGui()
    w.show()
    sys.exit(app.exec())
