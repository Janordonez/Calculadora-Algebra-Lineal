from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QGridLayout, QTextEdit, QVBoxLayout, QHBoxLayout, QFrame, QGroupBox, QMessageBox
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
from combinacion_lineal import CombinacionLinealWindow

try:
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
    from matplotlib.figure import Figure
    from guiManager import guiManager
    HAS_MATRICES = True
except Exception as e:
    print("ERROR AL IMPORTAR MATRICES:", e)
    HAS_MATRICES = False

# --------- Ventana de Vectores ---------
class VectorWindow(QWidget):
    def __init__(self, volver_callback):
        super().__init__()
        self.volver_callback = volver_callback
        self.setWindowTitle("Calculadora de Vectores")
        self.setMinimumSize(600, 500)
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 #e8f0ff, stop:1 #ffffff
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
            QComboBox { padding: 6px; border-radius: 6px; }
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

        titulo = QLabel("🧮 Calculadora de Vectores")
        titulo.setFont(QFont("Arial", 18, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(titulo)

        main_layout.addSpacing(10)
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

        # Operación
        op_box = QGroupBox("Operación")
        op_layout = QHBoxLayout()
        op_box.setLayout(op_layout)
        self.combo_op = QComboBox()
        self.combo_op.addItems([
            "Suma (+) entre dos vectores",
            "Resta (-) entre dos vectores",
            "Multiplicación elemento a elemento (*)",
            "Vector por escalar"
        ])
        self.operar_btn = QPushButton("Calcular")
        self.operar_btn.clicked.connect(self.operar_vectores)
        self.operar_btn.setVisible(False)
        op_layout.addWidget(QLabel("Operación:"))
        op_layout.addWidget(self.combo_op)
        self.escalar_input = QLineEdit()
        self.escalar_input.setPlaceholderText("Escalar")
        self.escalar_input.setFixedWidth(80)
        self.escalar_input.setVisible(False)
        op_layout.addWidget(self.escalar_input)
        op_layout.addWidget(self.operar_btn)
        main_layout.addWidget(op_box)

        self.combo_op.currentIndexChanged.connect(self.mostrar_escalar)

        self.resultado = QTextEdit()
        self.resultado.setReadOnly(True)
        self.resultado.setFixedHeight(120)
        main_layout.addWidget(self.resultado)

    def mostrar_escalar(self):
        self.escalar_input.setVisible(self.combo_op.currentIndex() == 3)

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
        self.operar_btn.setVisible(True)
        self.resultado.clear()

    def operar_vectores(self):
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
            if len(vectores) < 2:
                self.resultado.setText("Se requieren al menos dos vectores.")
                return
            v1, v2 = vectores[0], vectores[1]
            n1, n2 = nombres[0], nombres[1]
            if len(v1) != len(v2):
                self.resultado.setText("Los vectores deben tener el mismo tamaño.")
                return
            op = self.combo_op.currentIndex()
            if op == 0:
                res = [v1[i] + v2[i] for i in range(len(v1))]
                texto = f"Suma de {n1} + {n2}:\n{res}"
            elif op == 1:
                res = [v1[i] - v2[i] for i in range(len(v1))]
                texto = f"Resta de {n1} - {n2}:\n{res}"
            elif op == 2:
                res = [v1[i] * v2[i] for i in range(len(v1))]
                texto = f"Multiplicación elemento a elemento {n1} * {n2}:\n{res}"
            elif op == 3:
                try:
                    escalar = float(self.escalar_input.text())
                except Exception:
                    self.resultado.setText("Ingrese un escalar válido.")
                    return
                res = [escalar * v for v in v1]
                texto = f"{escalar} × {n1}:\n{res}"
            else:
                texto = "Operación no soportada."
            self.resultado.setText(texto)
        except Exception:
            self.resultado.setText("Error en los datos de los vectores.")

    def volver_a_menu(self):
        self.close()
        self.volver_callback()

# --------- Ventana de Matrices ---------
if HAS_MATRICES:
    class GraphCanvas(FigureCanvas):
        def __init__(self, parent=None, width=5, height=4, dpi=100):
            self.figure = Figure(figsize=(width, height), dpi=dpi)
            self.axes = self.figure.add_subplot(111)
            super().__init__(self.figure)
            self.setParent(parent)

    class MatrixWindow(QWidget):
        def __init__(self, volver_callback):
            super().__init__()
            self.volver_callback = volver_callback
            self.setWindowTitle("Calculadora de Ecuaciones Lineales — Visual")
            self.setMinimumSize(1000, 700)
            self.setStyleSheet("""
                QWidget {
                    background: qlineargradient(
                        spread:pad, x1:0, y1:0, x2:1, y2:1,
                        stop:0 #e8f0ff, stop:1 #ffffff
                    );
                    font-family: Segoe UI, Arial;
                }
                QLabel { font-size: 14px; font-weight: bold; color: #2c3e50; }
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
                QGroupBox { font-size: 14px; font-weight: bold; color: #2c3e50; border: 1px solid #bbb; border-radius: 8px; margin-top: 10px; }
                QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
            """)

            layoutPrincipal = QVBoxLayout(self)

            barra = QHBoxLayout()
            btn_home = QPushButton("🏠")
            btn_home.setObjectName("homeBtn")
            btn_home.setFixedSize(48, 48)
            btn_home.clicked.connect(self.volver_a_menu)
            barra.addWidget(btn_home, alignment=Qt.AlignLeft)
            barra.addStretch()
            layoutPrincipal.addLayout(barra)

            logo_path = "calculadora-cientifica.png"
            if os.path.exists(logo_path):
                logo = QLabel()
                pixmap = QPixmap(logo_path).scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                logo.setPixmap(pixmap)
                logo.setAlignment(Qt.AlignCenter)
                layoutPrincipal.addWidget(logo)
            else:
                logo = QLabel("🧮")
                logo.setFont(QFont("Arial", 48))
                logo.setAlignment(Qt.AlignCenter)
                layoutPrincipal.addWidget(logo)

            titulo = QLabel("🔢 Calculadora de Sistemas de Ecuaciones Lineales (con gráfico)")
            titulo.setFont(QFont("Arial", 18, QFont.Bold))
            titulo.setAlignment(Qt.AlignCenter)
            layoutPrincipal.addWidget(titulo)

            separador = QFrame()
            separador.setFrameShape(QFrame.HLine)
            separador.setFrameShadow(QFrame.Sunken)
            layoutPrincipal.addWidget(separador)

            entradaLayout = QHBoxLayout()
            self.entradaFilas = QLineEdit()
            self.entradaFilas.setPlaceholderText("Número de filas (ej: 3)")
            self.entradaColumnas = QLineEdit()
            self.entradaColumnas.setPlaceholderText("Número de columnas (ej: 3)")
            entradaLayout.addWidget(QLabel("Filas:"))
            entradaLayout.addWidget(self.entradaFilas)
            entradaLayout.addSpacing(20)
            entradaLayout.addWidget(QLabel("Columnas:"))
            entradaLayout.addWidget(self.entradaColumnas)
            layoutPrincipal.addLayout(entradaLayout)

            botonesLayout = QHBoxLayout()
            self.botonGenerar = QPushButton("➕ Generar Matriz")
            self.botonResolver = QPushButton("✅ Resolver y Analizar")
            self.botonResolver.hide()
            botonesLayout.addStretch()
            botonesLayout.addWidget(self.botonGenerar)
            botonesLayout.addWidget(self.botonResolver)
            botonesLayout.addStretch()
            layoutPrincipal.addLayout(botonesLayout)

            grupoMatriz = QGroupBox("📐 Matriz del sistema (última columna = términos independientes)")
            self.layoutCentral = QGridLayout()
            grupoMatriz.setLayout(self.layoutCentral)
            layoutPrincipal.addWidget(grupoMatriz)

            layoutPrincipal.addWidget(QLabel("📄 Resultados:"))
            self.texto = QTextEdit()
            self.texto.setReadOnly(True)
            self.texto.setFixedHeight(200)
            layoutPrincipal.addWidget(self.texto)

            layoutPrincipal.addWidget(QLabel("📊 Gráfico:"))
            self.grafico = GraphCanvas()
            toolbar = NavigationToolbar(self.grafico, self)
            layoutPrincipal.addWidget(toolbar)
            layoutPrincipal.addWidget(self.grafico, stretch=1)

            self.Manager = guiManager(
                self.entradaFilas, self.entradaColumnas, self.layoutCentral,
                self.botonResolver, self.texto, self.grafico
            )

            self.botonGenerar.clicked.connect(self.validar_y_crear)
            self.botonResolver.clicked.connect(self.Manager.resolverMatriz)

        def validar_y_crear(self):
            try:
                filas = int(self.entradaFilas.text())
                columnas = int(self.entradaColumnas.text())
                if filas < 1 or columnas < 2:
                    raise ValueError
            except Exception:
                QMessageBox.warning(self, "Error", "Ingrese un número válido de filas y columnas (mínimo 1 fila, 2 columnas).")
                return
            self.Manager.crearMatriz()
            self.botonResolver.show()

        def volver_a_menu(self):
            self.close()
            self.volver_callback()

# --------- Menú Principal ---------
class MenuPrincipal(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculadora Álgebra Lineal")
        self.setMinimumSize(440, 350)
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 #dbeafe, stop:1 #f0f9ff
                );
                font-family: Segoe UI, Arial;
            }
            QLabel { font-size: 16px; font-weight: bold; color: #2c3e50; }
            QPushButton {
                background-color: #2563eb; color: white; padding: 14px 0px; border-radius: 12px;
                font-size: 16px; font-weight: bold;
            }
            QPushButton:hover { background-color: #1e40af; }
        """)
        layout = QVBoxLayout()
        logo_path = "calculadora-cientifica.png"
        if os.path.exists(logo_path):
            logo = QLabel()
            pixmap = QPixmap(logo_path).scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo.setPixmap(pixmap)
            logo.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo)
        else:
            logo = QLabel("🧮")
            logo.setFont(QFont("Arial", 48))
            logo.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo)

        titulo = QLabel("Calculadora de Álgebra Lineal")
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        layout.addSpacing(20)

        btn_matrices = QPushButton("Matrices")
        btn_vectores = QPushButton("Vectores")
        btn_combinacion = QPushButton("Combinación Lineal")
        btn_matrices.setFixedHeight(55)
        btn_vectores.setFixedHeight(55)
        btn_combinacion.setFixedHeight(55)
        btn_matrices.setFont(QFont("Arial", 15))
        btn_vectores.setFont(QFont("Arial", 15))
        btn_combinacion.setFont(QFont("Arial", 15))

        btn_matrices.clicked.connect(self.abrir_matrices)
        btn_vectores.clicked.connect(self.abrir_vectores)
        btn_combinacion.clicked.connect(self.abrir_combinacion)

        layout.addWidget(btn_matrices)
        layout.addWidget(btn_vectores)
        layout.addWidget(btn_combinacion)
        layout.addStretch()
        self.setLayout(layout)

    def abrir_matrices(self):
        self.hide()
        if HAS_MATRICES:
            self.matriz_win = MatrixWindow(self.mostrar)
            self.matriz_win.showMaximized()
        else:
            QMessageBox.warning(self, "No disponible", "La interfaz de matrices no está disponible.")
            self.show()

    def abrir_vectores(self):
        self.hide()
        self.vec_win = VectorWindow(self.mostrar)
        self.vec_win.showMaximized()

    def abrir_combinacion(self):
        self.hide()
        self.comb_win = CombinacionLinealWindow(self.mostrar)
        self.comb_win.showMaximized()

    def mostrar(self):
        self.showMaximized()

def main():
    app = QApplication([])
    menu = MenuPrincipal()
    menu.showMaximized()
    app.exec_()

if __name__ == "__main__":
    main()