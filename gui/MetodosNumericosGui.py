# gui/MetodosNumericosGui.py

from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QTextEdit,
    QVBoxLayout, QHBoxLayout, QGridLayout, QMessageBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from models.logica_metodos_numericos import (
    evaluar_funcion,
    biseccion,
    regla_falsa,
    newton_raphson,
    metodo_secante,
    normalizar_expresion_usuario,
    contexto_matematico,
)

import re

# =============================================================================
# PARSER PARA CAMPOS NUMÉRICOS (permite π, etc.)
# =============================================================================

def numero_desde_texto(txt: str) -> float:
    """
    Convierte un texto como '3', 'pi/2', '2π', '1e-3', etc., en float.
    Usa el mismo normalizador y contexto que f(x).
    """
    s = txt.strip()
    if not s:
        raise ValueError("Campo numérico vacío.")
    expr_norm = normalizar_expresion_usuario(s)
    ctx = contexto_matematico()
    try:
        val = eval(expr_norm, {"__builtins__": {}}, ctx)
        return float(val)
    except Exception as e:
        raise ValueError(f"Valor incorrecto: {txt}") from e


# =============================================================================
# CAMPO MATEMÁTICO (superíndices, atajos, etc.)
# =============================================================================

SUP_DIGITS = "⁰¹²³⁴⁵⁶⁷⁸⁹"
NORMAL_DIGITS = "0123456789"
DIGIT_TO_SUP = str.maketrans(NORMAL_DIGITS + "-", SUP_DIGITS + "⁻")


class CampoMatematico(QLineEdit):
    """
    QLineEdit que soporta:
    - ↑ dos veces: modo superíndice (², ³, ⁻¹, etc.)
    - Ctrl+R: √()
    - Ctrl+3: ∛()
    - Ctrl+L: ln()
    - Ctrl+S: sen()
    - Ctrl+P: π
    """
    def __init__(self):
        super().__init__()
        self._ultima_flecha = False
        self._modo_superindice = False

    def keyPressEvent(self, e):
        key = e.key()
        txt = e.text()
        mods = e.modifiers()

        # Doble flecha arriba -> modo superíndice
        if key == Qt.Key.Key_Up:
            if self._ultima_flecha:
                self._modo_superindice = True
                self._ultima_flecha = False
                return
            self._ultima_flecha = True
            super().keyPressEvent(e)
            return
        self._ultima_flecha = False

        if self._modo_superindice:
            if txt.isdigit():
                self.insert(txt.translate(DIGIT_TO_SUP))
                return
            if txt == "-" or key == Qt.Key.Key_Minus:
                self.insert("⁻")
                return
            if key in (
                Qt.Key.Key_Down,
                Qt.Key.Key_Space,
                Qt.Key.Key_Right,
                Qt.Key.Key_Plus,
            ):
                self._modo_superindice = False
                if key == Qt.Key.Key_Down:
                    return
            elif key == Qt.Key.Key_Backspace:
                pass
            else:
                self._modo_superindice = False

        # Tecla ^ -> ² rápido
        if key == Qt.Key.Key_AsciiCircum:
            self.insert("²")
            return

        # Atajos Ctrl + ...
        if mods == Qt.KeyboardModifier.ControlModifier:
            if key == Qt.Key.Key_R:
                self.insert("√()")
                self.setCursorPosition(self.cursorPosition() - 1)
                return
            if key == Qt.Key.Key_3:
                self.insert("∛()")
                self.setCursorPosition(self.cursorPosition() - 1)
                return
            if key == Qt.Key.Key_L:
                self.insert("ln()")
                self.setCursorPosition(self.cursorPosition() - 1)
                return
            if key == Qt.Key.Key_S:
                self.insert("sen()")
                self.setCursorPosition(self.cursorPosition() - 1)
                return
            if key == Qt.Key.Key_P:
                self.insert("π")
                return

        super().keyPressEvent(e)


# =============================================================================
# WIDGET DE GRÁFICA
# =============================================================================

class GraficaWidget(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(4, 3))
        super().__init__(self.fig)
        self.setParent(parent)
        self.ax = self.fig.add_subplot(111)
        self._estilizar()

    def _estilizar(self):
        self.fig.patch.set_facecolor("#020617")
        self.ax.set_facecolor("#020617")
        for spine in self.ax.spines.values():
            spine.set_color("#e5e7eb")
        self.ax.tick_params(colors="#e5e7eb")
        self.ax.grid(True, color="#334155", alpha=0.5)
        self.ax.set_xlabel("x", color="#e5e7eb")
        self.ax.set_ylabel("f(x)", color="#e5e7eb")

    def limpiar(self):
        self.fig.clear()
        self.ax = self.fig.add_subplot(111)
        self._estilizar()
        self.draw()

    def dibujar_funcion_y_raiz(self, expr: str, x_min: float, x_max: float,
                               raiz, evaluar_funcion_callable):
        self.limpiar()

        if x_min == x_max:
            x_min -= 1.0
            x_max += 1.0
        if x_min > x_max:
            x_min, x_max = x_max, x_min

        xs = np.linspace(x_min, x_max, 400)
        ys = []
        for x in xs:
            try:
                y = evaluar_funcion_callable(expr, float(x))
                ys.append(y if np.isfinite(y) else np.nan)
            except Exception:
                ys.append(np.nan)

        ys = np.array(ys)
        self.ax.plot(xs, ys, label="f(x)")
        self.ax.axhline(0, linestyle="--", linewidth=1, label="Eje x")

        if raiz is not None:
            try:
                y_r = evaluar_funcion_callable(expr, float(raiz))
                if np.isfinite(y_r):
                    self.ax.scatter([raiz], [y_r], s=40, zorder=5, label="Raíz aprox.")
            except Exception:
                pass

        self.ax.legend(facecolor="#020617", edgecolor="#334155", labelcolor="#e5e7eb")
        self.draw()


# =============================================================================
# VENTANA PRINCIPAL
# =============================================================================

class MetodosNumericosGui(QWidget):
    """
    Ventana para Bisección, Regla Falsa, Newton-Raphson y Secante.

    - B / RF: usan intervalo [a, b] que debe encerrar la raíz.
    - N     : método de Newton-Raphson (abierto), SOLO x0 (punto inicial).
    - S     : método de la Secante (abierto), x0 y x1 (dos aproximaciones).
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Métodos Numéricos - Cerrados y Abiertos")
        self.resize(1150, 720)

        self._configurar_estilos()
        self._crear_ui()

    def _configurar_estilos(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #020617;
                color: #e5e7eb;
                font-family: 'Segoe UI', 'Inter', 'Arial';
            }
            QLabel {
                font-size: 14px;
            }
            QLineEdit {
                background-color: #020617;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 14px;
            }
            QTextEdit {
                background-color: #020617;
                border: 1px solid #334155;
                border-radius: 6px;
                font-family: 'Consolas', 'Fira Code', monospace;
                font-size: 13px;
            }
            QPushButton {
                background-color: #325475;
                color: #ffffff;
                border-radius: 18px;
                border: 1px solid #325475;
                padding: 8px 20px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #3b6b9a;
                border: 1px solid #4a89c7;
            }
            QPushButton:pressed {
                background-color: #1e293b;
            }
        """)

    def _crear_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(10)

        # Título
        lbl_titulo = QLabel("Métodos Numéricos: Bisección, Regla Falsa, Newton-Raphson y Secante")
        f_titulo = QFont("Segoe UI", 18, QFont.Weight.Bold)
        lbl_titulo.setFont(f_titulo)
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(lbl_titulo)

        # Panel superior de parámetros
        panel = QWidget(self)
        grid = QGridLayout(panel)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)

        fila = 0

        # Método
        lbl_metodo = QLabel("Método (B / RF / N / S):")
        self.txt_metodo = CampoMatematico()
        self.txt_metodo.setText("B")
        self.txt_metodo.setToolTip(
            "Escribe:\n"
            "  B  = Bisección (intervalo [a,b])\n"
            "  RF = Regla Falsa (intervalo [a,b])\n"
            "  N  = Newton-Raphson (x0 punto inicial)\n"
            "  S  = Secante (x0 y x1 aproximaciones)"
        )
        self.txt_metodo.textChanged.connect(self._actualizar_campos_por_metodo)

        grid.addWidget(lbl_metodo, fila, 0)
        grid.addWidget(self.txt_metodo, fila, 1)

        # f(x)
        fila += 1
        lbl_fx = QLabel("f(x) =")
        self.txt_fx = CampoMatematico()
        self.txt_fx.setText("x³ - 4x + 1")
        self.txt_fx.setPlaceholderText("Ej: x^3 - 4x + 1, sen(x), ln(x), √(x), etc.")
        grid.addWidget(lbl_fx, fila, 0)
        grid.addWidget(self.txt_fx, fila, 1, 1, 3)

        # a / x0 y b / x1
        fila += 1
        self.lbl_a = QLabel("a (extremo izquierdo):")
        self.txt_a = CampoMatematico()
        self.txt_a.setText("0")

        self.lbl_b = QLabel("b (extremo derecho):")
        self.txt_b = CampoMatematico()
        self.txt_b.setText("2")

        grid.addWidget(self.lbl_a, fila, 0)
        grid.addWidget(self.txt_a, fila, 1)
        grid.addWidget(self.lbl_b, fila, 2)
        grid.addWidget(self.txt_b, fila, 3)

        # tol y max_iter
        fila += 1
        self.lbl_tol = QLabel("Tolerancia de convergencia Ea (ej: 0.0001):")
        self.txt_tol = CampoMatematico()
        self.txt_tol.setText("0.0001")

        lbl_max_iter = QLabel("Máx. iteraciones:")
        self.txt_max_iter = CampoMatematico()
        self.txt_max_iter.setText("50")

        grid.addWidget(self.lbl_tol, fila, 0)
        grid.addWidget(self.txt_tol, fila, 1)
        grid.addWidget(lbl_max_iter, fila, 2)
        grid.addWidget(self.txt_max_iter, fila, 3)

        # Botones
        fila += 1
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.btn_calcular = QPushButton("Calcular")
        self.btn_calcular.clicked.connect(self.calcular)

        self.btn_limpiar = QPushButton("Limpiar")
        self.btn_limpiar.clicked.connect(self.limpiar)

        self.btn_volver = QPushButton("Regresar al Menú")
        self.btn_volver.clicked.connect(self.volver_menu)

        btn_layout.addWidget(self.btn_calcular)
        btn_layout.addWidget(self.btn_limpiar)
        btn_layout.addStretch(1)
        btn_layout.addWidget(self.btn_volver)

        grid.addLayout(btn_layout, fila, 0, 1, 4)

        main_layout.addWidget(panel)

        # Parte inferior: texto + gráfica
        lbl_iter = QLabel("Tabla de iteraciones, explicación y gráfica:")
        main_layout.addWidget(lbl_iter)

        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(12)

        self.txt_iter = QTextEdit()
        self.txt_iter.setReadOnly(True)

        self.grafica_widget = GraficaWidget(self)

        bottom_layout.addWidget(self.txt_iter, stretch=1)
        bottom_layout.addWidget(self.grafica_widget, stretch=1)

        main_layout.addLayout(bottom_layout, stretch=1)

        # Resultado final
        self.lbl_resultado = QLabel("Resultado final: (pendiente de cálculo)")
        self.lbl_resultado.setWordWrap(True)
        main_layout.addWidget(self.lbl_resultado)

        # Ajustar campos iniciales según método B
        self._actualizar_campos_por_metodo(self.txt_metodo.text())

    # -------------------------------------------------------------------------
    # Actualización dinámica de campos según el método
    # -------------------------------------------------------------------------
    def _actualizar_campos_por_metodo(self, txt: str):
        m = txt.strip().upper()
        if m == "B":
            self.lbl_a.setText("a (extremo izquierdo del intervalo):")
            self.lbl_b.setText("b (extremo derecho del intervalo):")
            self.txt_b.setEnabled(True)
            self.txt_b.setPlaceholderText("")
            self.lbl_tol.setText("Tolerancia de convergencia Ea (ej: 0.0001):")

        elif m == "RF":
            self.lbl_a.setText("a (extremo izquierdo del intervalo):")
            self.lbl_b.setText("b (extremo derecho del intervalo):")
            self.txt_b.setEnabled(True)
            self.txt_b.setPlaceholderText("")
            self.lbl_tol.setText("Tolerancia de convergencia Ea (ej: 0.0001):")

        elif m == "N":
            self.lbl_a.setText("Punto inicial X₀:")
            self.lbl_b.setText("X₁ (no se usa en Newton)")
            self.txt_b.setEnabled(False)
            self.txt_b.setPlaceholderText("No se usa")
            self.lbl_tol.setText("Tolerancia de convergencia Ea (ej: 0.0001):")

        elif m == "S":
            self.lbl_a.setText("X₀ (primera aproximación):")
            self.lbl_b.setText("X₁ (segunda aproximación):")
            self.txt_b.setEnabled(True)
            self.txt_b.setPlaceholderText("")
            self.lbl_tol.setText("Tolerancia de convergencia Ea (ej: 0.0001):")

        else:
            # Cualquier otra cosa: tratamos como Bisección por defecto
            self.lbl_a.setText("a (extremo izquierdo del intervalo):")
            self.lbl_b.setText("b (extremo derecho del intervalo):")
            self.txt_b.setEnabled(True)
            self.txt_b.setPlaceholderText("")
            self.lbl_tol.setText("Tolerancia de convergencia Ea (ej: 0.0001):")

    # -------------------------------------------------------------------------
    # Acciones básicas
    # -------------------------------------------------------------------------
    def limpiar(self):
        self.txt_fx.setText("x³ - 4x + 1")
        self.txt_a.setText("0")
        self.txt_b.setText("2")
        self.txt_tol.setText("0.0001")
        self.txt_max_iter.setText("50")
        self.txt_metodo.setText("B")
        self.txt_iter.clear()
        self.lbl_resultado.setText("Resultado final: (pendiente de cálculo)")
        self.grafica_widget.limpiar()

    def volver_menu(self):
        try:
            from gui.MenuGui import MenuGui
            self.menu = MenuGui()
            self.menu.show()
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo regresar al menú:\n{e}")

    # -------------------------------------------------------------------------
    # Lógica principal
    # -------------------------------------------------------------------------
    def calcular(self):
        expr = self.txt_fx.text().strip()
        metodo = self.txt_metodo.text().strip().upper()

        if metodo not in ("B", "RF", "N", "S"):
            QMessageBox.warning(
                self,
                "Método inválido",
                "Métodos válidos:\n"
                "  B  = Bisección\n"
                "  RF = Regla Falsa\n"
                "  N  = Newton-Raphson\n"
                "  S  = Secante"
            )
            return

        # Leer tolerancia y máx. iteraciones
        try:
            tol = float(numero_desde_texto(self.txt_tol.text()))
            max_iter = int(numero_desde_texto(self.txt_max_iter.text()))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Tolerancia o iteraciones inválidas:\n{e}")
            return

        # Según el método pedimos lo que toca
        try:
            if metodo in ("B", "RF", "S"):
                a = float(numero_desde_texto(self.txt_a.text()))
                b = float(numero_desde_texto(self.txt_b.text()))
            elif metodo == "N":
                a = float(numero_desde_texto(self.txt_a.text()))   # x0
                b = None
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Datos numéricos inválidos:\n{e}")
            return

        # Validaciones por método
        if metodo in ("B", "RF"):
            # Métodos cerrados: verificar cambio de signo
            try:
                fa = evaluar_funcion(expr, a)
                fb = evaluar_funcion(expr, b)
            except Exception as e:
                QMessageBox.critical(self, "Error al evaluar f(x)", str(e))
                return

            if fa * fb > 0:
                QMessageBox.warning(
                    self,
                    "Intervalo inválido",
                    "f(a)*f(b) > 0.\nNo hay cambio de signo en el intervalo [a,b]."
                )
                return

        if metodo == "S":
            if a == b:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Para la Secante, X₀ y X₁ deben ser distintos."
                )
                return

        # Ejecutar el método
        try:
            if metodo == "B":
                nombre = "Bisección"
                raiz, historia, intervalo_final, error_final = biseccion(
                    expr, a, b, tol, max_iter
                )
                self._mostrar_iteraciones(historia, nombre)
                texto_res = (
                    f"Método: {nombre} | "
                    f"Raíz aproximada: {raiz:.10f} | "
                    f"Iteraciones: {len(historia)} | "
                    f"Error relativo final (%): {error_final:.8f} | "
                    f"Intervalo final: [{intervalo_final[0]:.8f}, {intervalo_final[1]:.8f}]"
                )
                self._dibujar_grafica(expr, "B", raiz, historia, a, b)

            elif metodo == "RF":
                nombre = "Regla Falsa"
                raiz, historia, intervalo_final, error_final = regla_falsa(
                    expr, a, b, tol, max_iter
                )
                self._mostrar_iteraciones(historia, nombre)
                texto_res = (
                    f"Método: {nombre} | "
                    f"Raíz aproximada: {raiz:.10f} | "
                    f"Iteraciones: {len(historia)} | "
                    f"Error relativo final (%): {error_final:.8f} | "
                    f"Intervalo final: [{intervalo_final[0]:.8f}, {intervalo_final[1]:.8f}]"
                )
                self._dibujar_grafica(expr, "RF", raiz, historia, a, b)

            elif metodo == "N":
                nombre = "Newton-Raphson"
                raiz, historia, error_final = newton_raphson(
                    expr, a, tol, max_iter
                )
                self._mostrar_iteraciones(historia, nombre)
                texto_res = (
                    f"Método: {nombre} | "
                    f"Punto inicial X₀: {a:.8f} | "
                    f"Raíz aproximada: {raiz:.10f} | "
                    f"Iteraciones: {len(historia)} | "
                    f"Error relativo final (%): {error_final:.8f}"
                )
                # Para la gráfica, usamos el recorrido de las aproximaciones
                self._dibujar_grafica(expr, "N", raiz, historia, a, a)

            else:  # S
                nombre = "Secante"
                raiz, historia, error_final = metodo_secante(
                    expr, a, b, tol, max_iter
                )
                self._mostrar_iteraciones(historia, nombre)
                texto_res = (
                    f"Método: {nombre} | "
                    f"X₀: {a:.8f}, X₁: {b:.8f} | "
                    f"Raíz aproximada: {raiz:.10f} | "
                    f"Iteraciones: {len(historia)} | "
                    f"Error relativo final (%): {error_final:.8f}"
                )
                self._dibujar_grafica(expr, "S", raiz, historia, a, b)

        except Exception as e:
            QMessageBox.critical(self, "Error en el método numérico", str(e))
            return

        self.lbl_resultado.setText(texto_res)

    # -------------------------------------------------------------------------
    # Gráfica
    # -------------------------------------------------------------------------
    def _dibujar_grafica(self, expr: str, metodo: str,
                         raiz, historia, a: float, b: float):
        metodo = metodo.upper()

        if metodo in ("B", "RF"):
            x_min, x_max = min(a, b), max(a, b)
        elif metodo == "N":
            xs = [fila["x"] for fila in historia] if historia else [a]
            x_min, x_max = min(xs), max(xs)
            margen = (x_max - x_min) * 0.3 if x_max != x_min else 1.0
            x_min -= margen
            x_max += margen
        else:  # Secante
            xs = []
            for fila in historia:
                xs.append(fila["x_prev"])
                xs.append(fila["x"])
            if not xs:
                xs = [a, b]
            x_min, x_max = min(xs), max(xs)
            margen = (x_max - x_min) * 0.3 if x_max != x_min else 1.0
            x_min -= margen
            x_max += margen

        self.grafica_widget.dibujar_funcion_y_raiz(
            expr=expr,
            x_min=x_min,
            x_max=x_max,
            raiz=raiz,
            evaluar_funcion_callable=evaluar_funcion
        )

    # -------------------------------------------------------------------------
    # Mostrar iteraciones + explicación (paso a paso)
    # -------------------------------------------------------------------------
    def _mostrar_iteraciones(self, historia, nombre_metodo: str):
        self.txt_iter.clear()

        # ===================== BISECCIÓN =====================
        if nombre_metodo == "Bisección":
            encabezado = (
                "=== Iteraciones - Método de Bisección ===\n"
                " i  |      X_l     |      X_u     |      X_r     |"
                "     f(X_l)     |     f(X_u)     |     f(X_r)     |   E_a(%)   |      ΔX\n"
                + "-" * 122
            )
            self.txt_iter.append(encabezado)
            for fila in historia:
                err_str = "---------"
                if fila["error_pct"] is not None:
                    err_str = f"{fila['error_pct']:10.6f}"
                linea = (
                    f"{fila['iter']:2d} | "
                    f"{fila['a']:12.8f} | "
                    f"{fila['b']:12.8f} | "
                    f"{fila['x']:12.8f} | "
                    f"{fila['fa']:13.8f} | "
                    f"{fila['fb']:13.8f} | "
                    f"{fila['fx']:13.8f} | "
                    f"{err_str:>10} | "
                    f"{fila['len_interval']:10.8f}"
                )
                self.txt_iter.append(linea)

            # Paso a paso textual
            self.txt_iter.append("\n=== Paso a paso (Bisección) ===")
            for fila in historia:
                self.txt_iter.append(
                    f"Iteración {fila['iter']}: Intervalo [X_l={fila['a']:.8f}, X_u={fila['b']:.8f}], "
                    f"X_r = (X_l + X_u)/2 = {fila['x']:.8f}, f(X_r) = {fila['fx']:.8f}, "
                    f"ΔX = {fila['len_interval']:.8f}"
                )

        # ===================== REGLA FALSA =====================
        elif nombre_metodo == "Regla Falsa":
            encabezado = (
                "=== Iteraciones - Método de Regla Falsa ===\n"
                " i  |      X_l     |      X_u     |      X_r     |"
                "     f(X_l)     |     f(X_u)     |     f(X_r)     |   E_a(%)   | Ea<E\n"
                + "-" * 122
            )
            self.txt_iter.append(encabezado)
            for fila in historia:
                err_str = "---------"
                if fila["error_pct"] is not None:
                    err_str = f"{fila['error_pct']:10.6f}"
                ea_flag = "True" if fila.get("ea_less_tol") else "False"
                linea = (
                    f"{fila['iter']:2d} | "
                    f"{fila['a']:12.8f} | "
                    f"{fila['b']:12.8f} | "
                    f"{fila['x']:12.8f} | "
                    f"{fila['fa']:13.8f} | "
                    f"{fila['fb']:13.8f} | "
                    f"{fila['fx']:13.8f} | "
                    f"{err_str:>10} | "
                    f"{ea_flag:>5}"
                )
                self.txt_iter.append(linea)

            # Paso a paso textual
            self.txt_iter.append("\n=== Paso a paso (Regla Falsa) ===")
            for fila in historia:
                self.txt_iter.append(
                    f"Iteración {fila['iter']}: Intervalo [X_l={fila['a']:.8f}, X_u={fila['b']:.8f}], "
                    f"X_r calculado por Regla Falsa = {fila['x']:.8f}, f(X_r) = {fila['fx']:.8f}, "
                    f"E_a(%) ≈ {fila['error_pct'] if fila['error_pct'] is not None else 0:.6f}"
                )

        # ===================== NEWTON-RAPHSON =====================
        elif nombre_metodo == "Newton-Raphson":
            encabezado = (
                "=== Iteraciones - Método de Newton-Raphson ===\n"
                " i  |       X_i       |      f(X_i)     |     f'(X_i)     |    E_a(%)   \n"
                + "-" * 96
            )
            self.txt_iter.append(encabezado)
            for fila in historia:
                linea = (
                    f"{fila['iter']:2d} | "
                    f"{fila['x']:14.8f} | "
                    f"{fila['fx']:14.8f} | "
                    f"{fila['dfx']:14.8f} | "
                    f"{fila['error_pct']:10.6f}"
                )
                self.txt_iter.append(linea)

            # Paso a paso textual MEJORADO
            self.txt_iter.append("\n=== Paso a paso (Newton-Raphson) ===")
            for idx, fila in enumerate(historia):
                i = fila["iter"]
                x_i = fila["x"]
                fx_i = fila["fx"]
                dfx_i = fila["dfx"]
                ea_i = fila["error_pct"]

                # Para vincular con la siguiente aproximación X_{i+1}, usamos la fila siguiente (si existe)
                if idx + 1 < len(historia):
                    x_next = historia[idx + 1]["x"]
                    paso_formula = (
                        f"     X_{i+1} = X_i - f(X_i)/f'(X_i)\n"
                        f"           ≈ {x_i:.8f} - ({fx_i:.8f})/({dfx_i:.8f}) "
                        f"= {x_next:.8f}"
                    )
                else:
                    paso_formula = (
                        "     X_{i+1} = X_i - f(X_i)/f'(X_i)\n"
                        "           (esta es la última iteración mostrada, "
                        "la siguiente X ya no se calcula)."
                    )

                self.txt_iter.append(
                    f"Iteración {i}:\n"
                    f"  1) Tomamos X_i = {x_i:.8f}\n"
                    f"  2) Evaluamos f(X_i) = {fx_i:.8f}\n"
                    f"  3) Calculamos la derivada f'(X_i) ≈ {dfx_i:.8f}\n"
                    f"  4) Aplicamos la fórmula de Newton-Raphson:\n"
                    f"{paso_formula}\n"
                    f"  5) Calculamos el error relativo porcentual: "
                    f"E_a(%) ≈ {ea_i:.6f}\n"
                )

        # ===================== SECANTE =====================
        else:  # Secante
            encabezado = (
                "=== Iteraciones - Método de la Secante ===\n"
                " i  |    X_{i-1}    |      X_i      |   f(X_{i-1})  |     f(X_i)    |   E_a(%)   \n"
                + "-" * 100
            )
            self.txt_iter.append(encabezado)
            for fila in historia:
                linea = (
                    f"{fila['iter']:2d} | "
                    f"{fila['x_prev']:12.8f} | "
                    f"{fila['x']:12.8f} | "
                    f"{fila['fx_prev']:13.8f} | "
                    f"{fila['fx']:13.8f} | "
                    f"{fila['error_pct']:10.6f}"
                )
                self.txt_iter.append(linea)

            # Paso a paso textual MEJORADO
            self.txt_iter.append("\n=== Paso a paso (Secante) ===")
            for idx, fila in enumerate(historia):
                i = fila["iter"]
                x_im1 = fila["x_prev"]
                x_i = fila["x"]
                fx_im1 = fila["fx_prev"]
                fx_i = fila["fx"]
                ea_i = fila["error_pct"]

                if idx + 1 < len(historia):
                    x_next = historia[idx + 1]["x"]
                    paso_formula = (
                        f"     X_{i+1} = X_i - f(X_i)(X_i - X_{i-1}) / (f(X_i) - f(X_{i-1}))\n"
                        f"           ≈ {x_i:.8f} - ({fx_i:.8f})({x_i:.8f} - {x_im1:.8f}) / "
                        f"({fx_i:.8f} - {fx_im1:.8f})\n"
                        f"           ≈ {x_next:.8f}"
                    )
                else:
                    paso_formula = (
                        "     X_{i+1} = X_i - f(X_i)(X_i - X_{i-1}) / (f(X_i) - f(X_{i-1}))\n"
                        "           (esta es la última iteración mostrada, "
                        "la siguiente X ya no se calcula)."
                    )

                self.txt_iter.append(
                    f"Iteración {i}:\n"
                    f"  1) Usamos X_{i-1} = {x_im1:.8f} y X_i = {x_i:.8f}\n"
                    f"  2) Evaluamos f(X_{i-1}) = {fx_im1:.8f} y f(X_i) = {fx_i:.8f}\n"
                    f"  3) Aplicamos la fórmula de la Secante:\n"
                    f"{paso_formula}\n"
                    f"  4) Calculamos el error relativo porcentual: "
                    f"E_a(%) ≈ {ea_i:.6f}\n"
                )

        # Explicación corta final
        self.txt_iter.append("\n\n=== Comentario del método ===")
        if nombre_metodo == "Bisección":
            self.txt_iter.append(
                "Bisección: método cerrado. Requiere [a,b] con cambio de signo, "
                "divide el intervalo a la mitad en cada iteración y garantiza convergencia."
            )
        elif nombre_metodo == "Regla Falsa":
            self.txt_iter.append(
                "Regla Falsa: método cerrado. Usa la recta que une (X_l,f(X_l)) y (X_u,f(X_u)) "
                "para aproximar la raíz; mantiene el cambio de signo en [a,b]."
            )
        elif nombre_metodo == "Newton-Raphson":
            self.txt_iter.append(
                "Newton-Raphson: método abierto. Requiere solo un punto inicial X₀ y la derivada; "
                "es muy rápido si X₀ está cerca de la raíz, pero puede divergir."
            )
        else:
            self.txt_iter.append(
                "Secante: método abierto. Usa dos aproximaciones iniciales X₀ y X₁, "
                "y construye secantes en lugar de la derivada exacta."
            )


# Para pruebas rápidas
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    win = MetodosNumericosGui()
    win.show()
    sys.exit(app.exec())
