import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from typing import List
import traceback
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QListWidget, QMessageBox, QGridLayout, QTextEdit, QGroupBox, QSizePolicy,
    QInputDialog, QMenu, QComboBox, QCheckBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, qInstallMessageHandler, QtMsgType

# Importamos Matrices y tratamos de importar utilidades de Vectores; si no existen, proveemos un fallback.
from models.Matrices import Matrices
try:
    from models.Vectores import load_saved_vectors, save_vector, delete_saved_vector
except Exception:
    import json

    def _get_vectors_path():
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        data_dir = os.path.join(base, 'data')
        os.makedirs(data_dir, exist_ok=True)
        return os.path.join(data_dir, 'vectores.json')

    def load_saved_vectors() -> dict:
        path = _get_vectors_path()
        if not os.path.exists(path):
            return {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            out = {}
            for k, v in data.items():
                if isinstance(v, list):
                    out[k] = [float(x) for x in v]
                else:
                    out[k] = v
            return out
        except Exception:
            return {}

    def save_vector(name: str, vec: list):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Nombre de vector inválido.")
        path = _get_vectors_path()
        cur = load_saved_vectors()
        cur[name] = [float(x) for x in vec]
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(cur, f, indent=2)

    def delete_saved_vector(name: str):
        path = _get_vectors_path()
        cur = load_saved_vectors()
        if name in cur:
            del cur[name]
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(cur, f, indent=2)

# Intentar importar format_val desde Matrices; si no existe, usar un fallback local.
try:
    from models.Matrices import format_val
except Exception:
    from fractions import Fraction
    EPS = 1e-10

    def format_val(x):
        try:
            xf = float(x)
        except Exception:
            return str(x)
        if abs(xf) < EPS:
            return "0"
        if abs(xf - round(xf)) < EPS:
            return str(int(round(xf)))
        try:
            return str(Fraction(xf).limit_denominator())
        except Exception:
            return f"{xf:.6g}"


def _qt_message_handler(mode, context, message):
    """Manejador para mensajes Qt hacia stdout."""
    if mode == QtMsgType.QtDebugMsg:
        sys.stdout.write(f"DEBUG: {message}\n")
    elif mode == QtMsgType.QtInfoMsg:
        sys.stdout.write(f"INFO: {message}\n")
    elif mode == QtMsgType.QtWarningMsg:
        sys.stdout.write(f"WARNING: {message}\n")
    elif mode == QtMsgType.QtCriticalMsg:
        sys.stdout.write(f"CRITICAL: {message}\n")
    elif mode == QtMsgType.QtFatalMsg:
        sys.stdout.write(f"FATAL: {message}\n")
        sys.exit(1)


# Instalar el manejador antes de crear widgets
qInstallMessageHandler(_qt_message_handler)


class OperacionesMatricesGui(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Operaciones con Matrices")
        self.resize(900, 600)

        self.setStyleSheet("""
            QWidget { background: qlineargradient(x1:0 y1:0, x2:1 y2:1, stop:0 #071428, stop:1 #0b2940); color: #e6eef6; font-family: 'Segoe UI', Arial; }
            QGroupBox { border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; margin-top: 8px; background: rgba(255,255,255,0.02); }
            QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 4px 8px; color: #9ed0ff; font-weight: 700; }
            QLabel { color: #dff4ff; }
            QLineEdit { background: #07202a; border: 1px solid #164a60; padding: 6px; border-radius: 6px; color: #eaf6ff; }
            QLineEdit:focus { border: 1px solid #56b4e9; background: #04202a; }
            QPushButton { background: #0f4a66; color: white; border-radius: 8px; padding: 8px 12px; font-weight: 700; }
            QPushButton:hover { background: #1b6a8f; }
            QListWidget { background: #042233; border: 1px solid #123d51; padding: 6px; color: #dff4ff; }
            QListWidget::item:selected { background: #1b6a8f; color: #02121a; }
            QTextEdit { background: #021923; border: 1px solid #123d51; color: #e6f7ff; border-radius: 8px; padding: 10px; }
        """)

        layout = QVBoxLayout()

        # barra superior con botón home (coherente con otras ventanas)
        barra_top = QHBoxLayout()
        self.btn_home = QPushButton("🏠")
        self.btn_home.setFixedSize(52, 52)
        fbtn_home = QFont("Segoe UI", 20)
        fbtn_home.setWeight(QFont.Weight.Bold)
        self.btn_home.setFont(fbtn_home)
        self.btn_home.clicked.connect(self.ir_a_menu)
        barra_top.addWidget(self.btn_home)
        barra_top.addStretch()
        layout.addLayout(barra_top)

        # --- Grupo superior: crear matriz ---
        crear_group = QGroupBox("Crear matriz")
        crear_layout = QHBoxLayout()
        crear_group.setLayout(crear_layout)

        form = QGridLayout()
        lbl_name = QLabel("Nombre:")
        lbl_name.setFont(QFont('Segoe UI', 10, QFont.Weight.DemiBold))
        form.addWidget(lbl_name, 0, 0)
        self.name_input = QLineEdit()
        form.addWidget(self.name_input, 0, 1)
        form.addWidget(QLabel("Filas:"), 1, 0)
        self.rows_input = QLineEdit()
        self.rows_input.setFixedWidth(80)
        form.addWidget(self.rows_input, 1, 1)
        form.addWidget(QLabel("Columnas:"), 2, 0)
        self.cols_input = QLineEdit()
        self.cols_input.setFixedWidth(80)
        form.addWidget(self.cols_input, 2, 1)
        self.btn_generate = QPushButton("🧩 Generar campos")
        self.btn_generate.setToolTip("Generar los campos de entrada para la matriz (filas x columnas)")
        self.btn_generate.clicked.connect(self.generate_fields)
        form.addWidget(self.btn_generate, 3, 0, 1, 2)

        crear_layout.addLayout(form)

        # contenedor para inputs de matriz (derecha)
        self.matrix_grid = QGridLayout()
        self.matrix_widgets: List[List[QLineEdit]] = []
        crear_layout.addLayout(self.matrix_grid)

        layout.addWidget(crear_group)

        # botones principales en grupo
        acciones_group = QGroupBox("Acciones")
        acciones_layout = QHBoxLayout()
        acciones_group.setLayout(acciones_layout)
        self.btn_save = QPushButton("💾 Guardar matriz")
        self.btn_save.setToolTip("Guardar la matriz actual")
        self.btn_save.clicked.connect(self.save_matrix)
        acciones_layout.addWidget(self.btn_save)
        self.btn_show = QPushButton("👁️ Mostrar seleccionada")
        self.btn_show.setToolTip("Mostrar la matriz seleccionada en el panel de resultados")
        self.btn_show.clicked.connect(self.show_selected)
        acciones_layout.addWidget(self.btn_show)
        self.btn_transpose = QPushButton("🔁 Transponer seleccionada")
        self.btn_transpose.setToolTip("Calcular y (opcionalmente) guardar la transpuesta de la matriz seleccionada")
        self.btn_transpose.clicked.connect(self.transpose_selected)
        acciones_layout.addWidget(self.btn_transpose)
        self.btn_delete = QPushButton("🗑️ Eliminar seleccionados")
        self.btn_delete.setToolTip("Eliminar las matrices seleccionadas")
        self.btn_delete.clicked.connect(self.delete_selected)
        acciones_layout.addWidget(self.btn_delete)

        # BOTÓN ÚNICO: "Métodos determinante"
        self.btn_methods = QPushButton("Métodos determinante")
        self.btn_methods.setToolTip("Selecciona un método y se mostrará paso a paso automáticamente")
        menu_methods = QMenu(self)
        menu_methods.addAction("Sarrus (pasos)", lambda: self._show_method_steps('sarrus'))
        menu_methods.addAction("Cofactores (pasos)", lambda: self._show_method_steps('cofactors'))
        menu_methods.addAction("Cramer (pasos)", lambda: self._show_method_steps('cramer'))
        self.btn_methods.setMenu(menu_methods)
        acciones_layout.addWidget(self.btn_methods)

        layout.addWidget(acciones_group)

        # Panel de operaciones y lista (grupo)
        panel_group = QGroupBox("Matrices guardadas y operaciones")
        panel_layout = QHBoxLayout()
        panel_group.setLayout(panel_layout)

        left = QVBoxLayout()
        left.addWidget(QLabel("Matrices guardadas:"))
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.list_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        left.addWidget(self.list_widget)
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self._toggle_list_item_at_pos)
        left.addWidget(QLabel("Vectores guardados:"))
        self.vectors_list = QListWidget()
        self.vectors_list.setFixedWidth(200)
        self.vectors_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.vectors_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.vectors_list.customContextMenuRequested.connect(self._toggle_vector_item_at_pos)
        left.addWidget(self.vectors_list)
        self.btn_delete_vector = QPushButton("🗑️ Eliminar vector")
        self.btn_delete_vector.setToolTip("Eliminar uno o varios vectores seleccionados")
        self.btn_delete_vector.clicked.connect(self._delete_selected_vector)
        left.addWidget(self.btn_delete_vector)
        panel_layout.addLayout(left, 1)

        right = QVBoxLayout()
        sel_layout = QHBoxLayout()
        sel_layout.addWidget(QLabel("A (nombre):"))
        self.sel_a = QLineEdit()
        self.sel_a.setFixedWidth(120)
        sel_layout.addWidget(self.sel_a)
        sel_layout.addWidget(QLabel("B (nombre):"))
        self.sel_b = QLineEdit()
        self.sel_b.setFixedWidth(120)
        sel_layout.addWidget(self.sel_b)

        # Operación: combo box y controles avanzados
        self.op_combo = QComboBox()
        self.op_combo.addItems(["Multiplicar", "Sumar", "Restar", "Determinante"])
        self.op_combo.setFixedWidth(140)
        sel_layout.addWidget(self.op_combo)

        sel_layout.addWidget(QLabel("Método det:"))
        self.det_method_combo = QComboBox()
        self.det_method_combo.addItems(["Eliminación", "Cofactores", "Sarrus", "Cramer"])
        self.det_method_combo.setFixedWidth(160)
        sel_layout.addWidget(self.det_method_combo)

        self.btn_execute = QPushButton("Ejecutar")
        self.btn_execute.clicked.connect(self.operate_selected)
        sel_layout.addWidget(self.btn_execute)

        # Checkbox para mostrar/ocultar pasos
        self.chk_show_steps = QCheckBox("Mostrar pasos")
        self.chk_show_steps.setToolTip("Alterna la visualización de procedimientos detallados")
        self.chk_show_steps.setChecked(True)
        sel_layout.addWidget(self.chk_show_steps)
        # Checkbox para colapsar salidas largas
        self.chk_collapse = QCheckBox("Colapsar pasos largos")
        self.chk_collapse.setToolTip("Muestra solo un resumen cuando los pasos son muy extensos")
        self.chk_collapse.setChecked(False)
        sel_layout.addWidget(self.chk_collapse)

        # Estado de última salida para re-renderizar en tiempo real
        self._last_full_text = None
        self._last_compact_text = None
        self.chk_show_steps.stateChanged.connect(lambda _: self._rerender_last())
        self.chk_collapse.stateChanged.connect(lambda _: self._rerender_last())
        right.addLayout(sel_layout)

        # segunda fila: controles de vector y escalar
        vec_layout = QHBoxLayout()
        vec_layout.addWidget(QLabel("Vector (ej: 1,2,3):"))
        self.vector_input = QLineEdit()
        self.vector_input.setFixedWidth(220)
        self.vector_input.setPlaceholderText("ej: 1,0,2")
        vec_layout.addWidget(self.vector_input)
        self.btn_save_vector = QPushButton("Guardar vector")
        self.btn_save_vector.clicked.connect(self.save_vector_ui)
        vec_layout.addWidget(self.btn_save_vector)
        self.btn_mult_mat_vec = QPushButton("A x vector")
        self.btn_mult_mat_vec.clicked.connect(self.multiply_matrix_by_vector)
        vec_layout.addWidget(self.btn_mult_mat_vec)
        self.btn_mult_saved_vec = QPushButton("A x vec guard.")
        self.btn_mult_saved_vec.clicked.connect(self.multiply_matrix_by_saved_vector)
        vec_layout.addWidget(self.btn_mult_saved_vec)
        vec_layout.addStretch()
        vec_layout.addWidget(QLabel("Escalar:"))
        self.scalar_input = QLineEdit()
        self.scalar_input.setFixedWidth(100)
        self.scalar_input.setPlaceholderText("ej: 2.5 o 3/4")
        vec_layout.addWidget(self.scalar_input)
        self.btn_scalar = QPushButton("A * escalar")
        self.btn_scalar.clicked.connect(self.multiply_by_scalar_selected)
        vec_layout.addWidget(self.btn_scalar)
        right.addLayout(vec_layout)

        # tercera fila: entrada de ecuación y botón "Resolver ecuación"
        eq_layout = QHBoxLayout()
        self.equation_input = QLineEdit()
        self.equation_input.setPlaceholderText("ej: (A*B)^T + (3/4)*C - D, 2*A, A^-1")
        self.equation_input.setMinimumHeight(44)
        eq_layout.addWidget(self.equation_input, 1)
        self.btn_solve_equation = QPushButton("Resolver ecuación")
        self.btn_solve_equation.setMinimumHeight(44)
        self.btn_solve_equation.clicked.connect(self.solve_equation)
        eq_layout.addWidget(self.btn_solve_equation)
        right.addLayout(eq_layout)

        right.addWidget(QLabel("Resultado / Mensajes:"))
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setFixedHeight(220)
        right.addWidget(self.result_text, 1)

        panel_layout.addLayout(right, 2)
        layout.addWidget(panel_group)
        self.setLayout(layout)

        self.reload_saved()
        # Abrir la ventana maximizada para aprovechar pantalla del usuario
        try:
            self.showMaximized()
        except Exception:
            # Fallback silencioso si el método no está disponible
            pass

    # ---------------- Utilidades de salida ----------------
    def _set_result_text(self, content):
        if isinstance(content, list):
            text = "\n".join(content)
        else:
            text = str(content)
        if getattr(self, 'chk_show_steps', None) and self.chk_show_steps.isChecked() \
           and getattr(self, 'chk_collapse', None) and self.chk_collapse.isChecked():
            lines = text.splitlines()
            max_lines = 180
            if len(lines) > max_lines:
                head = 120
                tail = 60
                hidden = len(lines) - head - tail
                if hidden > 0:
                    marker = f"[… {hidden} líneas ocultas …] (desmarca 'Colapsar pasos largos' para ver todo)"
                    text = "\n".join(lines[:head] + [marker] + lines[-tail:])
        self.result_text.setPlainText(text)

    def _store_and_render(self, full_content, compact_content):
        def to_text(c):
            if isinstance(c, list):
                return "\n".join(c)
            return str(c)
        self._last_full_text = to_text(full_content) if full_content is not None else None
        self._last_compact_text = to_text(compact_content) if compact_content is not None else None
        self._rerender_last()

    def _rerender_last(self):
        if getattr(self, 'chk_show_steps', None) and self.chk_show_steps.isChecked():
            base = self._last_full_text if self._last_full_text is not None else self._last_compact_text
        else:
            base = self._last_compact_text if self._last_compact_text is not None else self._last_full_text
        if base is not None:
            self._set_result_text(base)

    # =========================
    #  Manejador único para mostrar pasos de métodos
    # =========================
    def _show_method_steps(self, method: str):
        try:
            item = self.list_widget.currentItem()
            if not item:
                raise ValueError("Selecciona una matriz de la lista.")
            name = item.text().split('  ')[0]
            saved = Matrices.load_saved_matrices()
            if name not in saved:
                raise ValueError("Matriz no encontrada.")
            mat = saved[name]
            if not isinstance(mat, list) or not all(isinstance(row, list) for row in mat):
                raise ValueError("La matriz guardada tiene formato inválido. Debe ser lista de filas.")

            if method == 'sarrus':
                det, pasos = Matrices.det_sarrus(mat)
                self._set_result_text([f"Determinante por Sarrus de '{name}': {format_val(det)}", "Pasos:", pasos])
                return

            if method == 'cofactors':
                det, pasos = Matrices.det_cofactor(mat)
                self._set_result_text([f"Determinante por Cofactores de '{name}': {format_val(det)}", "Pasos:", pasos])
                return

            if method == 'cramer':
                rows = len(mat)
                cols = len(mat[0]) if rows > 0 else 0
                if cols == rows + 1:
                    A = [row[:-1] for row in mat]
                    b = [[row[-1]] for row in mat]
                    sol, pasos = Matrices.cramer(A, b)
                    if sol is None:
                        self._set_result_text([f"Cramer no aplicable para '{name}'.", "Pasos:", pasos])
                    else:
                        self._set_result_text([f"Cramer (matriz aumentada) '{name}':", "Pasos:", pasos])
                    return
                b_name, ok = QInputDialog.getText(self, "Vector b requerido", "Ingrese el nombre del vector/matriz columna b:")
                if not ok or not b_name.strip():
                    return
                b_name = b_name.strip()
                saved2 = Matrices.load_saved_matrices()
                if b_name not in saved2:
                    raise ValueError(f"Vector b '{b_name}' no encontrado.")
                A = mat
                b_mat = saved2[b_name]
                if not isinstance(b_mat, list) or not all(isinstance(row, list) and len(row) == 1 for row in b_mat):
                    raise ValueError("b debe ser una matriz columna (nx1).")
                if len(b_mat) != len(A):
                    raise ValueError("Dimensiones incompatibles entre A y b.")
                sol, pasos = Matrices.cramer(A, b_mat)
                if sol is None:
                    self._set_result_text([f"Cramer no aplicable para A='{name}' y b='{b_name}'.", "Pasos:", pasos])
                else:
                    self._set_result_text([f"Cramer A='{name}', b='{b_name}':", "Pasos:", pasos])
                return

            raise ValueError("Método no reconocido.")
        except Exception as e:
            tb = traceback.format_exc()
            self._set_result_text([f"Error: {e}", f"Traceback:\n{tb}"])
            QMessageBox.warning(self, "Mostrar pasos - Error", str(e))

    # =========================
    #  Resto utilidades GUI (generar, guardar, mostrar, multiplicar, etc.)
    # =========================
    def generate_fields(self):
        try:
            r = int(self.rows_input.text())
            c = int(self.cols_input.text())
            if r <= 0 or c <= 0:
                raise ValueError()
        except Exception:
            QMessageBox.warning(self, "Error", "Filas y columnas deben ser enteros positivos.")
            return
        for i in reversed(range(self.matrix_grid.count())):
            w = self.matrix_grid.itemAt(i).widget()
            if w:
                w.setParent(None)
        self.matrix_widgets = []
        for i in range(r):
            row_widgets = []
            for j in range(c):
                le = QLineEdit()
                le.setFixedWidth(80)
                le.setPlaceholderText('0')
                self.matrix_grid.addWidget(le, i, j)
                row_widgets.append(le)
            self.matrix_widgets.append(row_widgets)

    def _read_matrix_from_fields(self) -> List[List[float]]:
        if not self.matrix_widgets:
            raise ValueError("Primero genera los campos de la matriz.")
        mat = []
        for i, row in enumerate(self.matrix_widgets):
            r = []
            for j, le in enumerate(row):
                txt = le.text().strip() or '0'
                try:
                    if '/' in txt:
                        from fractions import Fraction
                        val = float(Fraction(txt))
                    else:
                        val = float(txt)
                except Exception:
                    raise ValueError(f"Valor no numérico en fila {i+1}, col {j+1}: '{txt}'")
                r.append(val)
            mat.append(r)
        return mat

    def save_matrix(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Proporciona un nombre para la matriz.")
            return
        try:
            mat = self._read_matrix_from_fields()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
            return
        try:
            Matrices.save_matrix(name, mat)
            self._set_result_text(f"Matriz '{name}' guardada correctamente.")
            self.reload_saved()
        except Exception as e:
            QMessageBox.critical(self, "Error al guardar", str(e))

    def reload_saved(self):
        self.list_widget.clear()
        saved = Matrices.load_saved_matrices()
        for k in sorted(saved.keys()):
            rows = len(saved[k])
            cols = len(saved[k][0]) if rows > 0 else 0
            self.list_widget.addItem(f"{k}  ({rows}x{cols})")
        self.saved_vectors = load_saved_vectors()
        self.vectors_list.clear()
        for name, vec in sorted(self.saved_vectors.items()):
            self.vectors_list.addItem(f"{name}  ({len(vec)})")
        self.vectors_list.itemDoubleClicked.connect(self._load_vector_into_input)

    def ir_a_menu(self):
        try:
            # Importar MenuGui de la forma consistente con otros módulos
            # (al ejecutar desde Main.py la carpeta `gui` está en sys.path)
            from MenuGui import MenuGui
            self.menu = MenuGui()
            # MenuGui internamente usa showFullScreen(); llamar show() está bien
            self.menu.show()
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir MenuGui:\n{e}")

    def _get_name_from_list_item(self, item_text: str) -> str:
        return item_text.split('  ')[0]

    def show_selected(self):
        item = self.list_widget.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Selecciona una matriz de la lista.")
            return
        name = self._get_name_from_list_item(item.text())
        saved = Matrices.load_saved_matrices()
        if name not in saved:
            QMessageBox.warning(self, "Error", "Matriz no encontrada.")
            return
        mat = saved[name]
        txt = f"Matriz '{name}' ({len(mat)}x{len(mat[0]) if mat else 0}):\n"
        for row in mat:
            txt += "[ " + ", ".join(format_val(x) for x in row) + " ]\n"
        self._set_result_text(txt)

        r = len(mat)
        c = len(mat[0]) if r > 0 else 0
        if self.matrix_widgets and len(self.matrix_widgets) == r and len(self.matrix_widgets[0]) == c:
            for i in range(r):
                for j in range(c):
                    self.matrix_widgets[i][j].setText(str(mat[i][j]))
            return

        reply = QMessageBox.question(self, "Volcar matriz", f"¿Generar campos {r}x{c} y volcar la matriz en los campos?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.rows_input.setText(str(r))
            self.cols_input.setText(str(c))
            try:
                self.generate_fields()
            except Exception:
                pass
            if self.matrix_widgets and len(self.matrix_widgets) == r and len(self.matrix_widgets[0]) == c:
                for i in range(r):
                    for j in range(c):
                        self.matrix_widgets[i][j].setText(str(mat[i][j]))

    # ---------------- Vector helpers ----------------
    def _parse_vector_text(self, txt: str) -> list[float]:
        parts = [p.strip() for p in txt.split(',') if p.strip()!='']
        if not parts:
            raise ValueError('Vector vacío')
        try:
            vals = []
            from fractions import Fraction
            for p in parts:
                if '/' in p:
                    vals.append(float(Fraction(p)))
                else:
                    vals.append(float(p))
            return vals
        except Exception:
            raise ValueError('Formato de vector inválido. Usa números separados por comas.')

    def multiply_matrix_by_vector(self):
        a_name = self.sel_a.text().strip()
        if not a_name:
            item = self.list_widget.currentItem()
            if not item:
                QMessageBox.warning(self, 'Error', 'Proporciona el nombre de la matriz A o selecciona una matriz.')
                return
            a_name = self._get_name_from_list_item(item.text())
        saved = Matrices.load_saved_matrices()
        if a_name not in saved:
            QMessageBox.warning(self, 'Error', f'No existe la matriz A: {a_name}')
            return
        a = saved[a_name]
        vec_txt = self.vector_input.text().strip()
        if not vec_txt:
            QMessageBox.warning(self, 'Error', 'Introduce un vector en el campo correspondiente.')
            return
        try:
            v = self._parse_vector_text(vec_txt)
        except Exception as e:
            QMessageBox.warning(self, 'Error', str(e))
            return
        if not a:
            QMessageBox.warning(self, 'Error', 'Matriz A vacía.')
            return
        m = len(a[0])
        if len(v) != m:
            QMessageBox.warning(self, 'Error', f'Dimensiones incompatibles: A tiene {m} columnas, el vector tiene {len(v)} componentes.')
            return
        b = [[float(x)] for x in v]
        try:
            res, pasos = Matrices.multiply_with_steps(a, b)
            pasos.append('Resultado vector columna:')
            pasos.append('\n'.join(format_val(row[0]) for row in res))
            full_text = '\n'.join(pasos)
            plano = [row[0] for row in res]
            compact_text = 'Resultado vector:\n[ ' + ', '.join(format_val(x) for x in plano) + ' ]'
            self._store_and_render(full_text, compact_text)
        except Exception as e:
            QMessageBox.critical(self, 'Error al multiplicar', str(e))

    def save_vector_ui(self):
        txt = self.vector_input.text().strip()
        if not txt:
            QMessageBox.warning(self, 'Error', 'Introduce un vector para guardar.')
            return
        try:
            v = self._parse_vector_text(txt)
        except Exception as e:
            QMessageBox.warning(self, 'Error', str(e))
            return
        name, ok = QInputDialog.getText(self, 'Guardar vector', 'Nombre del vector:')
        if not ok or not name.strip():
            return
        try:
            save_vector(name.strip(), v)
            self.saved_vectors = load_saved_vectors()
            self.vectors_list.clear()
            for nm, vec in sorted(self.saved_vectors.items()):
                self.vectors_list.addItem(f"{nm}  ({len(vec)})")
            msg = f"Vector '{name.strip()}' guardado."
            self._store_and_render(msg, msg)
        except Exception as e:
            QMessageBox.critical(self, 'Error al guardar vector', str(e))

    def delete_vector_ui(self, name: str):
        if not name:
            return
        reply = QMessageBox.question(self, 'Confirmar eliminación', f"Eliminar vector '{name}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            delete_saved_vector(name)
            self.saved_vectors = load_saved_vectors()
            self.vectors_list.clear()
            for nm, vec in sorted(self.saved_vectors.items()):
                self.vectors_list.addItem(f"{nm}  ({len(vec)})")
            msg = f"Vector '{name}' eliminado."
            self._store_and_render(msg, msg)

    def _load_vector_into_input(self, item):
        name = item.text().split('  ')[0]
        v = self.saved_vectors.get(name)
        if v is None:
            QMessageBox.warning(self, 'Error', 'Vector no encontrado en memoria.')
            return
        self.vector_input.setText(','.join(str(x) for x in v))

    def multiply_matrix_by_saved_vector(self):
        item = self.vectors_list.currentItem()
        if not item:
            QMessageBox.warning(self, 'Error', 'Selecciona un vector guardado.')
            return
        name = item.text().split('  ')[0]
        v = self.saved_vectors.get(name)
        if v is None:
            QMessageBox.warning(self, 'Error', 'Vector no encontrado.')
            return
        a_name = self.sel_a.text().strip()
        if not a_name:
            itemm = self.list_widget.currentItem()
            if not itemm:
                QMessageBox.warning(self, 'Error', 'Proporciona el nombre de la matriz A o selecciona una matriz.')
                return
            a_name = self._get_name_from_list_item(itemm.text())
        saved = Matrices.load_saved_matrices()
        if a_name not in saved:
            QMessageBox.warning(self, 'Error', f'No existe la matriz A: {a_name}')
            return
        a = saved[a_name]
        if not a:
            QMessageBox.warning(self, 'Error', 'Matriz A vacía.')
            return
        m = len(a[0])
        if len(v) != m:
            QMessageBox.warning(self, 'Error', f'Dimensiones incompatibles: A tiene {m} columnas, el vector tiene {len(v)} componentes.')
            return
        b = [[float(x)] for x in v]
        try:
            res, pasos = Matrices.multiply_with_steps(a, b)
            pasos.append('Resultado vector columna:')
            pasos.append('\n'.join(format_val(row[0]) for row in res))
            full_text = '\n'.join(pasos)
            plano = [row[0] for row in res]
            compact_text = 'Resultado vector:\n[ ' + ', '.join(format_val(x) for x in plano) + ' ]'
            self._store_and_render(full_text, compact_text)
        except Exception as e:
            QMessageBox.critical(self, 'Error al multiplicar', str(e))

    def transpose_selected(self):
        item = self.list_widget.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Selecciona una matriz de la lista.")
            return
        name = self._get_name_from_list_item(item.text())
        saved = Matrices.load_saved_matrices()
        if name not in saved:
            QMessageBox.warning(self, "Error", "Matriz no encontrada.")
            return
        mat = saved[name]
        try:
            if hasattr(Matrices, 'transpose_with_steps'):
                t, pasos = Matrices.transpose_with_steps(mat)
                out = pasos + ["Transpuesta:", Matrices._mat_to_str_frac(t)]
                full_text = "\n".join(out)
                compact_text = "Transpuesta:\n" + Matrices._mat_to_str_frac(t)
                self._store_and_render(full_text, compact_text)
            else:
                t = Matrices.transpose(mat)
                self._set_result_text("Transpuesta:\n" + Matrices._mat_to_str_frac(t))
            reply = QMessageBox.question(self, "Guardar transpuesta", f"¿Guardar transpuesta como '{name}_T'?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                Matrices.save_matrix(f"{name}_T", t)
                self.reload_saved()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # ---------------- Ecuaciones matriciales ----------------
    def solve_equation(self):
        expr = self.equation_input.text().strip()
        if not expr:
            QMessageBox.warning(self, "Error", "Ingresa una ecuación. Ej: (A*B)^T + C")
            return
        saved_mats = Matrices.load_saved_matrices()
        saved_vecs = load_saved_vectors()
        if '=' in expr:
            lhs_str, rhs_str = expr.split('=', 1)
            lhs_str = lhs_str.strip()
            rhs_str = rhs_str.strip()
            try:
                lhs_val, lhs_steps, lhs_used = self._eval_matrix_expression(lhs_str, saved_mats, saved_vecs)
                rhs_val, rhs_steps, rhs_used = self._eval_matrix_expression(rhs_str, saved_mats, saved_vecs)
            except Exception as e:
                QMessageBox.critical(self, "Error al resolver ecuación", str(e))
                return
            used_mats_all = {**lhs_used.get('matrices', {}), **rhs_used.get('matrices', {})}
            used_vecs_all = {**lhs_used.get('vectores', {}), **rhs_used.get('vectores', {})}
            full_out: list[str] = []
            if used_mats_all or used_vecs_all:
                full_out.append("Símbolos usados:")
                if used_mats_all:
                    full_out.append("Matrices:")
                    for nm in sorted(used_mats_all.keys()):
                        full_out.append(f"{nm}:")
                        full_out.append(Matrices._mat_to_str_frac(used_mats_all[nm]))
                if used_vecs_all:
                    full_out.append("Vectores:")
                    for nm in sorted(used_vecs_all.keys()):
                        full_out.append(f"{nm}:")
                        col = [[v] for v in used_vecs_all[nm]]
                        full_out.append(Matrices._mat_to_str_frac(col))
                full_out.append("")
            full_out.append(f"Lado izquierdo: {lhs_str}")
            full_out.extend(lhs_steps)
            full_out.append("Resultado izquierdo:")
            full_out.append(Matrices._mat_to_str_frac(lhs_val))
            full_out.append("")
            full_out.append(f"Lado derecho: {rhs_str}")
            full_out.extend(rhs_steps)
            full_out.append("Resultado derecho:")
            full_out.append(Matrices._mat_to_str_frac(rhs_val))
            full_out.append("")
            iguales = Matrices.equal(lhs_val, rhs_val)
            full_out.append(f"¿Se cumple la igualdad LHS = RHS? -> {'SI' if iguales else 'NO'}")

            compact_out: list[str] = []
            compact_out.append(f"Lado izquierdo ({lhs_str}):")
            compact_out.append(Matrices._mat_to_str_frac(lhs_val))
            compact_out.append("")
            compact_out.append(f"Lado derecho ({rhs_str}):")
            compact_out.append(Matrices._mat_to_str_frac(rhs_val))
            compact_out.append("")
            compact_out.append(f"¿Se cumple la igualdad LHS = RHS? -> {'SI' if iguales else 'NO'}")
            self._store_and_render("\n".join(full_out), "\n".join(compact_out))

            left_suggest = lhs_str
            right_suggest = rhs_str
            text, ok = QInputDialog.getText(self, "Guardar LHS",
                                            "Nombre para guardar el lado izquierdo (puedes editar):",
                                            QLineEdit.EchoMode.Normal,
                                            left_suggest)
            if ok:
                final = text.strip() or left_suggest
                try:
                    Matrices.save_matrix(final, lhs_val)
                except Exception as e:
                    QMessageBox.critical(self, "Error al guardar LHS", str(e))
            text2, ok2 = QInputDialog.getText(self, "Guardar RHS",
                                              "Nombre para guardar el lado derecho (puedes editar):",
                                              QLineEdit.EchoMode.Normal,
                                              right_suggest)
            if ok2:
                final2 = text2.strip() or right_suggest
                try:
                    Matrices.save_matrix(final2, rhs_val)
                except Exception as e:
                    QMessageBox.critical(self, "Error al guardar RHS", str(e))
            self.reload_saved()
            return

        try:
            res, pasos, used = self._eval_matrix_expression(expr, saved_mats, saved_vecs)
        except Exception as e:
            QMessageBox.critical(self, "Error al resolver ecuación", str(e))
            return
        used_m = used.get('matrices', {})
        used_v = used.get('vectores', {})
        full_out: list[str] = []
        if used_m or used_v:
            full_out.append("Símbolos usados:")
            if used_m:
                full_out.append("Matrices:")
                for nm in sorted(used_m.keys()):
                    full_out.append(f"{nm}:")
                    full_out.append(Matrices._mat_to_str_frac(used_m[nm]))
            if used_v:
                full_out.append("Vectores:")
                for nm in sorted(used_v.keys()):
                    full_out.append(f"{nm}:")
                    col = [[v] for v in used_v[nm]]
                    full_out.append(Matrices._mat_to_str_frac(col))
            full_out.append("")
        full_out.extend(pasos)
        full_out.append("Resultado final de la expresión:")
        full_out.append(Matrices._mat_to_str_frac(res))
        compact_out = "Resultado final de la expresión:\n" + Matrices._mat_to_str_frac(res)
        self._store_and_render("\n".join(full_out), compact_out)
        text, ok = QInputDialog.getText(self, "Guardar resultado",
                                        "Nombre para guardar (puedes editar):",
                                        QLineEdit.EchoMode.Normal,
                                        expr)
        if ok:
            final = text.strip() or expr
            try:
                Matrices.save_matrix(final, res)
                self.reload_saved()
            except Exception as e:
                QMessageBox.critical(self, "Error al guardar", str(e))

    def _eval_matrix_expression(self, expr: str, saved_mats: dict, saved_vecs: dict):
        s = expr
        i = 0
        used_mats: dict[str, list[list[float]]] = {}
        used_vecs: dict[str, list[float]] = {}

        def skip_ws():
            nonlocal i
            while i < len(s) and s[i].isspace():
                i += 1

        def peek():
            skip_ws()
            return s[i] if i < len(s) else ''

        def consume(ch=None):
            nonlocal i
            skip_ws()
            if i >= len(s):
                return ''
            c = s[i]
            if ch is not None and c != ch:
                raise ValueError(f"Se esperaba '{ch}' en la posición {i+1}.")
            i += 1
            return c

        def parse_ident():
            nonlocal i
            skip_ws()
            if i >= len(s) or not (s[i].isalpha() or s[i] == '_'):
                raise ValueError(f"Se esperaba un nombre de matriz en la posición {i+1}.")
            start = i
            i += 1
            while i < len(s) and (s[i].isalnum() or s[i] == '_'):
                i += 1
            return s[start:i]

        def parse_number():
            nonlocal i
            skip_ws()
            start = i
            has_digit = False
            while i < len(s) and (s[i].isdigit() or s[i] == '.'):
                if s[i].isdigit():
                    has_digit = True
                i += 1
            if not has_digit:
                return None
            num = s[start:i]
            skip_ws()
            if i < len(s) and s[i] == '/':
                i += 1
                skip_ws()
                start_den = i
                if i >= len(s) or not s[i].isdigit():
                    raise ValueError("Denominador de fracción inválido.")
                while i < len(s) and s[i].isdigit():
                    i += 1
                den = s[start_den:i]
                from fractions import Fraction
                try:
                    val = float(Fraction(num + '/' + den))
                except Exception:
                    raise ValueError("Número fraccionario inválido.")
                return ('scalar', val, [f"Escalar {num}/{den}"])
            else:
                try:
                    val = float(num)
                    return ('scalar', val, [f"Escalar {num}"])
                except Exception:
                    return None

        def parse_primary():
            nonlocal i, used_mats, used_vecs
            if peek() == '(':
                consume('(')
                val = parse_expr()
                if peek() != ')':
                    raise ValueError("Falta ')' de cierre en la ecuación.")
                consume(')')
                return val
            pos_before = i
            num = parse_number()
            if num is not None:
                return num
            i = pos_before
            name = parse_ident()
            if name in saved_mats and name in saved_vecs:
                raise ValueError(f"Existe una matriz y un vector con el mismo nombre '{name}'. Cambia uno de los nombres.")
            if name in saved_mats:
                mat = saved_mats[name]
                used_mats[name] = mat
                return ('matrix', mat, [])
            if name in saved_vecs:
                vec = saved_vecs[name]
                used_vecs[name] = vec
                return ('vector', vec, [])
            raise ValueError(f"Símbolo '{name}' no existe en guardados (matrices o vectores).")

        def as_mat(val):
            if val[0] != 'matrix':
                raise ValueError("Operación válida solo para matrices.")
            return val[1]

        def as_scalar(val):
            if val[0] != 'scalar':
                raise ValueError("Se esperaba un escalar.")
            return float(val[1])

        def to_scalar(val):
            return val[0] == 'scalar'

        def to_matrix(val):
            return val[0] == 'matrix'

        def to_vector(val):
            return val[0] == 'vector'

        def steps_of(val):
            return val[2] if len(val) > 2 else []

        def wrap_matrix(m, steps=None):
            return ('matrix', m, steps or [])

        def wrap_scalar(x, steps=None):
            return ('scalar', float(x), steps or [])

        def wrap_vector(v, steps=None):
            return ('vector', [float(x) for x in v], steps or [])

        def mat_add(x, y):
            if not (to_matrix(x) and to_matrix(y)):
                raise ValueError("La suma/resta sólo está definida entre matrices.")
            res, p = Matrices.add_with_steps(as_mat(x), as_mat(y))
            return wrap_matrix(res, steps_of(x) + steps_of(y) + p)

        def mat_sub(x, y):
            if not (to_matrix(x) and to_matrix(y)):
                raise ValueError("La suma/resta sólo está definida entre matrices.")
            res, p = Matrices.subtract_with_steps(as_mat(x), as_mat(y))
            return wrap_matrix(res, steps_of(x) + steps_of(y) + p)

        def vec_add(x, y):
            vx, vy = x[1], y[1]
            if len(vx) != len(vy):
                raise ValueError("Los vectores deben tener la misma longitud para suma/resta.")
            steps = [f"Sumando vectores de longitud {len(vx)}:"]
            res = []
            for i in range(len(vx)):
                s_val = float(vx[i]) + float(vy[i])
                steps.append(f"w[{i+1}] = {format_val(vx[i])} + {format_val(vy[i])} = {format_val(s_val)}")
                res.append(s_val)
            return wrap_vector(res, steps_of(x) + steps_of(y) + steps)

        def vec_sub(x, y):
            vx, vy = x[1], y[1]
            if len(vx) != len(vy):
                raise ValueError("Los vectores deben tener la misma longitud para suma/resta.")
            steps = [f"Restando vectores de longitud {len(vx)}:"]
            res = []
            for i in range(len(vx)):
                d_val = float(vx[i]) - float(vy[i])
                steps.append(f"w[{i+1}] = {format_val(vx[i])} - {format_val(vy[i])} = {format_val(d_val)}")
                res.append(d_val)
            return wrap_vector(res, steps_of(x) + steps_of(y) + steps)

        def mat_mul(x, y):
            if to_matrix(x) and to_matrix(y):
                res, p = Matrices.multiply_with_steps(as_mat(x), as_mat(y))
                return wrap_matrix(res, steps_of(x) + steps_of(y) + p)
            if to_matrix(x) and to_scalar(y):
                res, p = Matrices.multiply_scalar_with_steps(as_mat(x), as_scalar(y))
                return wrap_matrix(res, steps_of(x) + steps_of(y) + p)
            if to_scalar(x) and to_matrix(y):
                res, p = Matrices.multiply_scalar_with_steps(as_mat(y), as_scalar(x))
                return wrap_matrix(res, steps_of(x) + steps_of(y) + p)
            if to_matrix(x) and to_vector(y):
                col = [[float(v)] for v in y[1]]
                mat_res, p = Matrices.multiply_with_steps(as_mat(x), col)
                vec_res = [row[0] for row in mat_res]
                steps = p + ["Vector resultado (como columna):", Matrices._mat_to_str_frac(col),
                             "Vector resultado (plano):", "[ " + ", ".join(format_val(z) for z in vec_res) + " ]"]
                return wrap_vector(vec_res, steps_of(x) + steps_of(y) + steps)
            if to_scalar(x) and to_vector(y):
                k = as_scalar(x)
                vy = y[1]
                steps = [f"Escalando vector por {format_val(k)}:"]
                res = []
                for i, val in enumerate(vy):
                    r = k * float(val)
                    steps.append(f"w[{i+1}] = {format_val(k)}*{format_val(val)} = {format_val(r)}")
                    res.append(r)
                return wrap_vector(res, steps_of(x) + steps_of(y) + steps)
            if to_vector(x) and to_scalar(y):
                k = as_scalar(y)
                vx = x[1]
                steps = [f"Escalando vector por {format_val(k)}:"]
                res = []
                for i, val in enumerate(vx):
                    r = k * float(val)
                    steps.append(f"w[{i+1}] = {format_val(k)}*{format_val(val)} = {format_val(r)}")
                    res.append(r)
                return wrap_vector(res, steps_of(x) + steps_of(y) + steps)
            raise ValueError("Multiplicación inválida: no se admite escalar*escalar en expresiones matriciales.")

        def mat_transpose(x):
            if not to_matrix(x):
                if to_vector(x):
                    row = [x[1][:]]
                    steps = steps_of(x) + ["Transponiendo vector (columna -> fila):", Matrices._mat_to_str_frac([[v] for v in x[1]]),
                                            "Vector fila:", Matrices._mat_to_str_frac(row)]
                    return wrap_matrix(row, steps)
                raise ValueError("La transpuesta sólo aplica a matrices o vectores.")
            if hasattr(Matrices, 'transpose_with_steps'):
                t, p = Matrices.transpose_with_steps(as_mat(x))
                return wrap_matrix(t, steps_of(x) + p)
            else:
                t = Matrices.transpose(as_mat(x))
                return wrap_matrix(t, steps_of(x) + ["Transpuesta calculada."])

        def mat_inverse(x):
            if not to_matrix(x):
                raise ValueError("La inversa sólo aplica a matrices.")
            det_method = getattr(self, 'det_method_combo', None)
            det_method_sel = det_method.currentText() if det_method is not None else 'Eliminación'
            inv, p = Matrices.inverse_with_steps(as_mat(x), det_method=det_method_sel)
            return wrap_matrix(inv, steps_of(x) + p)

        def parse_factor():
            nonlocal i
            val = parse_primary()
            while True:
                skip_ws()
                if i < len(s) and s[i] == '^':
                    i += 1
                    skip_ws()
                    if i < len(s) and (s[i] in ('T', 't')):
                        i += 1
                        val = mat_transpose(val)
                        continue
                    if i < len(s) and s[i] == '-':
                        i += 1
                        if i < len(s) and s[i] == '1':
                            i += 1
                            val = mat_inverse(val)
                            continue
                        else:
                            raise ValueError("Se esperaba '^-1' para inversa.")
                    if i < len(s) and s[i] == '(':
                        i += 1
                        skip_ws()
                        if i < len(s) and s[i] == '-':
                            i += 1
                            if i < len(s) and s[i] == '1':
                                i += 1
                                skip_ws()
                                if i < len(s) and s[i] == ')':
                                    i += 1
                                    val = mat_inverse(val)
                                    continue
                        raise ValueError("Se esperaba '^(-1)' para inversa.")
                    raise ValueError("Operador '^' no reconocido. Use '^T' o '^-1'.")
                break
            return val

        def parse_unary():
            if peek() == '-':
                consume('-')
                val = parse_unary()
                if to_matrix(val):
                    res, p = Matrices.multiply_scalar_with_steps(as_mat(val), -1.0)
                    return wrap_matrix(res, steps_of(val) + p)
                if to_scalar(val):
                    return wrap_scalar(-as_scalar(val), steps_of(val) + ["Aplicando signo unario a escalar"])
                if to_vector(val):
                    k = -1.0
                    vx = val[1]
                    steps = ["Aplicando signo unario a vector:"]
                    res = []
                    for i, v in enumerate(vx):
                        r = -float(v)
                        steps.append(f"w[{i+1}] = -1*{format_val(v)} = {format_val(r)}")
                        res.append(r)
                    return wrap_vector(res, steps_of(val) + steps)
                raise ValueError("Signo unario inválido.")
            return parse_factor()

        def parse_term():
            val = parse_unary()
            while True:
                if peek() == '*':
                    consume('*')
                    rhs = parse_unary()
                    val = mat_mul(val, rhs)
                else:
                    break
            return val

        def parse_expr():
            val = parse_term()
            while True:
                c = peek()
                if c == '+':
                    consume('+')
                    rhs = parse_term()
                    if to_matrix(val) and to_matrix(rhs):
                        val = mat_add(val, rhs)
                    elif to_vector(val) and to_vector(rhs):
                        val = vec_add(val, rhs)
                    else:
                        raise ValueError("La suma sólo está definida entre dos matrices o dos vectores del mismo tamaño.")
                elif c == '-':
                    consume('-')
                    rhs = parse_term()
                    if to_matrix(val) and to_matrix(rhs):
                        val = mat_sub(val, rhs)
                    elif to_vector(val) and to_vector(rhs):
                        val = vec_sub(val, rhs)
                    else:
                        raise ValueError("La resta sólo está definida entre dos matrices o dos vectores del mismo tamaño.")
                else:
                    break
            return val

        result = parse_expr()
        if i < len(s):
            raise ValueError(f"Símbolo inesperado cerca de '{s[i:]}'")
        if result[0] == 'scalar':
            raise ValueError("La expresión resultó en un escalar; se esperaba una matriz o un vector.")
        used = {'matrices': used_mats, 'vectores': used_vecs}
        return result[1], steps_of(result), used

    def multiply_selected(self):
        a_name = self.sel_a.text().strip()
        b_name = self.sel_b.text().strip()
        if not a_name or not b_name:
            QMessageBox.warning(self, "Error", "Proporciona ambos nombres A y B.")
            return
        saved = Matrices.load_saved_matrices()
        if a_name not in saved:
            QMessageBox.warning(self, "Error", f"No existe la matriz A: {a_name}")
            return
        if b_name not in saved:
            QMessageBox.warning(self, "Error", f"No existe la matriz B: {b_name}")
            return
        a = saved[a_name]
        b = saved[b_name]
        try:
            res, pasos = Matrices.multiply_with_steps(a, b)
            full_out = pasos + ["Resultado:", Matrices._mat_to_str_frac(res)]
            compact_out = "Resultado:\n" + Matrices._mat_to_str_frac(res)
            self._store_and_render("\n".join(full_out), compact_out)
            reply = QMessageBox.question(self, "Guardar resultado", f"¿Guardar resultado como '{a_name}_x_{b_name}'?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                Matrices.save_matrix(f"{a_name}_x_{b_name}", res)
                self.reload_saved()
        except Exception as e:
            QMessageBox.critical(self, "Error al multiplicar", str(e))

    def operate_selected(self):
        """Ejecuta la operación seleccionada en el combo sobre las matrices guardadas."""
        op = self.op_combo.currentText()
        a_name = self.sel_a.text().strip()
        b_name = self.sel_b.text().strip()
        saved = Matrices.load_saved_matrices()

        if op == "Determinante":
            if not a_name:
                QMessageBox.warning(self, "Error", "Proporciona el nombre de la matriz A en el campo 'A (nombre)'.")
                return
            if a_name not in saved:
                QMessageBox.warning(self, "Error", f"No existe la matriz A: {a_name}")
                return
            a = saved[a_name]
            try:
                method = self.det_method_combo.currentText()
                if method == "Eliminación":
                    det, pasos = Matrices.determinant_with_steps(a)
                elif method == "Cofactores":
                    det, pasos = Matrices.determinant_cofactor_with_steps(a)
                elif method == "Sarrus":
                    if len(a) != 3 or any(len(row) != 3 for row in a):
                        QMessageBox.warning(self, "Error", "Sarrus aplica sólo a matrices 3x3.")
                        return
                    det, pasos = Matrices.determinant_sarrus_with_steps(a)
                elif method == "Cramer":
                    det, pasos = Matrices.determinant_cramer_with_steps(a)
                else:
                    QMessageBox.warning(self, "Error", f"Método desconocido: {method}")
                    return
                full_out = pasos + [f"det(A) = {format_val(det)}"]
                compact_out = f"det(A) = {format_val(det)}"
                self._store_and_render("\n".join(full_out), compact_out)
            except Exception as e:
                QMessageBox.critical(self, "Error al calcular determinante", str(e))
            return

        if op in ("Multiplicar", "Sumar", "Restar"):
            if not a_name or not b_name:
                QMessageBox.warning(self, "Error", "Proporciona ambos nombres A y B.")
                return
            if a_name not in saved:
                QMessageBox.warning(self, "Error", f"No existe la matriz A: {a_name}")
                return
            if b_name not in saved:
                QMessageBox.warning(self, "Error", f"No existe la matriz B: {b_name}")
                return
            a = saved[a_name]
            b = saved[b_name]
        else:
            QMessageBox.warning(self, "Error", f"Operación desconocida: {op}")
            return
        try:
            if op == "Multiplicar":
                res, pasos = Matrices.multiply_with_steps(a, b)
                full_out = pasos + ["Resultado:", Matrices._mat_to_str_frac(res)]
                compact_out = "Resultado:\n" + Matrices._mat_to_str_frac(res)
                self._store_and_render("\n".join(full_out), compact_out)
                default_name = f"{a_name}_x_{b_name}"
            elif op == "Sumar":
                res, pasos = Matrices.add_with_steps(a, b)
                full_out = pasos + ["Resultado:", Matrices._mat_to_str_frac(res)]
                compact_out = "Resultado:\n" + Matrices._mat_to_str_frac(res)
                self._store_and_render("\n".join(full_out), compact_out)
                default_name = f"{a_name}_plus_{b_name}"
            elif op == "Restar":
                res, pasos = Matrices.subtract_with_steps(a, b)
                full_out = pasos + ["Resultado:", Matrices._mat_to_str_frac(res)]
                compact_out = "Resultado:\n" + Matrices._mat_to_str_frac(res)
                self._store_and_render("\n".join(full_out), compact_out)
                default_name = f"{a_name}_minus_{b_name}"
            else:
                QMessageBox.warning(self, "Error", f"Operación desconocida: {op}")
                return
            text, ok = QInputDialog.getText(self, "Guardar resultado",
                                            "Nombre para guardar (puedes editar):",
                                            QLineEdit.EchoMode.Normal,
                                            default_name)
            if ok:
                final_name = text.strip() or default_name
                try:
                    Matrices.save_matrix(final_name, res)
                    self.reload_saved()
                except Exception as e:
                    QMessageBox.critical(self, "Error al guardar", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def multiply_by_scalar_selected(self):
        name = self.sel_a.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Proporciona el nombre de la matriz A en el campo 'A (nombre)'.")
            return
        saved = Matrices.load_saved_matrices()
        if name not in saved:
            QMessageBox.warning(self, "Error", f"No existe la matriz: {name}")
            return
        try:
            scalar_txt = self.scalar_input.text().strip()
            if scalar_txt == "":
                raise ValueError("Introduce un escalar válido.")
            from fractions import Fraction
            if '/' in scalar_txt:
                scalar = float(Fraction(scalar_txt))
            else:
                scalar = float(scalar_txt)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Escalar no válido: {e}")
            return
        a = saved[name]
        try:
            res, pasos = Matrices.multiply_scalar_with_steps(a, scalar)
            full_out = pasos + ["Resultado:", Matrices._mat_to_str_frac(res)]
            compact_out = "Resultado:\n" + Matrices._mat_to_str_frac(res)
            self._store_and_render("\n".join(full_out), compact_out)
            scalar_label = format_val(scalar)
            scalar_fname = scalar_label.replace('/', '_')
            default_name = f"{name}_x_{scalar_fname}"
            text, ok = QInputDialog.getText(self, "Guardar resultado",
                                            "Nombre para guardar (puedes editar):",
                                            QLineEdit.EchoMode.Normal,
                                            default_name)
            if ok:
                final_name = text.strip() or default_name
                Matrices.save_matrix(final_name, res)
                self.reload_saved()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def delete_selected(self):
        items = self.list_widget.selectedItems()
        if not items:
            QMessageBox.warning(self, "Error", "Selecciona una o más matrices a eliminar.")
            return
        names = [self._get_name_from_list_item(it.text()) for it in items]
        lista_nombres = "\n".join(names)
        reply = QMessageBox.question(self, "Confirmar eliminación",
                                     f"Eliminar las siguientes matrices?\n{lista_nombres}",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            for name in names:
                try:
                    Matrices.delete_saved_matrix(name)
                except Exception as e:
                    self.result_text.append(f"Error eliminando '{name}': {e}")
            self.reload_saved()
            msg = f"Matrices eliminadas:\n{lista_nombres}"
            self._store_and_render(msg, msg)

    def _toggle_list_item_at_pos(self, pos):
        item = self.list_widget.itemAt(pos)
        if item is None:
            return
        item.setSelected(not item.isSelected())

    def _delete_selected_vector(self):
        items = self.vectors_list.selectedItems()
        if not items:
            QMessageBox.warning(self, 'Error', 'Selecciona uno o más vectores a eliminar.')
            return
        names = [it.text().split('  ')[0] for it in items]
        lista = "\n".join(names)
        reply = QMessageBox.question(self, 'Confirmar eliminación', f"Eliminar los siguientes vectores?\n{lista}",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            for name in names:
                try:
                    delete_saved_vector(name)
                except Exception as e:
                    self.result_text.append(f"Error eliminando '{name}': {e}")
            self.saved_vectors = load_saved_vectors()
            self.vectors_list.clear()
            for nm, vec in sorted(self.saved_vectors.items()):
                self.vectors_list.addItem(f"{nm}  ({len(vec)})")
            msg = f"Vectores eliminados:\n{lista}"
            self._store_and_render(msg, msg)

    def _toggle_vector_item_at_pos(self, pos):
        item = self.vectors_list.itemAt(pos)
        if item is None:
            return
        item.setSelected(not item.isSelected())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = OperacionesMatricesGui()
    w.showFullScreen()
    sys.exit(app.exec())