import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
)
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt, QTimer, QTime, QDate

FONDO_PATH = r"C:\Users\guill\Downloads\Fondo.jpg"

class MenuGui(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculadora")
        self.setStyleSheet("background: #222;")
        self.fondo = QLabel(self)
        self.fondo.setScaledContents(True)
        self.fondo_offset = 0
        self.fondo_direction = 1

        # Overlay principal
        self.overlay = QWidget(self)
        self.overlay.setStyleSheet("background: transparent;")
        self.overlay.setGeometry(0, 0, self.width(), self.height())

        # Layout principal
        self.main_layout = QVBoxLayout(self.overlay)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.setContentsMargins(0, 80, 0, 80)
        self.main_layout.setSpacing(30)

        # Título
        titulo = QLabel("<i><b>Calculadora</b></i>")
        titulo.setFont(QFont("Segoe UI", 56, QFont.Weight.Bold))
        titulo.setStyleSheet("color: white;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.main_layout.addWidget(titulo)

        # Botones centrados
        btn_layout = QVBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        btn_layout.setSpacing(35)

        self.btn_matrices = QPushButton("Matrices  ➔")
        self.btn_matrices.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        self.btn_matrices.setStyleSheet("""
            QPushButton {
                background: #f3f3f3;
                color: #222;
                border-radius: 28px;
                border: none;
                padding: 22px 80px;
            }
            QPushButton:hover {
                background: #ffe066;
                color: #222;
            }
        """)
        self.btn_matrices.setFixedWidth(420)
        self.btn_matrices.clicked.connect(self.abrir_matrices)
        btn_layout.addWidget(self.btn_matrices, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.btn_vectores = QPushButton("Vectores  ➔")
        self.btn_vectores.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        self.btn_vectores.setStyleSheet("""
            QPushButton {
                background: #f3f3f3;
                color: #222;
                border-radius: 28px;
                border: none;
                padding: 22px 80px;
            }
            QPushButton:hover {
                background: #ffe066;
                color: #222;
            }
        """)
        self.btn_vectores.setFixedWidth(420)
        self.btn_vectores.clicked.connect(self.abrir_vectores)
        btn_layout.addWidget(self.btn_vectores, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.btn_salir = QPushButton("Salir")
        self.btn_salir.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        self.btn_salir.setStyleSheet("""
            QPushButton {
                background: #e57373;
                color: #fff;
                border-radius: 24px;
                border: none;
                padding: 16px 60px;
            }
            QPushButton:hover {
                background: #b71c1c;
                color: #fff;
            }
        """)
        self.btn_salir.setFixedWidth(320)
        self.btn_salir.clicked.connect(self.cerrar_programa)
        btn_layout.addWidget(self.btn_salir, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.main_layout.addLayout(btn_layout)

        # Fecha arriba a la derecha
        self.lbl_fecha = QLabel("")
        self.lbl_fecha.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        self.lbl_fecha.setStyleSheet("color: white;")
        self.lbl_fecha.setParent(self.overlay)
        self.lbl_fecha.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Hora abajo centrada
        self.lbl_hora = QLabel("")
        self.lbl_hora.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        self.lbl_hora.setStyleSheet("color: #ffe066;")
        self.lbl_hora.setParent(self.overlay)
        self.lbl_hora.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # Versión abajo a la izquierda
        self.lbl_version = QLabel("V.0.0.4")
        self.lbl_version.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.lbl_version.setStyleSheet("color: white;")
        self.lbl_version.setParent(self.overlay)

        # Grupo abajo a la derecha
        self.lbl_grupo = QLabel("<i>GROUP 2</i>")
        self.lbl_grupo.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        self.lbl_grupo.setStyleSheet("color: #ffe066; background: transparent; border: none;")
        self.lbl_grupo.setParent(self.overlay)
        self.lbl_grupo.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Timers
        self.fondo_timer = QTimer(self)
        self.fondo_timer.timeout.connect(self.animar_fondo)
        self.fondo_timer.start(40)  # 25 FPS

        self.hora_timer = QTimer(self)
        self.hora_timer.timeout.connect(self.actualizar_hora_fecha)
        self.hora_timer.start(1000)
        self.actualizar_hora_fecha()

        self.showFullScreen()

    def showEvent(self, event):
        self._actualizar_fondo()
        self.overlay.setGeometry(0, 0, self.width(), self.height())
        self._posicionar_esquinas()

    def _actualizar_fondo(self):
        if not os.path.exists(FONDO_PATH):
            self.fondo.setStyleSheet("background: #222; color: white;")
            self.fondo.setText(f"No se pudo cargar la imagen de fondo.\nVerifica la ruta:\n{FONDO_PATH}")
            self.fondo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            pixmap = QPixmap(FONDO_PATH)
            ancho = self.width() + 80
            alto = self.height() + 80
            fondo_pixmap = pixmap.scaled(ancho, alto, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
            x_offset = self.fondo_offset
            y_offset = self.fondo_offset // 3
            self.fondo.setPixmap(fondo_pixmap.copy(
                max(0, x_offset), max(0, y_offset),
                self.width(), self.height()
            ))
            self.fondo.setText("")
        self.fondo.setGeometry(0, 0, self.width(), self.height())

    def resizeEvent(self, event):
        if hasattr(self, "fondo"):
            self._actualizar_fondo()
        if hasattr(self, "overlay"):
            self.overlay.setGeometry(0, 0, self.width(), self.height())
        self._posicionar_esquinas()

    def _posicionar_esquinas(self):
        # Versión abajo a la izquierda
        self.lbl_version.adjustSize()
        self.lbl_version.move(10, self.height() - self.lbl_version.height() - 10)
        # Fecha arriba a la derecha
        self.lbl_fecha.adjustSize()
        self.lbl_fecha.move(self.width() - self.lbl_fecha.width() - 30, 20)
        # Grupo abajo a la derecha
        self.lbl_grupo.adjustSize()
        self.lbl_grupo.move(self.width() - self.lbl_grupo.width() - 30, self.height() - self.lbl_grupo.height() - 10)
        # Hora abajo centrada
        self.lbl_hora.adjustSize()
        self.lbl_hora.move((self.width() - self.lbl_hora.width()) // 2, self.height() - self.lbl_hora.height() - 18)

    def animar_fondo(self):
        self.fondo_offset += self.fondo_direction * 1
        max_offset = 80
        if self.fondo_offset > max_offset or self.fondo_offset < 0:
            self.fondo_direction *= -1
        self._actualizar_fondo()

    def actualizar_hora_fecha(self):
        hora = QTime.currentTime().toString("hh:mm:ss")
        fecha = QDate.currentDate().toString("dd/MM/yyyy")
        self.lbl_fecha.setText(f"<b>Fecha:</b> {fecha}")
        self.lbl_hora.setText(f"<b>Hora:</b> {hora}")

    def abrir_matrices(self):
        try:
            sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
            from MatricesGui import MatricesGui
            self.matrices = MatricesGui()
            self.matrices.show()
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir MatricesGui:\n{e}")

    def abrir_vectores(self):
        try:
            sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
            from VectoresGui import VectoresGui
            self.vectores = VectoresGui()
            self.vectores.show()
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir VectoresGui:\n{e}")

    def cerrar_programa(self):
        QApplication.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MenuGui()
    window.show()
    sys.exit(app.exec())