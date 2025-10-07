import sys
import os
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QTextEdit, QLineEdit, QMessageBox, QSizePolicy, QGridLayout
)
from PyQt6.QtGui import QFont, QPainter, QColor
from PyQt6.QtCore import Qt, QTimer

from models.Vectores import Vector, solucionMatrizVector, dependencia_lineal_pasos

class FondoAnimado(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_animacion)
        self.timer.start(70)
        self.simbolos = [
            "x", "y", "z", "λ", "μ", "α", "β", "Σ", "∑", "∈", "∉", "∩", "∪", "⊂", "⊆", "⊄", "⊇",
            "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
            "+", "-", "=", "≠", "≤", "≥", "→", "←", "·", "⋅", "∥", "⊥", "det", "rank", "dim",
            "A", "B", "C", "v", "w", "u", "T", "M", "R", "ℝ", "ℤ", "ℚ", "ℂ"
        ]
        self.formulas = [
            "Ax = b", "det(A)", "rank(A)", "x ∈ ℝⁿ", "v · w", "||v||", "A⁻¹", "ker(T)", "Im(T)", "span{v₁,...,vₙ}",
            "λI - A", "Σvᵢ", "dim(V)", "A·B", "v⊥w", "x = A⁻¹b"
        ]
        self.columns = []
        self.init_columns()

    def resizeEvent(self, event):
        self.init_columns()

    def init_columns(self):
        ancho = self.width()
        alto = self.height()
        font_size = 28
        col_width = font_size + 8
        n_cols = max(1, ancho // col_width)
        self.columns = []
        for i in range(n_cols):
            x = i * col_width
            y = random.randint(-alto, alto)
            speed = random.uniform(2.0, 4.0)
            self.columns.append({
                "x": x,
                "y": y,
                "speed": speed,
                "trail": random.randint(6, 16),
                "chars": [self.random_symbol_or_formula() for _ in range(alto // font_size + 2)]
            })

    def random_symbol_or_formula(self):
        if random.random() < 0.7:
            return random.choice(self.simbolos)
        else:
            return random.choice(self.formulas)

    def actualizar_animacion(self):
        alto = self.height()
        font_size = 28
        for col in self.columns:
            col["y"] += col["speed"]
            if col["y"] > alto + font_size * 2:
                col["y"] = random.randint(-alto // 2, 0)
                col["speed"] = random.uniform(2.0, 4.0)
                col["trail"] = random.randint(6, 16)
                col["chars"] = [self.random_symbol_or_formula() for _ in range(alto // font_size + 2)]
            else:
                for i in range(len(col["chars"])):
                    if random.random() < 0.08:
                        col["chars"][i] = self.random_symbol_or_formula()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        # Fondo negro
        painter.fillRect(self.rect(), QColor(0, 0, 0))
        font_size = 28
        painter.setFont(QFont("Consolas", font_size, QFont.Weight.Bold))
        alto = self.height()
        for col in self.columns:
            x = col["x"]
            y = col["y"]
            for i in range(col["trail"]):
                yy = y - i * font_size
                if 0 <= yy < alto:
                    # Verde Matrix: cabeza más brillante, cola más tenue
                    if i == 0:
                        color = QColor(180, 255, 180, 255)  # Verde claro brillante
                    else:
                        color = QColor(0, 255, 70, max(40, 180 - i * 18))
                    painter.setPen(color)
                    txt = col["chars"][int(yy // font_size) % len(col["chars"])]
                    painter.drawText(int(x), int(yy), font_size + 10, font_size + 10, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, txt)

class VectoresGui(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Álgebra Lineal - Operaciones con Vectores')
        self.resize(1200, 800)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.setLayout(self.layout)
        # Fondo animado como hijo directo de la ventana
        self.fondo = FondoAnimado(self)
        self.fondo.lower()
        self._crear_barra_superior()
        self._crear_tamanos_vectores()
        self._crear_grid_vectores()
        self._crear_operaciones()
        self._crear_resultado()
        self.showFullScreen()  # <-- Mueve esto aquí, al final del __init__

    def resizeEvent(self, event):
        if hasattr(self, "fondo"):
            self.fondo.resize(self.size())
        super().resizeEvent(event)

    def _crear_barra_superior(self):
        barra_superior = QHBoxLayout()
        self.btn_home = QPushButton("🏠")
        self.btn_home.setFixedSize(60, 60)
        self.btn_home.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        self.btn_home.setStyleSheet("""
            QPushButton {
                background: #222;
                color: #b6ffb6;
                border-radius: 30px;
                border: 2px solid #b6ffb6;
            }
            QPushButton:hover {
                background: #333;
                color: #fff;
            }
        """)
        self.btn_home.clicked.connect(self.ir_a_menu)
        barra_superior.addWidget(self.btn_home)
        barra_superior.addSpacing(20)

        barra_superior.addWidget(QLabel("Cantidad de vectores:"))
        self.combo_cant_vectores = QComboBox()
        self.combo_cant_vectores.addItems([str(i) for i in range(2, 6)])
        self.combo_cant_vectores.currentIndexChanged.connect(self.actualizar_tamanos_vectores)
        barra_superior.addWidget(self.combo_cant_vectores)
        self.layout.addLayout(barra_superior)

    def _crear_tamanos_vectores(self):
        self.tamanos_layout = QHBoxLayout()
        self.tamanos_labels = []
        self.tamanos_combos = []
        self.layout.addLayout(self.tamanos_layout)

    def _crear_grid_vectores(self):
        self.vectores_grid = QGridLayout()
        self.layout.addLayout(self.vectores_grid)
        self.campos_vectores = []
        self.actualizar_tamanos_vectores()

    def _crear_operaciones(self):
        oper_layout = QHBoxLayout()
        oper_layout.addWidget(QLabel('Operación:'))
        self.combo_oper = QComboBox()
        self.combo_oper.addItems([
            'Suma', 'Resta', 'Multiplicación', 'Escalar', 'Eliminar coma y punto',
            'Solución Matriz de Vectores', 'Dependencia/Independencia Lineal'
        ])
        oper_layout.addWidget(self.combo_oper)
        self.btn_ejecutar = QPushButton('Ejecutar')
        self.btn_ejecutar.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.btn_ejecutar.setStyleSheet("background: #222; color: #b6ffb6; border-radius: 10px;")
        self.btn_ejecutar.clicked.connect(self.ejecutar_operacion)
        oper_layout.addWidget(self.btn_ejecutar)
        self.btn_limpiar = QPushButton('Limpiar')
        self.btn_limpiar.setFont(QFont("Segoe UI", 14))
        self.btn_limpiar.setStyleSheet("background: #333; color: #b6ffb6; border-radius: 10px;")
        self.btn_limpiar.clicked.connect(self.limpiar_campos)
        oper_layout.addWidget(self.btn_limpiar)
        self.layout.addLayout(oper_layout)

    def _crear_resultado(self):
        self.resultado_label = QLabel('Solución paso a paso:')
        self.resultado_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.resultado_label.setStyleSheet("color: #b6ffb6;")
        self.layout.addWidget(self.resultado_label)
        self.resultado_texto = QTextEdit()
        self.resultado_texto.setReadOnly(True)
        self.resultado_texto.setFont(QFont("Consolas", 16))
        self.resultado_texto.setFixedHeight(350)
        self.resultado_texto.setStyleSheet("""
            background: #111;
            color: #b6ffb6;
            border-radius: 12px;
            border: 1px solid #b6ffb6;
        """)
        self.resultado_texto.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.layout.addWidget(self.resultado_texto)

    def resizeEvent(self, event):
        if hasattr(self, "fondo"):
            self.fondo.resize(self.size())
        super().resizeEvent(event)

    def limpiar_campos(self):
        for fila in self.campos_vectores:
            for campo in fila:
                campo.clear()
        self.resultado_texto.clear()

    def actualizar_tamanos_vectores(self):
        for lbl in self.tamanos_labels:
            self.tamanos_layout.removeWidget(lbl)
            lbl.deleteLater()
        for combo in self.tamanos_combos:
            self.tamanos_layout.removeWidget(combo)
            combo.deleteLater()
        self.tamanos_labels = []
        self.tamanos_combos = []
        cant = int(self.combo_cant_vectores.currentText())
        for i in range(cant):
            lbl = QLabel(f"Tamaño V{i+1}:")
            lbl.setStyleSheet("color: #b6ffb6;")
            combo = QComboBox()
            combo.addItems([str(j) for j in range(1, 11)])
            combo.currentIndexChanged.connect(self.actualizar_campos_vectores)
            self.tamanos_layout.addWidget(lbl)
            self.tamanos_layout.addWidget(combo)
            self.tamanos_labels.append(lbl)
            self.tamanos_combos.append(combo)
        self.actualizar_campos_vectores()

    def actualizar_campos_vectores(self):
        for fila in self.campos_vectores:
            for campo in fila:
                campo.deleteLater()
        self.campos_vectores = []
        while self.vectores_grid.count():
            item = self.vectores_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        cant = len(self.tamanos_combos)
        tamanos = [int(combo.currentText()) for combo in self.tamanos_combos]
        max_tam = max(tamanos) if tamanos else 0
        for i in range(max_tam):
            lbl = QLabel(f"x{i+1}")
            lbl.setStyleSheet("color: #b6ffb6;")
            self.vectores_grid.addWidget(lbl, 0, i+1, alignment=Qt.AlignmentFlag.AlignCenter)
        for j in range(cant):
            lbl = QLabel(f"<b>Vector {j+1}</b>")
            lbl.setStyleSheet("color: #b6ffb6;")
            self.vectores_grid.addWidget(lbl, j+1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
            fila_campos = []
            for i in range(max_tam):
                if i < tamanos[j]:
                    campo = QLineEdit()
                    campo.setFixedWidth(80)
                    campo.setFont(QFont("Segoe UI", 14))
                    campo.setStyleSheet("background: #222; color: #b6ffb6; border-radius: 6px;")
                    self.vectores_grid.addWidget(campo, j+1, i+1)
                else:
                    campo = QLineEdit()
                    campo.setFixedWidth(80)
                    campo.setFont(QFont("Segoe UI", 14))
                    campo.setDisabled(True)
                    campo.setStyleSheet("background: #222; color: #444; border-radius: 6px;")
                    self.vectores_grid.addWidget(campo, j+1, i+1)
                fila_campos.append(campo)
            self.campos_vectores.append(fila_campos)

    def obtener_vectores(self):
        vectores = []
        tamanos = [int(combo.currentText()) for combo in self.tamanos_combos]
        for j, tam in enumerate(tamanos):
            datos = []
            for i in range(tam):
                texto = self.campos_vectores[j][i].text()
                if not texto:
                    raise ValueError(f"Falta un valor en el vector {j+1}, componente {i+1}.")
                try:
                    datos.append(float(texto))
                except ValueError:
                    raise ValueError(f"El valor '{texto}' en el vector {j+1}, componente {i+1} no es numérico.")
            vectores.append(datos)
        return vectores

    def ejecutar_operacion(self):
        self.resultado_texto.clear()
        oper = self.combo_oper.currentText()
        try:
            vectores = self.obtener_vectores()
            pasos = ""
            if oper == 'Suma':
                if not all(len(v) == len(vectores[0]) for v in vectores):
                    raise ValueError("Todos los vectores deben tener el mismo tamaño para la suma.")
                resultado = Vector(vectores[0])
                for v in vectores[1:]:
                    resultado = resultado.suma(Vector(v))
                pasos += "Suma de vectores:\n"
                for idx, v in enumerate(vectores):
                    pasos += f"Vector {idx+1}: {v}\n"
                pasos += f"\nResultado: {resultado.datos}"
                self.resultado_texto.setText(pasos)
            elif oper == 'Resta':
                if not all(len(v) == len(vectores[0]) for v in vectores):
                    raise ValueError("Todos los vectores deben tener el mismo tamaño para la resta.")
                resultado = Vector(vectores[0])
                for v in vectores[1:]:
                    resultado = resultado.resta(Vector(v))
                pasos += "Resta de vectores:\n"
                for idx, v in enumerate(vectores):
                    pasos += f"Vector {idx+1}: {v}\n"
                pasos += f"\nResultado: {resultado.datos}"
                self.resultado_texto.setText(pasos)
            elif oper == 'Multiplicación':
                if not all(len(v) == len(vectores[0]) for v in vectores):
                    raise ValueError("Todos los vectores deben tener el mismo tamaño para la multiplicación.")
                resultado = Vector(vectores[0])
                for v in vectores[1:]:
                    resultado = resultado.multiplicacion(Vector(v))
                pasos += "Multiplicación componente a componente:\n"
                for idx, v in enumerate(vectores):
                    pasos += f"Vector {idx+1}: {v}\n"
                pasos += f"\nResultado: {resultado.datos}"
                self.resultado_texto.setText(pasos)
            elif oper == 'Escalar':
                from PyQt6.QtWidgets import QInputDialog
                esc, ok = QInputDialog.getDouble(self, 'Escalar', 'Introduce el escalar:', 1.0)
                if not ok:
                    return
                resultado = Vector(vectores[0]).escalar(esc)
                pasos += f"Vector: {vectores[0]}\nEscalar: {esc}\n\n"
                pasos += f"Resultado: {resultado.datos}"
                self.resultado_texto.setText(pasos)
            elif oper == 'Eliminar coma y punto':
                resultado = Vector(vectores[0]).eliminar_coma_punto()
                pasos += f"Vector original: {vectores[0]}\n"
                pasos += f"Vector sin comas ni puntos: {resultado.datos}"
                self.resultado_texto.setText(pasos)
            elif oper == 'Solución Matriz de Vectores':
                pasos = solucionMatrizVector(vectores)
                self.resultado_texto.setText(pasos)
            elif oper == 'Dependencia/Independencia Lineal':
                pasos = dependencia_lineal_pasos(vectores)
                self.resultado_texto.setText(pasos)
        except Exception as e:
            QMessageBox.warning(self, 'Error', str(e))

    def ir_a_menu(self):
        try:
            from gui.MenuGui import MenuGui
            self.menu = MenuGui()
            self.menu.show()
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir MenuGui:\n{e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = VectoresGui()
    window.show()
    sys.exit(app.exec())