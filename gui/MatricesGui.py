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
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from models.Matrices import Matrices, GaussResult

EPS = 1e-10

# --- Animated Background with Blue Theme ---
class FondoAnimado(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.offset = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_animacion)
        self.timer.start(50)  # 20 FPS for smooth animation

    def actualizar_animacion(self):
        self.offset = (self.offset + 1) % 200
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect()
        grad = QLinearGradient(rect.topLeft(), rect.bottomRight())
        grad.setColorAt(0, QColor("#1e3a8a"))  # Dark blue
        grad.setColorAt(0.5, QColor("#3b82f6"))  # Medium blue
        grad.setColorAt(1, QColor("#1e40af"))  # Slightly darker blue
        painter.fillRect(rect, grad)

        # Subtle wave effect
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(255, 255, 255, 20))
        for i in range(-200, self.width(), 100):
            painter.drawEllipse(i + self.offset, rect.height() // 2, 150, 150)

class MatrizInputWidget(QWidget):
    def __init__(self, filas: int, columnas: int, parent=None):
        super().__init__(parent)
        self.filas = filas
        self.columnas = columnas
        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.inputs: List[List[QLineEdit]] = []
        self.b_inputs: List[QLineEdit] = []
        style = """
            QLineEdit {
                background: #1e40af;
                color: #ffffff;
                border: 1px solid #3b82f6;
                border-radius: 5px;
                padding: 8px;
                font-family: Inter, Arial;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #60a5fa;
                background: #1e3a8a;
            }
        """
        label_style = """
            QLabel {
                color: #ffffff;
                font-family: Inter, Arial;
                font-size: 14px;
                font-weight: bold;
            }
        """
        # Column labels
        for j in range(columnas):
            lbl = QLabel(f"x{j+1}")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet(label_style)
            self.grid.addWidget(lbl, 0, j)
        eq_label = QLabel("=")
        eq_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        eq_label.setStyleSheet(label_style)
        self.grid.addWidget(eq_label, 0, columnas)
        b_label = QLabel("b")
        b_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        b_label.setStyleSheet(label_style)
        self.grid.addWidget(b_label, 0, columnas+1)
        # Input fields
        for i in range(filas):
            fila_inputs = []
            for j in range(columnas):
                le = QLineEdit()
                le.setFixedWidth(80)
                le.setAlignment(Qt.AlignmentFlag.AlignCenter)
                le.setStyleSheet(style)
                le.setPlaceholderText("0")
                self.grid.addWidget(le, i+1, j)
                fila_inputs.append(le)
            self.inputs.append(fila_inputs)
            eq_label = QLabel("=")
            eq_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            eq_label.setStyleSheet(label_style)
            self.grid.addWidget(eq_label, i+1, columnas)
            le_b = QLineEdit()
            le_b.setFixedWidth(80)
            le_b.setAlignment(Qt.AlignmentFlag.AlignCenter)
            le_b.setStyleSheet(style)
            le_b.setPlaceholderText("0")
            self.grid.addWidget(le_b, i+1, columnas+1)
            self.b_inputs.append(le_b)

    def get_matrix_and_b(self) -> tuple[List[List[float]], List[List[float]]]:
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
        self.showFullScreen()

        # Animated background
        self.fondo_animado = FondoAnimado(self)
        self.fondo_animado.lower()

        self.layout = QVBoxLayout()
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(self.layout)

        # --- Top bar with controls ---
        barra_superior = QHBoxLayout()
        barra_superior.setSpacing(15)
        self.btn_home = QPushButton("🏠")
        self.btn_home.setFixedSize(50, 50)
        self.btn_home.setFont(QFont("Inter, Arial", 24, QFont.Weight.Bold))
        self.btn_home.setStyleSheet("""
            QPushButton {
                background: #2563eb;
                color: #ffffff;
                border-radius: 10px;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                background: #3b82f6;
            }
        """)
        self.btn_home.clicked.connect(self.ir_a_menu)
        barra_superior.addWidget(self.btn_home)

        label_style = """
            QLabel {
                color: #ffffff;
                font-family: Inter, Arial;
                font-size: 14px;
                font-weight: bold;
            }
        """
        input_style = """
            QLineEdit {
                background: #1e40af;
                color: #ffffff;
                border: 1px solid #3b82f6;
                border-radius: 5px;
                padding: 8px;
                font-family: Inter, Arial;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #60a5fa;
                background: #1e3a8a;
            }
        """
        button_style = """
            QPushButton {
                background: #2563eb;
                color: #ffffff;
                border-radius: 8px;
                padding: 10px;
                font-family: Inter, Arial;
                font-size: 14px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background: #3b82f6;
            }
            QPushButton:pressed {
                background: #1e40af;
            }
        """
        combo_style = """
            QComboBox {
                background: #1e40af;
                color: #ffffff;
                border: 1px solid #3b82f6;
                border-radius: 5px;
                padding: 8px;
                font-family: Inter, Arial;
                font-size: 14px;
            }
            QComboBox:hover {
                background: #3b82f6;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(:/icons/down-arrow.png);
                width: 14px;
                height: 14px;
            }
        """
        barra_superior.addSpacing(20)
        filas_label = QLabel("Filas (ecuaciones):")
        filas_label.setStyleSheet(label_style)
        barra_superior.addWidget(filas_label)
        self.filas_input = QLineEdit()
        self.filas_input.setFixedWidth(80)
        self.filas_input.setPlaceholderText("ej: 3")
        self.filas_input.setStyleSheet(input_style)
        barra_superior.addWidget(self.filas_input)
        columnas_label = QLabel("Columnas (incógnitas):")
        columnas_label.setStyleSheet(label_style)
        barra_superior.addWidget(columnas_label)
        self.columnas_input = QLineEdit()
        self.columnas_input.setFixedWidth(80)
        self.columnas_input.setPlaceholderText("ej: 3")
        self.columnas_input.setStyleSheet(input_style)
        barra_superior.addWidget(self.columnas_input)
        self.btn_generar = QPushButton("+ Generar Matriz")
        self.btn_generar.setStyleSheet(button_style)
        self.btn_generar.clicked.connect(self.crear_matriz)
        barra_superior.addWidget(self.btn_generar)
        self.btn_limpiar = QPushButton("Limpiar campos")
        self.btn_limpiar.setStyleSheet(button_style)
        self.btn_limpiar.clicked.connect(self.limpiar_campos)
        barra_superior.addWidget(self.btn_limpiar)
        barra_superior.addSpacing(20)
        metodo_label = QLabel("Método:")
        metodo_label.setStyleSheet(label_style)
        barra_superior.addWidget(metodo_label)
        self.combo_metodo = QComboBox()
        self.combo_metodo.addItems(["Gauss", "Gauss-Jordan"])
        self.combo_metodo.setStyleSheet(combo_style)
        barra_superior.addWidget(self.combo_metodo)
        self.btn_ejecutar = QPushButton("Ejecutar")
        self.btn_ejecutar.setStyleSheet(button_style)
        self.btn_ejecutar.clicked.connect(self.ejecutar_metodo)
        barra_superior.addWidget(self.btn_ejecutar)
        barra_superior.addStretch()
        self.layout.addLayout(barra_superior)

        # --- Matrix group ---
        self.matriz_group = QGroupBox("Matriz del sistema (términos independientes a la derecha)")
        self.matriz_group.setStyleSheet("""
            QGroupBox {
                color: #ffffff;
                font-family: Inter, Arial;
                font-size: 16px;
                font-weight: bold;
                border: 1px solid #3b82f6;
                border-radius: 10px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px 10px;
                background: #2563eb;
                border-radius: 5px;
            }
        """)
        self.matriz_layout = QVBoxLayout()
        self.matriz_layout.setContentsMargins(15, 15, 15, 15)
        self.matriz_group.setLayout(self.matriz_layout)
        self.layout.addWidget(self.matriz_group)
        self.matriz_widget = None

        # --- Results and graph ---
        bottom = QHBoxLayout()
        bottom.setSpacing(15)

        # Steps and solution panel
        left = QVBoxLayout()
        left.setSpacing(10)
        label_pasos = QLabel("Pasos:")
        label_pasos.setStyleSheet(label_style)
        left.addWidget(label_pasos)
        self.pasos_texto = QTextEdit()
        self.pasos_texto.setReadOnly(True)
        self.pasos_texto.setStyleSheet("""
            QTextEdit {
                background: #1e40af;
                color: #ffffff;
                border: 1px solid #3b82f6;
                border-radius: 10px;
                padding: 10px;
                font-family: Inter, Arial;
                font-size: 14px;
            }
        """)
        self.pasos_texto.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        left.addWidget(self.pasos_texto, 2)

        label_sol = QLabel("Solución / clasificación:")
        label_sol.setStyleSheet(label_style)
        left.addWidget(label_sol)
        self.sol_text = QTextEdit()
        self.sol_text.setReadOnly(True)
        self.sol_text.setStyleSheet("""
            QTextEdit {
                background: #1e40af;
                color: #ffffff;
                border: 1px solid #3b82f6;
                border-radius: 10px;
                padding: 10px;
                font-family: Inter, Arial;
                font-size: 14px;
            }
        """)
        self.sol_text.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        left.addWidget(self.sol_text, 1)

        # Graph panel
        right = QVBoxLayout()
        self.canvas = FigureCanvas(Figure(figsize=(5, 4)))
        self.canvas.setStyleSheet("background: #ffffff; border-radius: 10px;")
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        right.addWidget(self.canvas)

        bottom.addLayout(left, 2)
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

        if self.matriz_widget:
            self.matriz_layout.removeWidget(self.matriz_widget)
            self.matriz_widget.deleteLater()
            self.matriz_widget = None

        self.matriz_widget = MatrizInputWidget(filas, columnas)
        self.matriz_layout.addWidget(self.matriz_widget)

    def limpiar_campos(self):
        if self.matriz_widget:
            for fila in self.matriz_widget.inputs:
                for le in fila:
                    le.clear()
            for le in self.matriz_widget.b_inputs:
                le.clear()
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

            # Formatear los pasos con un espacio entre cada paso para que
            # la impresión no quede "pegada" una línea sobre otra.
            pasos_ordenados = []
            for idx, paso in enumerate(pasos, 1):
                # Si el paso ya es una descripción del estado actual, úsalo tal cual
                # (sin añadir saltos extra al principio). Para los demás pasos,
                # anteponemos un índice para mayor claridad.
                if paso.startswith("Estado actual:"):
                    pasos_ordenados.append(paso)
                else:
                    pasos_ordenados.append(f"Paso {idx}: {paso}")

            # Usar doble salto de línea entre bloques para evitar que queden
            # pegados cuando un paso contiene varias líneas (por ejemplo
            # matrices impresas). QTextEdit respetará estos saltos.
            self.pasos_texto.setPlainText("\n\n".join(pasos_ordenados) if pasos_ordenados else "No hay pasos.")

            info = Matrices.clasificar_y_resolver_from_rref(final_rref)
            txt = "Matriz aumentada final (RREF cuando aplica):\n"
            for row in final_rref.augmented:
                txt += str([int(x) if x == int(x) else Fraction(x).limit_denominator() for x in row]) + "\n"

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

    def _graficar_si_corresponde(self, a: List[List[float]], b: List[List[float]], solucion_unique):
        try:
            n = len(a)
            if n == 0:
                return
            m = len(a[0])
            ax = self.canvas.figure.add_subplot(111)
            ax.set_facecolor('#f8fafc')

            if m != 2:
                ax.text(0.5, 0.5, "Gráfico automático solo para 2 incógnitas.", ha='center', va='center', fontfamily='Inter, Arial', fontsize=12)
                self.canvas.draw()
                return

            xs = [i/10 for i in range(-150, 151)]
            colores = ['#2563eb', '#1d4ed8', '#3b82f6', '#60a5fa', '#93c5fd']
            plotted = False
            for i in range(n):
                A0 = a[i][0]
                A1 = a[i][1]
                B = b[i][0]
                if abs(A0) < EPS and abs(A1) < EPS:
                    continue
                if abs(A1) < EPS:
                    x_const = B / A0
                    ax.plot([x_const, x_const], [-100, 100], label=f"Ecuación {i+1}", color=colores[i % len(colores)], linewidth=2)
                else:
                    ys = [(B - A0 * x) / A1 for x in xs]
                    ax.plot(xs, ys, label=f"Ecuación {i+1}", color=colores[i % len(colores)], linewidth=2)
                plotted = True

            if not plotted:
                ax.text(0.5, 0.5, "No se pueden graficar ecuaciones inválidas.", ha='center', va='center', fontfamily='Inter, Arial', fontsize=12)
                self.canvas.draw()
                return

            if solucion_unique is not None and len(solucion_unique) >= 2 and all(isinstance(x, (int, float)) for x in solucion_unique[:2]):
                x_sol = solucion_unique[0]
                y_sol = solucion_unique[1]
                ax.scatter([x_sol], [y_sol], s=100, color='#1e3a8a', zorder=5)
                ax.annotate(f"({x_sol:.3g}, {y_sol:.3g})", (x_sol, y_sol), textcoords="offset points", xytext=(10,10), color='#1e3a8a', fontfamily='Inter, Arial')

            ax.set_xlim(-10, 10)
            ax.set_ylim(-10, 10)
            ax.grid(True, linestyle='--', alpha=0.7)
            ax.legend(loc='upper right', frameon=True, facecolor='#f8fafc', edgecolor='#3b82f6')
            ax.set_title("Sistema 2x2", fontfamily='Inter, Arial', fontsize=14, fontweight='bold')
            self.canvas.draw()
            self.canvas.flush_events()
        except Exception as e:
            ax.clear()
            ax.text(0.5, 0.5, f"Error al graficar: {str(e)}", ha='center', va='center', fontfamily='Inter, Arial', fontsize=12)
            self.canvas.draw()
            self.canvas.flush_events()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Modern look
    window = MatricesGui()
    window.show()
    sys.exit(app.exec())