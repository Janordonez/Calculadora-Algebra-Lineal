import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QFrame, QMessageBox
)
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt, QTimer

FONDO_PATH = r"C:\Users\guill\Downloads\fondo calculadora.jpg"

class EntradaGui(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Álgebra Lineal - Bienvenida")
        self.setStyleSheet("background: #222;")
        self.fondo = QLabel(self)
        self.fondo.setScaledContents(True)
        self.fondo_offset = 0
        self.fondo_direction = 1

        # Overlay principal (layout vertical centrado)
        self.overlay = QWidget(self)
        self.overlay.setStyleSheet("background: transparent;")
        self.main_layout = QVBoxLayout(self.overlay)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Título y subtítulo
        titulo = QLabel("<i><b>Álgebra lineal</b></i>")
        titulo.setFont(QFont("Segoe UI", 48, QFont.Weight.Bold))
        titulo.setStyleSheet("color: white;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(titulo)

        subtitulo = QLabel("<b>Integrantes</b>")
        subtitulo.setFont(QFont("Segoe UI", 36, QFont.Weight.Bold))
        subtitulo.setStyleSheet("color: #ffe066;")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(subtitulo)

        # Recuadro para todos los nombres (solo uno, más sutil)
        self.frame_nombres = QFrame()
        self.frame_nombres.setStyleSheet("""
            QFrame {
                background: rgba(30, 30, 30, 0.5);
                border-radius: 18px;
                border: 1.5px solid #ffe066;
            }
        """)
        self.frame_nombres.setFixedWidth(500)
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
            lbl.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
            lbl.setStyleSheet("color: white; background: transparent; border: none;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            vbox_nombres.addWidget(lbl)
            self.labels_nombres.append(lbl)

        self.main_layout.addWidget(self.frame_nombres, alignment=Qt.AlignmentFlag.AlignCenter)

        # Botón Bienvenido con emoji de calculadora después del texto
        self.btn_bienvenido = QPushButton("Bienvenido 🧮")
        self.btn_bienvenido.setFont(QFont("Segoe UI", 25, QFont.Weight.Bold))
        self.btn_bienvenido.setStyleSheet("""
            QPushButton {
                background: #b0b0b0;
                color: #333;
                border-radius: 18px;
                border: 3px solid #888;
                padding: 18px 60px;
            }
            QPushButton:hover {
                background: #ffb347;
                color: #222;
            }
        """)
        self.btn_bienvenido.setFixedWidth(350)
        self.btn_bienvenido.setFixedHeight(90)
        self.btn_bienvenido.clicked.connect(self.ir_a_menu)
        self.btn_bienvenido.setEnabled(False)  # Deshabilitado al inicio
        self.main_layout.addWidget(self.btn_bienvenido, alignment=Qt.AlignmentFlag.AlignCenter)

        # "Grupo" abajo a la derecha (solo texto, sin fondo ni borde)
        self.lbl_grupo = QLabel("Grupo 2")
        self.lbl_grupo.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        self.lbl_grupo.setStyleSheet("color: white; background: transparent; border: none;")
        self.lbl_grupo.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.lbl_grupo.setParent(self.overlay)
        self.lbl_grupo.hide()

        # Timer para animar nombres
        self.nombre_idx = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.mostrar_siguiente_nombre)
        self.timer.start(800)  # 0.8 segundos entre nombres

        # Timer para fondo "live"
        self.fondo_timer = QTimer(self)
        self.fondo_timer.timeout.connect(self.animar_fondo)
        self.fondo_timer.start(40)  # 25 FPS

        self.showFullScreen()

    def showEvent(self, event):
        self._actualizar_fondo()
        self.overlay.setGeometry(0, 0, self.width(), self.height())
        self._posicionar_grupo()

    def _actualizar_fondo(self):
        pixmap = QPixmap(FONDO_PATH)
        if not pixmap or pixmap.isNull():
            self.fondo.setStyleSheet("background: #222; color: white;")
            self.fondo.setText(f"No se pudo cargar la imagen de fondo.\nVerifica la ruta:\n{FONDO_PATH}")
            self.fondo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            ancho = self.width() + 80  # Un poco más ancho para el efecto
            alto = self.height() + 80
            fondo_pixmap = pixmap.scaled(ancho, alto, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
            # Efecto de movimiento horizontal suave
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
        # Pone el label "Grupo" exactamente en la esquina inferior derecha
        if hasattr(self, "lbl_grupo"):
            self.lbl_grupo.adjustSize()
            self.lbl_grupo.move(self.width() - self.lbl_grupo.width(), self.height() - self.lbl_grupo.height())

    def animar_fondo(self):
        # Movimiento horizontal suave (parallax)
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
                # Cuando termina de mostrar todos, inicia el temporizador de 3 segundos
                self.permitir_boton_despues_de_nombres()
        else:
            self.timer.stop()
            self.lbl_grupo.show()  # Muestra "Grupo" al final

    def permitir_boton_despues_de_nombres(self):
        # Espera 3 segundos después de mostrar todos los nombres y habilita el botón
        QTimer.singleShot(3000, self._habilitar_boton)

    def _habilitar_boton(self):
        self.btn_bienvenido.setEnabled(True)

    def ir_a_menu(self):
        if not self.btn_bienvenido.isEnabled():
            return  # No hace nada si el botón no está habilitado
        try:
            # Si MenuGui.py está en la misma carpeta:
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