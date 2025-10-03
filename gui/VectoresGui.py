import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QTextEdit, QLineEdit, QMessageBox, QSizePolicy, QGridLayout
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from models.Vectores import Vector, solucionMatrizVector

class VectoresGui(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Álgebra Lineal - Operaciones con Vectores')
        self.showFullScreen()
        self.setStyleSheet("background: #23272e; color: #eee;")
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

        # Selección de cantidad de vectores
        barra_superior.addWidget(QLabel("Cantidad de vectores:"))
        self.combo_cant_vectores = QComboBox()
        self.combo_cant_vectores.addItems([str(i) for i in range(2, 6)])  # 2 a 5 vectores
        self.combo_cant_vectores.currentIndexChanged.connect(self.actualizar_tamanos_vectores)
        barra_superior.addWidget(self.combo_cant_vectores)
        self.layout.addLayout(barra_superior)

        # Layout para los combos de tamaño de cada vector
        self.tamanos_layout = QHBoxLayout()
        self.tamanos_labels = []
        self.tamanos_combos = []
        self.layout.addLayout(self.tamanos_layout)

        # Layout para los campos de entrada de los vectores
        self.vectores_grid = QGridLayout()
        self.layout.addLayout(self.vectores_grid)
        self.campos_vectores = []

        self.actualizar_tamanos_vectores()  # Inicializa los combos y campos

        # Layout para seleccionar la operación y botones
        oper_layout = QHBoxLayout()
        oper_layout.addWidget(QLabel('Operación:'))
        self.combo_oper = QComboBox()
        self.combo_oper.addItems([
            'Suma', 'Resta', 'Multiplicación', 'Escalar', 'Eliminar coma y punto', 'Solución Matriz de Vectores'
        ])
        oper_layout.addWidget(self.combo_oper)
        self.btn_ejecutar = QPushButton('Ejecutar')
        self.btn_ejecutar.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.btn_ejecutar.clicked.connect(self.ejecutar_operacion)
        oper_layout.addWidget(self.btn_ejecutar)
        self.btn_limpiar = QPushButton('Limpiar')
        self.btn_limpiar.setFont(QFont("Segoe UI", 14))
        self.btn_limpiar.clicked.connect(self.limpiar_campos)
        oper_layout.addWidget(self.btn_limpiar)
        self.layout.addLayout(oper_layout)

        # Área para mostrar la solución paso a paso
        self.resultado_label = QLabel('Solución paso a paso:')
        self.resultado_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.layout.addWidget(self.resultado_label)
        self.resultado_texto = QTextEdit()
        self.resultado_texto.setReadOnly(True)
        self.resultado_texto.setFont(QFont("Consolas", 16))
        self.resultado_texto.setFixedHeight(350)
        self.resultado_texto.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.layout.addWidget(self.resultado_texto)

    def limpiar_campos(self):
        for fila in self.campos_vectores:
            for campo in fila:
                campo.clear()
        self.resultado_texto.clear()

    def actualizar_tamanos_vectores(self):
        # Limpia los combos y etiquetas anteriores
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
            combo = QComboBox()
            combo.addItems([str(j) for j in range(1, 11)])  # 1 a 10 componentes
            combo.currentIndexChanged.connect(self.actualizar_campos_vectores)
            self.tamanos_layout.addWidget(lbl)
            self.tamanos_layout.addWidget(combo)
            self.tamanos_labels.append(lbl)
            self.tamanos_combos.append(combo)
        self.actualizar_campos_vectores()

    def actualizar_campos_vectores(self):
        # Limpia los campos anteriores
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
        # Etiquetas de columna (componentes)
        for i in range(max_tam):
            self.vectores_grid.addWidget(QLabel(f"x{i+1}"), 0, i+1, alignment=Qt.AlignmentFlag.AlignCenter)
        # Etiquetas de fila (vectores) y campos
        for j in range(cant):
            self.vectores_grid.addWidget(QLabel(f"<b>Vector {j+1}</b>"), j+1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
            fila_campos = []
            for i in range(max_tam):
                if i < tamanos[j]:
                    campo = QLineEdit()
                    campo.setFixedWidth(80)
                    campo.setFont(QFont("Segoe UI", 14))
                    self.vectores_grid.addWidget(campo, j+1, i+1)
                else:
                    campo = QLineEdit()
                    campo.setFixedWidth(80)
                    campo.setFont(QFont("Segoe UI", 14))
                    campo.setDisabled(True)
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