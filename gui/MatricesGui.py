import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from typing import List
from fractions import Fraction
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QTextEdit, QMessageBox, QGroupBox, QGridLayout, QSizePolicy
)
from PyQt6.QtGui import QFont, QPainter, QLinearGradient, QColor
from PyQt6.QtCore import Qt, QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from models.Matrices import Matrices, GaussResult

EPS = 1e-10

# --- Fondo animado y colorido ---
class FondoAnimado(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.hue = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_color)
        self.timer.start(40)  # 25 FPS

    def actualizar_color(self):
        self.hue = (self.hue + 1) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect()
        grad = QLinearGradient(rect.topLeft(), rect.bottomRight())
        color1 = QColor.fromHsv(self.hue, 180, 255)
        color2 = QColor.fromHsv((self.hue + 120) % 360, 180, 255)
        grad.setColorAt(0, color1)
        grad.setColorAt(1, color2)
        painter.fillRect(rect, grad)

class MatrizInputWidget(QWidget):
    def __init__(self, filas: int, columnas: int, parent=None):
        super().__init__(parent)
        self.filas = filas
        self.columnas = columnas
        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.inputs: List[List[QLineEdit]] = []
        self.b_inputs: List[QLineEdit] = []
        style = "QLineEdit { background: #1b1b1b; color: #eee; border: 1px solid #444; padding:6px; }"
        # Etiquetas de columna
        for j in range(columnas):
            lbl = QLabel(f"x{j+1}")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.grid.addWidget(lbl, 0, j)
        self.grid.addWidget(QLabel("="), 0, columnas)
        self.grid.addWidget(QLabel("b"), 0, columnas+1)
        # Campos de entrada
        for i in range(filas):
            fila_inputs = []
            for j in range(columnas):
                le = QLineEdit()
                le.setFixedWidth(70)
                le.setAlignment(Qt.AlignmentFlag.AlignCenter)
                le.setStyleSheet(style)
                le.setPlaceholderText("0")
                self.grid.addWidget(le, i+1, j)
                fila_inputs.append(le)
            self.inputs.append(fila_inputs)
            eq_label = QLabel("=")
            eq_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.grid.addWidget(eq_label, i+1, columnas)
            le_b = QLineEdit()
            le_b.setFixedWidth(70)
            le_b.setAlignment(Qt.AlignmentFlag.AlignCenter)
            le_b.setStyleSheet(style)
            le_b.setPlaceholderText("0")
            self.grid.addWidget(le_b, i+1, columnas+1)
            self.b_inputs.append(le_b)

    def get_matrix_and_b(self) -> (List[List[float]], List[List[float]]):
        datos: List[List[float]] = []
        b: List[List[float]] = []
        for i in range(self.filas):
            fila: List[float] = []
            for j in range(self.columnas):
                txt = self.inputs[i][j].text().strip()
                if txt == "":
                    raise ValueError(f"Campo vacío en fila {i+1}, columna {j+1}. Completa todos los valores.")
                try:
                    val = float(txt)
                except ValueError:
                    raise ValueError(f"Valor no numérico en fila {i+1}, columna {j+1}: '{txt}'")
                fila.append(val)
            datos.append(fila)
            txt_b = self.b_inputs[i].text().strip()
            if txt_b == "":
                raise ValueError(f"Campo vacío en término independiente de la fila {i+1}.")
            try:
                val_b = float(txt_b)
            except ValueError:
                raise ValueError(f"Valor no numérico en término independiente de la fila {i+1}: '{txt_b}'")
            b.append([val_b])
        if len(datos) < 2 or len(datos[0]) < 2:
            raise ValueError("La matriz debe tener al menos 2 filas y 2 columnas (2 incógnitas).")
        return datos, b

class MatricesGui(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculadora de Sistemas — PyQt6")
        self.showFullScreen()  # Pantalla completa

        # Fondo animado
        self.fondo_animado = FondoAnimado(self)
        self.fondo_animado.lower()  # Asegura que esté detrás de todo

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # --- Barra superior con botón de casita y controles ---
        barra_superior = QHBoxLayout()
        self.btn_home = QPushButton("🏠")
        self.btn_home.setFixedSize(60, 60)
        self.btn_home.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        self.btn_home.setStyleSheet("""
            QPushButton {
                background: #f3f3f3;
                color: #222;
                border-radius: 30px;
                border: 2px solid #888;
            }
            QPushButton:hover {
                background: #ffe066;
                color: #222;
            }
        """)
        self.btn_home.clicked.connect(self.ir_a_menu)
        barra_superior.addWidget(self.btn_home)

        barra_superior.addSpacing(20)
        barra_superior.addWidget(QLabel("Filas (ecuaciones):"))
        self.filas_input = QLineEdit()
        self.filas_input.setFixedWidth(80)
        self.filas_input.setPlaceholderText("ej: 3")
        barra_superior.addWidget(self.filas_input)
        barra_superior.addWidget(QLabel("Columnas (incógnitas):"))
        self.columnas_input = QLineEdit()
        self.columnas_input.setFixedWidth(80)
        self.columnas_input.setPlaceholderText("ej: 3")
        barra_superior.addWidget(self.columnas_input)
        self.btn_generar = QPushButton("+ Generar Matriz")
        self.btn_generar.clicked.connect(self.crear_matriz)
        barra_superior.addWidget(self.btn_generar)
        self.btn_limpiar = QPushButton("Limpiar campos")
        self.btn_limpiar.clicked.connect(self.limpiar_campos)
        barra_superior.addWidget(self.btn_limpiar)
        barra_superior.addSpacing(20)
        barra_superior.addWidget(QLabel("Método:"))
        self.combo_metodo = QComboBox()
        self.combo_metodo.addItems(["Gauss", "Gauss-Jordan"])
        barra_superior.addWidget(self.combo_metodo)
        self.btn_ejecutar = QPushButton("Ejecutar")
        self.btn_ejecutar.clicked.connect(self.ejecutar_metodo)
        barra_superior.addWidget(self.btn_ejecutar)
        barra_superior.addStretch()
        self.layout.addLayout(barra_superior)

        # --- Matriz group ---
        self.matriz_group = QGroupBox("Matriz del sistema (términos independientes a la derecha)")
        self.matriz_layout = QVBoxLayout()
        self.matriz_group.setLayout(self.matriz_layout)
        self.layout.addWidget(self.matriz_group)
        self.matriz_widget = None

        # --- Resultados y gráficos ---
        bottom = QHBoxLayout()

        # Panel pasos y solución
        left = QVBoxLayout()
        self.pasos_texto = QTextEdit()
        self.pasos_texto.setReadOnly(True)
        self.pasos_texto.setFixedHeight(340)
        left.addWidget(QLabel("Pasos:"))
        left.addWidget(self.pasos_texto)
        self.sol_text = QTextEdit()
        self.sol_text.setReadOnly(True)
        self.sol_text.setFixedHeight(200)
        left.addWidget(QLabel("Solución / clasificación:"))
        left.addWidget(self.sol_text)
        bottom.addLayout(left, 2)

        # Panel gráfico
        right = QVBoxLayout()
        self.canvas = FigureCanvas(Figure(figsize=(5,4)))
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        right.addWidget(self.canvas)
        bottom.addLayout(right, 3)

        self.layout.addLayout(bottom)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "fondo_animado"):
            self.fondo_animado.setGeometry(0, 0, self.width(), self.height())

    def ir_a_menu(self):
        try:
            from MenuGui import MenuGui
            self.menu = MenuGui()
            self.menu.show()
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir MenuGui:\n{e}")

    def crear_matriz(self):
        try:
            filas = int(self.filas_input.text())
            columnas = int(self.columnas_input.text())
            if filas < 2 or columnas < 2:
                raise ValueError
        except Exception:
            QMessageBox.warning(self, "Error", "Ingrese al menos 2 filas y 2 columnas (2 incógnitas).")
            return

        # limpiar anterior
        if self.matriz_widget:
            self.matriz_layout.removeWidget(self.matriz_widget)
            self.matriz_widget.deleteLater()
            self.matriz_widget = None

        self.matriz_widget = MatrizInputWidget(filas, columnas)
        self.matriz_layout.addWidget(self.matriz_widget)

    def limpiar_campos(self):
        # Limpiar matriz
        if self.matriz_widget:
            for fila in self.matriz_widget.inputs:
                for le in fila:
                    le.clear()
            for le in self.matriz_widget.b_inputs:
                le.clear()
        # Limpiar resultados y gráfico
        self.pasos_texto.clear()
        self.sol_text.clear()
        self.canvas.figure.clf()
        self.canvas.draw()

    def ejecutar_metodo(self):
        if not self.matriz_widget:
            QMessageBox.warning(self, "Error", "Primero genere la matriz.")
            return

        try:
            a, b = self.matriz_widget.get_matrix_and_b()
            if not a or not a[0] or len(a) < 2 or len(a[0]) < 2:
                raise ValueError("La matriz debe tener al menos 2 filas y 2 incógnitas.")

            metodo = self.combo_metodo.currentText()
            self.pasos_texto.clear()
            self.sol_text.clear()
            self.canvas.figure.clf()

            if metodo == "Gauss":
                gauss_res = Matrices.gauss(a, b)
                rref_res = Matrices.gauss_jordan([row[:-1] for row in gauss_res.augmented],
                                                 [[row[-1]] for row in gauss_res.augmented])
                pasos = gauss_res.pasos + ["--- RREF (a partir del resultado) ---"] + rref_res.pasos
                final_rref = rref_res
            else:
                gauss_res = Matrices.gauss_jordan(a, b)
                pasos = gauss_res.pasos
                final_rref = gauss_res

            # Paso a paso ordenado y numerado
            pasos_ordenados = []
            for idx, paso in enumerate(pasos, 1):
                if paso.startswith("Estado actual:"):
                    pasos_ordenados.append("\n" + paso)
                else:
                    pasos_ordenados.append(f"Paso {idx}: {paso}")
            self.pasos_texto.setPlainText("\n".join(pasos_ordenados) if pasos_ordenados else "No hay pasos.")

            info = Matrices.clasificar_y_resolver_from_rref(final_rref)
            txt = "Matriz aumentada final (RREF cuando aplica):\n"
            for row in final_rref.augmented:
                txt += str([int(x) if x == int(x) else Fraction(x).limit_denominator() for x in row]) + "\n"

            # Mostrar variables básicas y libres
            m = len(a[0])
            pivote_col = [-1] * len(final_rref.augmented)
            for i, row in enumerate(final_rref.augmented):
                for j in range(m):
                    if abs(row[j]) > EPS:
                        pivote_col[i] = j
                        break
            usados = set([c for c in pivote_col if c != -1])
            basicas = [f"x{p+1}" for p in usados]
            libres = [f"x{j+1}" for j in range(m) if j not in usados]
            txt += f"\nVariables básicas (VB): {', '.join(basicas) if basicas else 'Ninguna'}"
            txt += f"\nVariables libres (VL): {', '.join(libres) if libres else 'Ninguna'}"

            # Mostrar tipo de sistema
            txt += "\n\nClasificación: " + info.get("tipo", "?").upper() + "\n\n"
            if info["tipo"] == "incompatible":
                txt += "❌ SISTEMA INCONSISTENTE: no tiene solución.\n"
            elif info["tipo"] == "determinada":
                txt += "✅ SISTEMA CONSISTENTE: solución única:\n"
                for idx, val in enumerate(info["solucion"]):
                    if val == int(val):
                        txt += f" x{idx+1} = {int(val)}\n"
                    else:
                        txt += f" x{idx+1} = {Fraction(val).limit_denominator()}\n"
                self._graficar_si_corresponde(a, b, info["solucion"])
            else:
                txt += "⚠️ SISTEMA CONSISTENTE INDETERMINADO (sol paramétrica):\n"
                for idx, expr in enumerate(info.get("solucion_parametrica", [])):
                    txt += f" x{idx+1} = {expr}\n"
                self._graficar_si_corresponde(a, b, None)

            self.sol_text.setPlainText(txt)

        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            QMessageBox.critical(self, "Error al ejecutar", f"{str(e)}\n\nTraceback (últimas líneas):\n{tb.splitlines()[-6:]}")
            return

    def _graficar_si_corresponde(self, a: List[List[float]], b: List[List[float]], solucion_unique):
        n = len(a)
        if n == 0:
            return
        m = len(a[0])
        ax = self.canvas.figure.add_subplot(111)
        ax.set_facecolor('#ffffff')

        if m != 2:
            ax.text(0.5, 0.5, "Grafico automático solo para 2 incógnitas.", ha='center', va='center')
            self.canvas.draw()
            return

        xs = [i/10 for i in range(-150, 151)]
        colores = ['#c62828', '#2e7d32', '#1565c0', '#ff8f00', '#6a1b9a']
        for i in range(n):
            A0 = a[i][0]
            A1 = a[i][1]
            B = b[i][0]
            if abs(A1) < EPS:
                if abs(A0) < EPS:
                    continue
                x_const = B / A0
                ax.plot([x_const, x_const], [-100, 100], label=f"Ecuación {i+1}")
            else:
                ys = [ (B - A0 * x)/A1 for x in xs ]
                ax.plot(xs, ys, label=f"Ecuación {i+1}", color=colores[i % len(colores)])

        if solucion_unique is not None and len(solucion_unique) >= 2:
            x_sol = solucion_unique[0]
            y_sol = solucion_unique[1]
            ax.scatter([x_sol], [y_sol], s=80, color='black', zorder=5)
            ax.annotate(f"({x_sol:.3g}, {y_sol:.3g})", (x_sol, y_sol), textcoords="offset points", xytext=(8,8), color='black')

        ax.set_xlim(-10, 10)
        ax.set_ylim(-10, 10)
        ax.grid(True)
        ax.legend(loc='upper right')
        ax.set_title("Sistema 2x2")
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MatricesGui()
    window.show()
    sys.exit(app.exec())