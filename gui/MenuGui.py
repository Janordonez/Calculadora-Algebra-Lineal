from gui.MatricesGui import MatricesGui
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox,
    QGraphicsDropShadowEffect
)
from PyQt6.QtGui import QPixmap, QFont, QColor
from PyQt6.QtCore import Qt, QTimer, QTime, QDate
import os
import sys

# Ruta a la imagen de fondo (mantén la tuya)
FONDO_PATH = r"C:\Users\guill\Downloads\Fondo.jpg"

class MenuGui(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculadora")
        # Estilo general coherente con MatricesGui (tema "midnight blue minimal")
        self.setStyleSheet("""
            QWidget {
                background-color: #0b1220;
                color: #e6eef6;
                font-family: 'Segoe UI', 'Inter', 'Arial';
                font-size: 14px;
            }
            QLabel#titulo {
                color: #f8fafc;
                font-size: 48px;
                font-weight: 800;
            }
            QLabel.info {
                color: #cfe7fb;
                font-weight: 600;
            }
            QPushButton.primary {
                background-color: #1e3a8a;
                color: #f8fafc;
                border-radius: 18px;
                padding: 18px 72px;
                border: 1px solid #3b82f6;
                font-size: 26px;
                font-weight: 700;
            }
            QPushButton.primary:hover {
                background-color: #3b82f6;
            }
            QPushButton.secondary {
                background-color: #153246;
                color: #e6eef6;
                border-radius: 16px;
                padding: 12px 48px;
                border: 1px solid #2a4a63;
                font-size: 22px;
                font-weight: 700;
            }
            QPushButton.secondary:hover {
                background-color: #2a4a63;
            }
            QPushButton.danger {
                background-color: #b91c1c;
                color: #fff;
                border-radius: 16px;
                padding: 12px 40px;
                font-size: 22px;
                font-weight: 700;
                border: none;
            }
            QPushButton.danger:hover {
                background-color: #7f1414;
            }
        """)

        # Fondo (imagen)
        self.fondo = QLabel(self)
        self.fondo.setScaledContents(True)
        self.fondo_offset = 0
        self.fondo_direction = 1

        # Overlay oscuro semitransparente para legibilidad (estético y minimal)
        self.overlay = QLabel(self)
        self.overlay.setStyleSheet("background: rgba(11,18,32,0.55);")  # sutil, deja ver imagen
        self.overlay.setGeometry(0, 0, self.width(), self.height())

        # Layout principal (sobre el overlay)
        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.setContentsMargins(40, 80, 40, 80)
        self.main_layout.setSpacing(28)

        # Contenedor central (widget transparente para colocar el layout)
        self.container = QWidget(self.overlay)
        self.container.setLayout(self.main_layout)
        self.container.setContentsMargins(0, 0, 0, 0)
        self.container.setStyleSheet("background: transparent;")

        # Título grande y elegante
        titulo = QLabel("Calculadora", self.container)
        titulo.setObjectName("titulo")
        titulo.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.main_layout.addWidget(titulo)

        # Botones (centrados)
        btn_layout = QVBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        btn_layout.setSpacing(26)

        self.btn_matrices = QPushButton("Matrices  ➔", self.container)
        self.btn_matrices.setObjectName("btn_matrices")
        self.btn_matrices.setProperty("class", "primary")
        self.btn_matrices.setStyleSheet("")  # use stylesheet above via object/class
        # Ajuste de fuente (asegura consistencia)
        f_btn = QFont("Segoe UI", 20)
        f_btn.setBold(True)
        self.btn_matrices.setFont(f_btn)
        self.btn_matrices.setFixedWidth(460)
        self.btn_matrices.clicked.connect(self.abrir_matrices)
        self.btn_matrices.setProperty("class", "primary")
        btn_layout.addWidget(self.btn_matrices, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.btn_vectores = QPushButton("Vectores  ➔", self.container)
        self.btn_vectores.setFont(f_btn)
        self.btn_vectores.setFixedWidth(460)
        self.btn_vectores.clicked.connect(self.abrir_vectores)
        self.btn_vectores.setProperty("class", "primary")
        btn_layout.addWidget(self.btn_vectores, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Botón salir (menos chillón, tono más sobrio)
        self.btn_salir = QPushButton("Salir", self.container)
        f_btn_small = QFont("Segoe UI", 18)
        f_btn_small.setBold(True)
        self.btn_salir.setFont(f_btn_small)
        self.btn_salir.setFixedWidth(340)
        self.btn_salir.clicked.connect(self.cerrar_programa)
        self.btn_salir.setProperty("class", "danger")
        btn_layout.addWidget(self.btn_salir, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.main_layout.addLayout(btn_layout)

        # Info/fecha/hora/version/grupo (posicionados en esquinas)
        self.lbl_fecha = QLabel("", self.overlay)
        self.lbl_fecha.setProperty("class", "info")
        self.lbl_fecha.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.lbl_hora = QLabel("", self.overlay)
        self.lbl_hora.setProperty("class", "info")
        self.lbl_hora.setStyleSheet("color: #38bdf8;")  # acento para la hora
        self.lbl_hora.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.lbl_version = QLabel("V.0.0.4", self.overlay)
        self.lbl_version.setProperty("class", "info")

        self.lbl_grupo = QLabel("<i>GROUP 2</i>", self.overlay)
        self.lbl_grupo.setProperty("class", "info")
        self.lbl_grupo.setStyleSheet("color: #38bdf8; background: transparent; border: none;")
        self.lbl_grupo.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Sombra sutil en botones (profesional)
        sombra_btn = QGraphicsDropShadowEffect()
        sombra_btn.setBlurRadius(20)
        sombra_btn.setOffset(0, 6)
        sombra_btn.setColor(QColor(0, 0, 0, 140))
        self.btn_matrices.setGraphicsEffect(sombra_btn)
        # duplicar la sombra para cada botón (copiar objeto a cada uno)
        sombra_btn2 = QGraphicsDropShadowEffect()
        sombra_btn2.setBlurRadius(20)
        sombra_btn2.setOffset(0, 6)
        sombra_btn2.setColor(QColor(0, 0, 0, 140))
        self.btn_vectores.setGraphicsEffect(sombra_btn2)
        sombra_btn3 = QGraphicsDropShadowEffect()
        sombra_btn3.setBlurRadius(14)
        sombra_btn3.setOffset(0, 4)
        sombra_btn3.setColor(QColor(0, 0, 0, 120))
        self.btn_salir.setGraphicsEffect(sombra_btn3)

        # Timers
        self.fondo_timer = QTimer(self)
        self.fondo_timer.timeout.connect(self.animar_fondo)
        self.fondo_timer.start(40)  # 25 FPS para movimiento sutil

        self.hora_timer = QTimer(self)
        self.hora_timer.timeout.connect(self.actualizar_hora_fecha)
        self.hora_timer.start(1000)
        self.actualizar_hora_fecha()

        # Mostrar fullscreen tal como antes
        self.showFullScreen()

    def showEvent(self, _):
        # Actualizar fondo y overlay cuando se muestre
        self._actualizar_fondo()
        self.overlay.setGeometry(0, 0, self.width(), self.height())
        self.container.setGeometry(0, 0, self.width(), self.height())
        self._posicionar_esquinas()

    def _actualizar_fondo(self):
        """Carga y recorta la imagen de fondo respetando el offset (mantiene funcionalidad original)."""
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
            # Asegurar coordenadas válidas antes de recortar
            x_offset = max(0, min(x_offset, max(0, fondo_pixmap.width() - self.width())))
            y_offset = max(0, min(y_offset, max(0, fondo_pixmap.height() - self.height())))
            try:
                cropped = fondo_pixmap.copy(x_offset, y_offset, self.width(), self.height())
                self.fondo.setPixmap(cropped)
                self.fondo.setText("")
            except Exception:
                # Fallback: usar scaled completo si copy falla
                self.fondo.setPixmap(fondo_pixmap.scaled(self.width(), self.height(), Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation))
                self.fondo.setText("")
        self.fondo.setGeometry(0, 0, self.width(), self.height())

    def resizeEvent(self, _):
        # Mantener overlay/fondo y reposicionar esquinas al cambiar tamaño
        if hasattr(self, "fondo"):
            self._actualizar_fondo()
        if hasattr(self, "overlay"):
            self.overlay.setGeometry(0, 0, self.width(), self.height())
            self.container.setGeometry(0, 0, self.width(), self.height())
        self._posicionar_esquinas()

    def _posicionar_esquinas(self):
        # Posicionar versiones y etiquetas en esquinas (igual funcionalidad que antes)
        self.lbl_version.adjustSize()
        self.lbl_version.move(12, self.height() - self.lbl_version.height() - 12)

        self.lbl_fecha.adjustSize()
        self.lbl_fecha.move(self.width() - self.lbl_fecha.width() - 28, 18)

        self.lbl_grupo.adjustSize()
        self.lbl_grupo.move(self.width() - self.lbl_grupo.width() - 28, self.height() - self.lbl_grupo.height() - 12)

        self.lbl_hora.adjustSize()
        self.lbl_hora.move((self.width() - self.lbl_hora.width()) // 2, self.height() - self.lbl_hora.height() - 18)

        # Asegurar que los widgets estén visibles (son hijos del overlay)
        self.lbl_version.setParent(self.overlay)
        self.lbl_fecha.setParent(self.overlay)
        self.lbl_grupo.setParent(self.overlay)
        self.lbl_hora.setParent(self.overlay)

    def animar_fondo(self):
        # Mismo comportamiento sutil de desplazamiento de fondo que tenías
        self.fondo_offset += self.fondo_direction * 1
        max_offset = 80
        if self.fondo_offset > max_offset or self.fondo_offset < 0:
            self.fondo_direction *= -1
        self._actualizar_fondo()

    def actualizar_hora_fecha(self):
        # Mantener formato de hora y fecha exactamente como antes
        hora = QTime.currentTime().toString("hh:mm:ss")
        fecha = QDate.currentDate().toString("dd/MM/yyyy")
        self.lbl_fecha.setText(f"<b>Fecha:</b> {fecha}")
        self.lbl_hora.setText(f"<b>Hora:</b> {hora}")

    def abrir_matrices(self):
        try:
            # Abrir MatricesGui tal como antes (import dinámico por seguridad)
            from gui.MatricesGui import MatricesGui
            self.matrices = MatricesGui()
            self.matrices.show()
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir MatricesGui:\n{e}")

    def abrir_vectores(self):
        try:
            # Mantengo el import dinámico igual que en tu código original
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