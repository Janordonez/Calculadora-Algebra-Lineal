import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from typing import List
from fractions import Fraction
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QTextEdit, QMessageBox, QGroupBox, QGridLayout, QSizePolicy,
    QGraphicsDropShadowEffect
)
from PyQt6.QtGui import QFont, QPainter, QLinearGradient, QColor
from PyQt6.QtCore import Qt, QTimer
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from models.Matrices import Matrices, GaussResult

EPS = 1e-10

# --- Fondo animado sutil ---
class FondoAnimado(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.offset = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_animacion)
        self.timer.start(80)  # animación suave, baja CPU

    def actualizar_animacion(self):
        self.offset = (self.offset + 1) % 400
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect()
        grad = QLinearGradient(rect.topLeft(), rect.bottomRight())
        # paleta sobria: azul-gris profundo
        grad.setColorAt(0, QColor("#0b1220"))
        grad.setColorAt(0.5, QColor("#0f1b2a"))
        grad.setColorAt(1, QColor("#0b1220"))
        painter.fillRect(rect, grad)

        # ondas muy sutiles con baja opacidad
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(90, 140, 180, 18))  # tono azul suave, muy translúcido
        for i in range(-400, self.width() + 400, 220):
            painter.drawEllipse(i + self.offset, rect.height() // 2 - 80, 220, 220)


# --- Widget para entrada de la matriz ---
class MatrizInputWidget(QWidget):
    def __init__(self, filas: int, columnas: int, parent=None):
        super().__init__(parent)
        self.filas = filas
        self.columnas = columnas
        self.grid = QGridLayout()
        self.grid.setHorizontalSpacing(8)
        self.grid.setVerticalSpacing(8)
        self.setLayout(self.grid)
        self.inputs: List[List[QLineEdit]] = []
        self.b_inputs: List[QLineEdit] = []

        input_style = """
            QLineEdit {
                background: #0f1b2a;
                color: #e6eef6;
                border: 1px solid #22313f;
                border-radius: 6px;
                padding: 6px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #66a6d9;
                background: #0b1623;
            }
        """
        label_style = """
            QLabel {
                color: #cfe7fb;
                font-size: 13px;
                font-weight: 600;
            }
        """

        # etiquetas de columnas
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

        # campos de entrada
        for i in range(filas):
            fila_inputs = []
            for j in range(columnas):
                le = QLineEdit()
                le.setFixedWidth(78)
                le.setAlignment(Qt.AlignmentFlag.AlignCenter)
                le.setStyleSheet(input_style)
                le.setPlaceholderText("0")
                self.grid.addWidget(le, i+1, j)
                fila_inputs.append(le)
            self.inputs.append(fila_inputs)

            eq_label = QLabel("=")
            eq_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            eq_label.setStyleSheet(label_style)
            self.grid.addWidget(eq_label, i+1, columnas)

            le_b = QLineEdit()
            le_b.setFixedWidth(78)
            le_b.setAlignment(Qt.AlignmentFlag.AlignCenter)
            le_b.setStyleSheet(input_style)
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


# --- GUI principal ---
class MatricesGui(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculadora de Sistemas — PyQt6")
        self.showFullScreen()  # muestra a pantalla completa

        # fondo animado y detrás de todo
        self.fondo_animado = FondoAnimado(self)
        self.fondo_animado.lower()

        # layout principal
        self.layout = QVBoxLayout()
        self.layout.setSpacing(12)
        self.layout.setContentsMargins(18, 18, 18, 18)
        self.setLayout(self.layout)

        # Estilo global refinado (colores sobrios, tipografía consistente)
        self.setStyleSheet("""
            QWidget {
                background-color: #0b1220;
                color: #e6eef6;
                font-family: 'Segoe UI', 'Inter', 'Arial';
                font-size: 13px;
            }
            QLabel {
                color: #cfe7fb;
                font-weight: 600;
            }
            QGroupBox {
                color: #e6eef6;
                font-size: 14px;
                font-weight: 700;
                border: 1px solid #22313f;
                border-radius: 10px;
                margin-top: 10px;
                background-color: rgba(15,27,42,0.9);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 10px;
                border-radius: 6px;
                background-color: rgba(34,49,63,0.85);
                color: #90d1f9;
                font-size: 13px;
            }
            QPushButton {
                background-color: #153246;
                color: #e6eef6;
                border-radius: 8px;
                padding: 8px 14px;
                border: 1px solid #2a4a63;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #2a4a63;
            }
            QPushButton:pressed {
                background-color: #122634;
            }
            QLineEdit, QComboBox {
                background-color: #0f1b2a;
                color: #e6eef6;
                border: 1px solid #1f3341;
                border-radius: 6px;
                padding: 6px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #66a6d9;
                background-color: #0b1623;
            }
            QTextEdit {
                background-color: #0f1b2a;
                color: #e6eef6;
                border: 1px solid #1f3341;
                border-radius: 10px;
                padding: 10px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12.5px;
            }
            QScrollBar:vertical {
                background: #0f1b2a;
                width: 10px;
            }
            QScrollBar::handle:vertical {
                background: #25414f;
                border-radius: 5px;
            }
        """)

        # --- barra superior con controles ---
        barra_superior = QHBoxLayout()
        barra_superior.setSpacing(10)

        # botón home elegante
        self.btn_home = QPushButton("🏠")
        self.btn_home.setFixedSize(52, 52)
        fbtn = QFont("Segoe UI", 20)
        fbtn.setWeight(QFont.Weight.Bold)
        self.btn_home.setFont(fbtn)
        self.btn_home.clicked.connect(self.ir_a_menu)
        barra_superior.addWidget(self.btn_home)

        barra_superior.addSpacing(10)
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

        barra_superior.addSpacing(10)
        barra_superior.addWidget(QLabel("Método:"))
        self.combo_metodo = QComboBox()
        self.combo_metodo.addItems(["Gauss", "Gauss-Jordan"])
        barra_superior.addWidget(self.combo_metodo)

        self.btn_ejecutar = QPushButton("Ejecutar")
        self.btn_ejecutar.clicked.connect(self.ejecutar_metodo)
        barra_superior.addWidget(self.btn_ejecutar)

        barra_superior.addStretch()
        self.layout.addLayout(barra_superior)

        # --- grupo matriz ---
        self.matriz_group = QGroupBox("Matriz del sistema (términos independientes a la derecha)")
        self.matriz_layout = QVBoxLayout()
        self.matriz_layout.setContentsMargins(12, 12, 12, 12)
        self.matriz_group.setLayout(self.matriz_layout)
        self.layout.addWidget(self.matriz_group)
        self.matriz_widget = None

        # sombra sutil
        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(24)
        sombra.setOffset(0, 0)
        sombra.setColor(QColor(0, 0, 0, 130))
        self.matriz_group.setGraphicsEffect(sombra)

        # --- panel inferior con pasos/solución y gráfico ---
        bottom = QHBoxLayout()
        bottom.setSpacing(12)

        # panel izquierdo: pasos y solución (autoajustan)
        left = QVBoxLayout()
        left.setSpacing(8)
        lbl_pasos = QLabel("Pasos:")
        left.addWidget(lbl_pasos)
        self.pasos_texto = QTextEdit()
        self.pasos_texto.setReadOnly(True)
        self.pasos_texto.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        left.addWidget(self.pasos_texto, 2)  # ocupa más espacio vertical

        lbl_sol = QLabel("Solución / clasificación:")
        left.addWidget(lbl_sol)
        self.sol_text = QTextEdit()
        self.sol_text.setReadOnly(True)
        self.sol_text.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        left.addWidget(self.sol_text, 1)

        # panel derecho: gráfico
        right = QVBoxLayout()
        self.canvas = FigureCanvas(Figure(figsize=(5, 4)))
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
                # construir RREF a partir del resultado de Gauss (si necesitas RREF para clasificar)
                rref_res = Matrices.gauss_jordan([row[:-1] for row in gauss_res.augmented],
                                                 [[row[-1]] for row in gauss_res.augmented])
                pasos = gauss_res.pasos + ["--- RREF (a partir del resultado) ---"] + rref_res.pasos
                final_rref = rref_res
            else:
                gauss_res = Matrices.gauss_jordan(a, b)
                pasos = gauss_res.pasos
                final_rref = gauss_res

            # paso a paso ordenado y numerado (preservando "Estado actual:")
            pasos_ordenados = []
            for idx, paso in enumerate(pasos, 1):
                if paso.startswith("Estado actual:"):
                    pasos_ordenados.append("\n" + paso)
                else:
                    pasos_ordenados.append(f"Paso {idx}: {paso}")
            self.pasos_texto.setPlainText("\n".join(pasos_ordenados) if pasos_ordenados else "No hay pasos.")

            # clasificación y presentación de solución (igual que la versión funcional original)
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

            # Mostrar tipo de sistema y soluciones
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
            # mostramos mensaje con las últimas líneas del traceback para depuración
            QMessageBox.critical(self, "Error al ejecutar", f"{str(e)}\n\nTraceback (últimas líneas):\n{tb.splitlines()[-6:]}")
            return

    def _graficar_si_corresponde(self, a: List[List[float]], b: List[List[float]], solucion_unique):
        n = len(a)
        if n == 0:
            return
        m = len(a[0])
        ax = self.canvas.figure.add_subplot(111)
        ax.clear()
        ax.set_facecolor('#f8fafc')

        if m != 2:
            ax.text(0.5, 0.5, "Grafico automático solo para 2 incógnitas.", ha='center', va='center')
            self.canvas.draw()
            return

        xs = [i/10 for i in range(-150, 151)]
        colores = ['#264653', '#2a9d8f', '#2b5d9f', '#e9c46a', '#6a4c93']
        for i in range(n):
            A0 = a[i][0]
            A1 = a[i][1]
            B = b[i][0]
            if abs(A1) < EPS:
                if abs(A0) < EPS:
                    continue
                x_const = B / A0
                ax.plot([x_const, x_const], [-100, 100], label=f"Ecuación {i+1}", color=colores[i % len(colores)])
            else:
                ys = [ (B - A0 * x)/A1 for x in xs ]
                ax.plot(xs, ys, label=f"Ecuación {i+1}", color=colores[i % len(colores)])

        if solucion_unique is not None and len(solucion_unique) >= 2:
            x_sol = solucion_unique[0]
            y_sol = solucion_unique[1]
            ax.scatter([x_sol], [y_sol], s=80, color='#0b1623', zorder=5)
            ax.annotate(f"({x_sol:.3g}, {y_sol:.3g})", (x_sol, y_sol), textcoords="offset points", xytext=(8,8), color='#0b1623')

        ax.set_xlim(-10, 10)
        ax.set_ylim(-10, 10)
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.legend(loc='upper right')
        ax.set_title("Sistema 2x2")
        self.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MatricesGui()
    window.show()
    sys.exit(app.exec())
