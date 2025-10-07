import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QFrame, QMessageBox
)
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt, QTimer

def resource_path(relative_path):
    """Devuelve la ruta correcta del recurso, incluso si está empaquetado con PyInstaller."""
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# ✅ Ruta al fondo dentro de gui/assets
FONDO_PATH = resource_path(os.path.join("assets", "Fondo1.jpg"))

class EntradaGui(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Álgebra Lineal - Bienvenida")
        self.setStyleSheet("background: #0d1b2a;")  # azul profundo elegante
        self.fondo = QLabel(self)
        self.fondo.setScaledContents(True)
        self.fondo_offset = 0
        self.fondo_direction = 1

        # Overlay principal
        self.overlay = QWidget(self)
        self.overlay.setStyleSheet("background: transparent;")
        self.main_layout = QVBoxLayout(self.overlay)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Título principal
        titulo = QLabel("<i><b>Álgebra Lineal</b></i>")
        titulo.setFont(QFont("Segoe UI", 48, QFont.Weight.Bold))
        titulo.setStyleSheet("color: #e0eafc;")  # azul claro elegante
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(titulo)

        # Subtítulo
        subtitulo = QLabel("<b>Integrantes</b>")
        subtitulo.setFont(QFont("Segoe UI", 34, QFont.Weight.Bold))
        subtitulo.setStyleSheet("color: #89b4fa;")  # azul tenue
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(subtitulo)

        # Marco para nombres
        self.frame_nombres = QFrame()
        self.frame_nombres.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 18px;
                border: 1.5px solid #1e6091;
            }
        """)
        self.frame_nombres.setFixedWidth(520)
        self.frame_nombres.setFixedHeight(260)
        self.frame_nombres.hide()

        vbox_nombres = QVBoxLayout(self.frame_nombres)
        vbox_nombres.setContentsMargins(30, 30, 30, 30)
        vbox_nombres.setSpacing(18)

        self.nombres = [
            "Allan Acuña",
            "Joshua Ordoñez",
            "Jan Paramo",
            "Guillermo Vega"
        ]
        self.labels_nombres = []
        for _ in self.nombres:
            lbl = QLabel("")
            lbl.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
            lbl.setStyleSheet("color: #d7e3fc; background: transparent; border: none;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            vbox_nombres.addWidget(lbl)
            self.labels_nombres.append(lbl)

        self.main_layout.addWidget(self.frame_nombres, alignment=Qt.AlignmentFlag.AlignCenter)

        # Botón principal "Bienvenido"
        self.btn_bienvenido = QPushButton("Bienvenido 🧮")
        self.btn_bienvenido.setFont(QFont("Segoe UI", 25, QFont.Weight.Bold))
        self.btn_bienvenido.setStyleSheet("""
            QPushButton {
                background-color: #1e6091;
                color: #f8f9fa;
                border-radius: 18px;
                border: 2px solid #1e6091;
                padding: 18px 60px;
                transition: all 0.3s ease;
            }
            QPushButton:hover {
                background-color: #184e77;
                border: 2px solid #52b2cf;
                color: #ffffff;
            }
            QPushButton:disabled {
                background-color: #3e4c5e;
                color: #a1a1a1;
                border: 2px solid #3e4c5e;
            }
        """)
        self.btn_bienvenido.setFixedWidth(350)
        self.btn_bienvenido.setFixedHeight(90)
        self.btn_bienvenido.clicked.connect(self.ir_a_menu)
        self.btn_bienvenido.setEnabled(False)
        self.main_layout.addWidget(self.btn_bienvenido, alignment=Qt.AlignmentFlag.AlignCenter)

        # Texto "Grupo" abajo derecha
        self.lbl_grupo = QLabel("Grupo 2")
        self.lbl_grupo.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        self.lbl_grupo.setStyleSheet("color: #304D73; background: transparent; border: none;")
        self.lbl_grupo.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.lbl_grupo.setParent(self.overlay)
        self.lbl_grupo.hide()

        # Timers
        self.nombre_idx = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.mostrar_siguiente_nombre)
        self.timer.start(800)

        self.fondo_timer = QTimer(self)
        self.fondo_timer.timeout.connect(self.animar_fondo)
        self.fondo_timer.start(40)

        self.showFullScreen()

    def showEvent(self, event):
        self._actualizar_fondo()
        self.overlay.setGeometry(0, 0, self.width(), self.height())
        self._posicionar_grupo()

    def _actualizar_fondo(self):
        pixmap = QPixmap(FONDO_PATH)
        if not pixmap or pixmap.isNull():
            self.fondo.setStyleSheet("background: #0d1b2a; color: white;")
            self.fondo.setText(f"No se pudo cargar la imagen de fondo.\nVerifica la ruta:\n{FONDO_PATH}")
            self.fondo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
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
        self._posicionar_grupo()

    def _posicionar_grupo(self):
        if hasattr(self, "lbl_grupo"):
            self.lbl_grupo.adjustSize()
            self.lbl_grupo.move(self.width() - self.lbl_grupo.width() - 20, self.height() - self.lbl_grupo.height() - 20)

    def animar_fondo(self):
        self.fondo_offset += self.fondo_direction * 1
        max_offset = 80
        if self.fondo_offset > max_offset or self.fondo_offset < 0:
            self.fondo_direction *= -1
        self._actualizar_fondo()

    def mostrar_siguiente_nombre(self):
        if self.nombre_idx < len(self.nombres):
            self.frame_nombres.show()
            self.labels_nombres[self.nombre_idx].setText(self.nombres[self.nombre_idx])
            self.nombre_idx += 1
            if self.nombre_idx == len(self.nombres):
                self.permitir_boton_despues_de_nombres()
        else:
            self.timer.stop()
            self.lbl_grupo.show()

    def permitir_boton_despues_de_nombres(self):
        QTimer.singleShot(3000, self._habilitar_boton)

    def _habilitar_boton(self):
        self.btn_bienvenido.setEnabled(True)

    def ir_a_menu(self):
        if not self.btn_bienvenido.isEnabled():
            return
        try:
            from MenuGui import MenuGui
            self.menu = MenuGui()
            self.menu.show()
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir MenuGui:\n{e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EntradaGui()
    window.show()
    sys.exit(app.exec())
