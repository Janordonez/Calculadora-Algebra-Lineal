from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QTextEdit,
    QVBoxLayout, QHBoxLayout, QGroupBox, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class CombinacionLinealWindow(QWidget):
    def __init__(self, volver_callback):
        super().__init__()
        self.volver_callback = volver_callback
        self.setWindowTitle("Combinación Lineal de Vectores")
        self.setMinimumSize(700, 600)
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f1f5f9, stop:1 #e0e7ef
                );
                font-family: Segoe UI, Arial;
            }
            QLabel { font-size: 15px; font-weight: bold; color: #2c3e50; }
            QLineEdit { padding: 6px; border: 1px solid #bbb; border-radius: 6px; background-color: #fff; }
            QPushButton {
                background-color: #2e86de; color: white; padding: 10px 16px; border-radius: 8px;
                font-size: 13px; font-weight: bold;
            }
            QPushButton#homeBtn {
                background: transparent;
                color: #2563eb;
                font-size: 28px;
                border: none;
                padding: 0;
            }
            QPushButton#homeBtn:hover {
                background: #e0e7ef;
            }
            QPushButton:hover { background-color: #1f6fb1; }
            QTextEdit { border: 1px solid #ccc; border-radius: 6px; padding: 8px; background-color: #fff; font-size: 13px; }
        """)

        main_layout = QVBoxLayout(self)
        barra = QHBoxLayout()
        btn_home = QPushButton("🏠")
        btn_home.setObjectName("homeBtn")
        btn_home.setFixedSize(48, 48)
        btn_home.clicked.connect(self.volver_a_menu)
        barra.addWidget(btn_home, alignment=Qt.AlignLeft)
        barra.addStretch()
        main_layout.addLayout(barra)

        titulo = QLabel("Combinación Lineal de Vectores")
        titulo.setFont(QFont("Arial", 18, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(titulo)

        datos_box = QGroupBox("Datos de los vectores")
        datos_layout = QHBoxLayout()
        datos_box.setLayout(datos_layout)
        self.tam_input = QLineEdit()
        self.tam_input.setPlaceholderText("Tamaño")
        self.tam_input.setFixedWidth(60)
        self.cant_input = QLineEdit()
        self.cant_input.setPlaceholderText("Cantidad")
        self.cant_input.setFixedWidth(60)
        self.gen_btn = QPushButton("Ingresar vectores")
        self.gen_btn.clicked.connect(self.generar_campos)
        datos_layout.addWidget(QLabel("Tamaño:"))
        datos_layout.addWidget(self.tam_input)
        datos_layout.addSpacing(10)
        datos_layout.addWidget(QLabel("Cantidad:"))
        datos_layout.addWidget(self.cant_input)
        datos_layout.addWidget(self.gen_btn)
        main_layout.addWidget(datos_box)

        self.campos_widget = QWidget()
        self.campos_layout = QVBoxLayout()
        self.campos_widget.setLayout(self.campos_layout)
        main_layout.addWidget(self.campos_widget)
        self.vectores_inputs = []
        self.nombres_inputs = []

        # Coeficientes
        coef_box = QGroupBox("Coeficientes para la combinación lineal")
        coef_layout = QHBoxLayout()
        coef_box.setLayout(coef_layout)
        self.coef_inputs = []
        self.coef_labels = []
        main_layout.addWidget(coef_box)
        self.coef_box = coef_box
        self.coef_layout = coef_layout

        self.calcular_btn = QPushButton("Calcular combinación lineal")
        self.calcular_btn.clicked.connect(self.calcular_combinacion)
        self.calcular_btn.setVisible(False)
        main_layout.addWidget(self.calcular_btn)

        self.resultado = QTextEdit()
        self.resultado.setReadOnly(True)
        self.resultado.setFixedHeight(220)
        main_layout.addWidget(self.resultado)

    def generar_campos(self):
        try:
            tam = int(self.tam_input.text())
            cant = int(self.cant_input.text())
            if tam < 1 or cant < 2:
                raise ValueError
        except Exception:
            QMessageBox.warning(self, "Error", "Ingrese valores válidos (mínimo 2 vectores, tamaño > 0).")
            return
        for i in reversed(range(self.campos_layout.count())):
            self.campos_layout.itemAt(i).widget().setParent(None)
        self.vectores_inputs = []
        self.nombres_inputs = []
        for i in range(cant):
            fila = QHBoxLayout()
            nombre_input = QLineEdit()
            nombre_input.setPlaceholderText(f"Nombre {i+1}")
            nombre_input.setFixedWidth(50)
            self.nombres_inputs.append(nombre_input)
            fila.addWidget(QLabel("Nombre:"))
            fila.addWidget(nombre_input)
            fila_label = QLabel(f"Vector {i+1}:")
            fila.addWidget(fila_label)
            entradas = []
            for j in range(tam):
                e = QLineEdit()
                e.setFixedWidth(40)
                fila.addWidget(e)
                entradas.append(e)
            self.vectores_inputs.append(entradas)
            fila_widget = QWidget()
            fila_widget.setLayout(fila)
            self.campos_layout.addWidget(fila_widget)
        # Coeficientes
        for i in reversed(range(self.coef_layout.count())):
            self.coef_layout.itemAt(i).widget().setParent(None)
        self.coef_inputs = []
        self.coef_labels = []
        for i in range(cant):
            coef = QLineEdit()
            coef.setPlaceholderText(f"Coef.")
            coef.setFixedWidth(60)
            label = QLabel(f"?")
            self.coef_labels.append(label)
            self.coef_layout.addWidget(label)
            self.coef_layout.addWidget(coef)
            self.coef_inputs.append(coef)
        self.calcular_btn.setVisible(True)
        self.resultado.clear()

    def calcular_combinacion(self):
        try:
            vectores = []
            nombres = []
            for nombre_input in self.nombres_inputs:
                nombre = nombre_input.text().strip()
                if not nombre:
                    nombres.append("?")
                else:
                    nombres.append(nombre)
            for entradas in self.vectores_inputs:
                vec = [float(e.text()) for e in entradas]
                vectores.append(vec)
            coefs = [float(c.text()) for c in self.coef_inputs]
            if any(len(vec) != len(vectores[0]) for vec in vectores):
                self.resultado.setText("Todos los vectores deben tener el mismo tamaño.")
                return
            # Actualiza etiquetas de coeficientes con nombres
            for i, label in enumerate(self.coef_labels):
                label.setText(f"{nombres[i]}:")
            paso_a_paso = ""
            tam = len(vectores[0])
            # Mostrar cada multiplicación
            for i in range(len(vectores)):
                paso_a_paso += f"{coefs[i]} × {nombres[i]} = ["
                paso_a_paso += ", ".join(f"{coefs[i]*vectores[i][j]:.2f}" for j in range(tam))
                paso_a_paso += "]\n"
            # Mostrar suma paso a paso
            suma_parcial = [0.0 for _ in range(tam)]
            for j in range(tam):
                suma_str = " + ".join(f"{coefs[i]*vectores[i][j]:.2f}" for i in range(len(vectores)))
                suma_val = sum(coefs[i]*vectores[i][j] for i in range(len(vectores)))
                paso_a_paso += f"Componente {j+1}: {suma_str} = {suma_val:.2f}\n"
                suma_parcial[j] = suma_val
            paso_a_paso += f"\nResultado final: {suma_parcial}"
            self.resultado.setText(paso_a_paso)
        except Exception:
            self.resultado.setText("Error en los datos de los vectores o coeficientes.")

    def volver_a_menu(self):
        self.close()
        self.volver_callback()