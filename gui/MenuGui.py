from gui.MatricesGui import MatricesGui
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QMessageBox,
    QGraphicsDropShadowEffect
)
from PyQt6.QtGui import QPixmap, QFont, QColor
from PyQt6.QtCore import Qt, QTimer, QTime, QDate
import os
import sys

def resource_path(relative_path):
    """Devuelve la ruta correcta del recurso, incluso si está empaquetado con PyInstaller."""
    if hasattr(sys, "_MEIPASS"):
        # Si está empaquetado con PyInstaller
        base_path = sys._MEIPASS
    else:
        # Carpeta actual (gui/)
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# ✅ Ruta al fondo dentro de gui/assets
FONDO_PATH = resource_path(os.path.join("assets", "Fondo1.jpg"))

class MenuGui(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculadora")
        self.setStyleSheet("""
            QWidget {
                background-color: #0b1220;
                color: #e6eef6;
                font-family: 'Segoe UI', 'Inter', 'Arial';
            }

            QLabel#titulo {
                color: #f8fafc;
                font-size: 52px;
                font-weight: 800;
            }

            QLabel.info {
                color: #cfe7fb;
                font-weight: 600;
            }

            /* === BOTONES REALES CON COLOR RELLENO === */
            QPushButton {
                background-color: #325475;
                color: #ffffff; /* Texto blanco para mejor contraste */
                border-radius: 22px;
                border: 2px solid #325475;
                padding: 20px 80px;
                font-size: 28px;
                font-weight: 700;
                transition: all 0.2s ease-in-out;
            }

            QPushButton:hover {
                background-color: #3b6b9a;
                border: 2px solid #4a89c7;
                transform: scale(1.03);
            }

            QPushButton:pressed {
                background-color: #27425c;
                border: 2px solid #1e2f44;
                transform: scale(0.98);
            }
        """)

        # Fondo animado
        self.fondo = QLabel(self)
        self.fondo.setScaledContents(True)
        self.fondo_offset = 0
        self.fondo_direction = 1

        # Overlay semitransparente
        self.overlay = QLabel(self)
        self.overlay.setStyleSheet("background: rgba(11,18,32,0.6);")
        self.overlay.setGeometry(0, 0, self.width(), self.height())

        # Layout principal
        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.setContentsMargins(40, 80, 40, 80)
        self.main_layout.setSpacing(32)

        self.container = QWidget(self.overlay)
        self.container.setLayout(self.main_layout)
        self.container.setStyleSheet("background: transparent;")

        # Título
        titulo = QLabel("Calculadora", self.container)
        titulo.setObjectName("titulo")
        titulo.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.main_layout.addWidget(titulo)

        # Botones
        btn_layout = QVBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        btn_layout.setSpacing(28)

        f_btn = QFont("Segoe UI", 20, QFont.Weight.Bold)

        self.btn_matrices = QPushButton("Matrices  ➔", self.container)
        self.btn_matrices.setFont(f_btn)
        self.btn_matrices.setFixedWidth(460)
        self.btn_matrices.clicked.connect(self.abrir_matrices)
        btn_layout.addWidget(self.btn_matrices, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.btn_vectores = QPushButton("Vectores  ➔", self.container)
        self.btn_vectores.setFont(f_btn)
        self.btn_vectores.setFixedWidth(460)
        self.btn_vectores.clicked.connect(self.abrir_vectores)
        btn_layout.addWidget(self.btn_vectores, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.btn_salir = QPushButton("Salir", self.container)
        f_btn_small = QFont("Segoe UI", 18, QFont.Weight.Bold)
        self.btn_salir.setFont(f_btn_small)
        self.btn_salir.setFixedWidth(340)
        self.btn_salir.clicked.connect(self.cerrar_programa)
        btn_layout.addWidget(self.btn_salir, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.main_layout.addLayout(btn_layout)

        # Info: hora, fecha, versión, grupo
        self.lbl_fecha = QLabel("", self.overlay)
        self.lbl_fecha.setProperty("class", "info")
        self.lbl_fecha.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.lbl_hora = QLabel("", self.overlay)
        self.lbl_hora.setProperty("class", "info")
        self.lbl_hora.setStyleSheet("color: #38bdf8;")
        self.lbl_hora.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.lbl_version = QLabel("V.0.0.4", self.overlay)
        self.lbl_version.setProperty("class", "info")

        self.lbl_grupo = QLabel("<i>GROUP 2</i>", self.overlay)
        self.lbl_grupo.setProperty("class", "info")
        self.lbl_grupo.setStyleSheet("color: #38bdf8; background: transparent; border: none;")
        self.lbl_grupo.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Sombra en botones
        for btn in [self.btn_matrices, self.btn_vectores, self.btn_salir]:
            sombra = QGraphicsDropShadowEffect()
            sombra.setBlurRadius(25)
            sombra.setOffset(0, 6)
            sombra.setColor(QColor(0, 0, 0, 160))
            btn.setGraphicsEffect(sombra)

        # Timers
        self.fondo_timer = QTimer(self)
        self.fondo_timer.timeout.connect(self.animar_fondo)
        self.fondo_timer.start(40)

        self.hora_timer = QTimer(self)
        self.hora_timer.timeout.connect(self.actualizar_hora_fecha)
        self.hora_timer.start(1000)
        self.actualizar_hora_fecha()

        self.showFullScreen()

    def showEvent(self, _):
        self._actualizar_fondo()
        self.overlay.setGeometry(0, 0, self.width(), self.height())
        self.container.setGeometry(0, 0, self.width(), self.height())
        self._posicionar_esquinas()

    def _actualizar_fondo(self):
        if not os.path.exists(FONDO_PATH):
            self.fondo.setStyleSheet("background: #0b1220; color: #e6eef6;")
            self.fondo.setText(f"No se pudo cargar la imagen de fondo.\nVerifica la ruta:\n{FONDO_PATH}")
            self.fondo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            pixmap = QPixmap(FONDO_PATH)
            ancho = max(1, self.width() + 120)
            alto = max(1, self.height() + 120)
            fondo_pixmap = pixmap.scaled(ancho, alto, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
            x_offset = int(self.fondo_offset)
            y_offset = int(self.fondo_offset // 3)
            x_offset = max(0, min(x_offset, max(0, fondo_pixmap.width() - self.width())))
            y_offset = max(0, min(y_offset, max(0, fondo_pixmap.height() - self.height())))
            cropped = fondo_pixmap.copy(x_offset, y_offset, self.width(), self.height())
            self.fondo.setPixmap(cropped)
            self.fondo.setText("")
        self.fondo.setGeometry(0, 0, self.width(), self.height())

    def resizeEvent(self, _):
        if hasattr(self, "fondo"):
            self._actualizar_fondo()
        if hasattr(self, "overlay"):
            self.overlay.setGeometry(0, 0, self.width(), self.height())
            self.container.setGeometry(0, 0, self.width(), self.height())
        self._posicionar_esquinas()

    def _posicionar_esquinas(self):
        self.lbl_version.adjustSize()
        self.lbl_version.move(12, self.height() - self.lbl_version.height() - 12)
        self.lbl_fecha.adjustSize()
        self.lbl_fecha.move(self.width() - self.lbl_fecha.width() - 28, 18)
        self.lbl_grupo.adjustSize()
        self.lbl_grupo.move(self.width() - self.lbl_grupo.width() - 28, self.height() - self.lbl_grupo.height() - 12)
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
            from gui.MatricesGui import MatricesGui
            self.matrices = MatricesGui()
            self.matrices.show()
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir MatricesGui:\n{e}")

    def abrir_vectores(self):
        try:
            from gui.VectoresGui import VectoresGui
            self.vectores = VectoresGui()
            self.vectores.show()
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir VectoresGui:\n{e}")

    def cerrar_programa(self):
        QApplication.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MenuGui()
    window.show()
    sys.exit(app.exec())