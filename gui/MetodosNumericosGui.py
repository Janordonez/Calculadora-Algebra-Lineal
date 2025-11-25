# gui/MetodosNumericosGui.py

from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QTextEdit,
    QVBoxLayout, QHBoxLayout, QGridLayout, QMessageBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from models.logica_metodos_numericos import (
    evaluar_funcion,
    biseccion,
    regla_falsa,
)


class MetodosNumericosGui(QWidget):
    """
    Ventana para métodos numéricos:
    - Bisección
    - Regla Falsa

    Usa la lógica definida en models.logica_metodos_numericos.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Métodos Numéricos - Bisección y Regla Falsa")
        self.resize(1000, 650)

        self._configurar_estilos()
        self._crear_ui()

    def _configurar_estilos(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #020617;
                color: #e5e7eb;
                font-family: 'Segoe UI', 'Inter', 'Arial';
            }
            QLabel {
                font-size: 14px;
            }
            QLineEdit {
                background-color: #020617;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 14px;
            }
            QTextEdit {
                background-color: #020617;
                border: 1px solid #334155;
                border-radius: 6px;
                font-family: 'Consolas', 'Fira Code', monospace;
                font-size: 13px;
            }
            QPushButton {
                background-color: #325475;
                color: #ffffff;
                border-radius: 18px;
                border: 1px solid #325475;
                padding: 8px 20px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #3b6b9a;
                border: 1px solid #4a89c7;
            }
            QPushButton:pressed {
                background-color: #1e293b;
            }
        """)

    def _crear_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(10)

        # Título
        lbl_titulo = QLabel("Métodos Numéricos: Bisección y Regla Falsa")
        f_titulo = QFont("Segoe UI", 18, QFont.Weight.Bold)
        lbl_titulo.setFont(f_titulo)
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(lbl_titulo)

        # Panel de parámetros
        panel = QWidget(self)
        grid = QGridLayout(panel)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)

        fila = 0

        # Método (texto simple: B / RF)
        lbl_metodo = QLabel("Método (B/RF):")
        self.txt_metodo = QLineEdit("B")  # B = Bisección, RF = Regla Falsa
        self.txt_metodo.setToolTip("Escribe B para Bisección o RF para Regla Falsa")

        grid.addWidget(lbl_metodo, fila, 0)
        grid.addWidget(self.txt_metodo, fila, 1)

        # f(x)
        fila += 1
        lbl_fx = QLabel("f(x) =")
        self.txt_fx = QLineEdit("x**3 - 4*x + 1")
        grid.addWidget(lbl_fx, fila, 0)
        grid.addWidget(self.txt_fx, fila, 1, 1, 3)

        # a y b
        fila += 1
        lbl_a = QLabel("Límite inferior a:")
        self.txt_a = QLineEdit("0")
        grid.addWidget(lbl_a, fila, 0)
        grid.addWidget(self.txt_a, fila, 1)

        lbl_b = QLabel("Límite superior b:")
        self.txt_b = QLineEdit("2")
        grid.addWidget(lbl_b, fila, 2)
        grid.addWidget(self.txt_b, fila, 3)

        # tol y max_iter
        fila += 1
        lbl_tol = QLabel("Error deseado (tol):")
        self.txt_tol = QLineEdit("0.0001")
        grid.addWidget(lbl_tol, fila, 0)
        grid.addWidget(self.txt_tol, fila, 1)

        lbl_max_iter = QLabel("Máx. iteraciones:")
        self.txt_max_iter = QLineEdit("50")
        grid.addWidget(lbl_max_iter, fila, 2)
        grid.addWidget(self.txt_max_iter, fila, 3)

        # Botones
        fila += 1
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.btn_calcular = QPushButton("Calcular")
        self.btn_calcular.clicked.connect(self.calcular)

        self.btn_limpiar = QPushButton("Limpiar")
        self.btn_limpiar.clicked.connect(self.limpiar)

        self.btn_volver = QPushButton("Regresar al Menú")
        self.btn_volver.clicked.connect(self.volver_menu)

        btn_layout.addWidget(self.btn_calcular)
        btn_layout.addWidget(self.btn_limpiar)
        btn_layout.addStretch(1)
        btn_layout.addWidget(self.btn_volver)

        grid.addLayout(btn_layout, fila, 0, 1, 4)

        main_layout.addWidget(panel)

        # Iteraciones
        lbl_iter = QLabel("Iteraciones (paso a paso):")
        main_layout.addWidget(lbl_iter)

        self.txt_iter = QTextEdit()
        self.txt_iter.setReadOnly(True)
        main_layout.addWidget(self.txt_iter, stretch=1)

        # Resultado final
        self.lbl_resultado = QLabel("Resultado final: (pendiente de cálculo)")
        self.lbl_resultado.setWordWrap(True)
        main_layout.addWidget(self.lbl_resultado)

    # ---------------------------------------------------------
    # Acciones
    # ---------------------------------------------------------
    def limpiar(self):
        self.txt_fx.setText("x**3 - 4*x + 1")
        self.txt_a.setText("0")
        self.txt_b.setText("2")
        self.txt_tol.setText("0.0001")
        self.txt_max_iter.setText("50")
        self.txt_metodo.setText("B")
        self.txt_iter.clear()
        self.lbl_resultado.setText("Resultado final: (pendiente de cálculo)")

    def volver_menu(self):
        try:
            from gui.MenuGui import MenuGui
            self.menu = MenuGui()
            self.menu.show()
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo regresar al menú:\n{e}")

    def calcular(self):
        expr = self.txt_fx.text().strip()
        metodo_texto = self.txt_metodo.text().strip().upper()

        if metodo_texto not in ("B", "RF"):
            QMessageBox.warning(
                self,
                "Método inválido",
                "Escribe B para Bisección o RF para Regla Falsa."
            )
            return

        try:
            a = float(self.txt_a.text())
            b = float(self.txt_b.text())
            tol = float(self.txt_tol.text())
            max_iter = int(self.txt_max_iter.text())
        except ValueError:
            QMessageBox.critical(self, "Error", "Parámetros numéricos inválidos.")
            return

        # Validar intervalo
        try:
            fa = evaluar_funcion(expr, a)
            fb = evaluar_funcion(expr, b)
        except Exception as e:
            QMessageBox.critical(self, "Error al evaluar f(x)", str(e))
            return

        if fa * fb > 0:
            QMessageBox.warning(
                self,
                "Intervalo inválido",
                "f(a)*f(b) > 0.\nNo hay cambio de signo en el intervalo [a,b]."
            )
            return

        # Elegir método
        if metodo_texto == "B":
            funcion_metodo = biseccion
            nombre = "Bisección"
        else:
            funcion_metodo = regla_falsa
            nombre = "Regla Falsa"

        try:
            raiz, historia, intervalo_final, error_final = funcion_metodo(
                expr, a, b, tol, max_iter
            )
        except Exception as e:
            QMessageBox.critical(self, "Error en el método numérico", str(e))
            return

        # Mostrar iteraciones
        self._mostrar_iteraciones(historia, nombre)

        # Resultado final
        texto_res = (
            f"Método: {nombre} | "
            f"Raíz aproximada: {raiz:.10f} | "
            f"Iteraciones: {len(historia)} | "
            f"Error relativo final (%): {error_final:.6f} | "
            f"Intervalo final: [{intervalo_final[0]:.6f}, {intervalo_final[1]:.6f}]"
        )
        self.lbl_resultado.setText(texto_res)

    def _mostrar_iteraciones(self, historia, nombre_metodo: str):
        """
        Muestra la tabla de iteraciones en el QTextEdit.

        - Bisección: 9 columnas (sin Ea<E).
        - Regla Falsa: 9 columnas (con Ea<E).
        """
        self.txt_iter.clear()

        if nombre_metodo == "Bisección":
            encabezado = (
                f"=== Iteraciones (Bisección) ===\n"
                f"{'Iter':>4} | {'xl':>8} | {'xu':>8} | {'xr':>8} | "
                f"{'Ea %':>8} | {'f(xl)':>10} | {'f(xu)':>10} | "
                f"{'f(xr)':>10} | {'(xu-xl)':>10}\n"
                + "-" * 96
            )
            self.txt_iter.append(encabezado)

            for fila in historia:
                err_str = "---"
                if fila["error_pct"] is not None:
                    err_str = f"{fila['error_pct']:8.4f}"

                linea = (
                    f"{fila['iter']:4d} | "
                    f"{fila['a']:8.4f} | "
                    f"{fila['b']:8.4f} | "
                    f"{fila['x']:8.4f} | "
                    f"{err_str:>8} | "
                    f"{fila['fa']:10.4f} | "
                    f"{fila['fb']:10.4f} | "
                    f"{fila['fx']:10.4f} | "
                    f"{fila['len_interval']:10.4f}"
                )
                self.txt_iter.append(linea)

        else:  # Regla Falsa
            encabezado = (
                f"=== Iteraciones (Regla Falsa) ===\n"
                f"{'Iter':>4} | {'xl':>8} | {'xu':>8} | {'xr':>8} | "
                f"{'Ea %':>8} | {'f(xl)':>10} | {'f(xu)':>10} | "
                f"{'f(xr)':>10} | {'Ea<E':>6}\n"
                + "-" * 96
            )
            self.txt_iter.append(encabezado)

            for fila in historia:
                err_str = "---"
                if fila["error_pct"] is not None:
                    err_str = f"{fila['error_pct']:8.4f}"
                ea_flag = "True" if fila.get("ea_less_tol") else "False"

                linea = (
                    f"{fila['iter']:4d} | "
                    f"{fila['a']:8.4f} | "
                    f"{fila['b']:8.4f} | "
                    f"{fila['x']:8.4f} | "
                    f"{err_str:>8} | "
                    f"{fila['fa']:10.4f} | "
                    f"{fila['fb']:10.4f} | "
                    f"{fila['fx']:10.4f} | "
                    f"{ea_flag:>6}"
                )
                self.txt_iter.append(linea)


# Para probar esta ventana sola:
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    win = MetodosNumericosGui()
    win.show()
    sys.exit(app.exec())
