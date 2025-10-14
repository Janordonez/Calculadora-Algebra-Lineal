import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from typing import List
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QListWidget, QMessageBox, QGridLayout, QTextEdit, QGroupBox, QSizePolicy, QInputDialog
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from models.Matrices import Matrices
from models.Vectores import load_saved_vectors, save_vector, delete_saved_vector


class OperacionesMatricesGui(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Operaciones con Matrices")
        self.resize(900, 600)

        # Tema y estilo
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
        self.btn_generate = QPushButton("Generar campos")
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
        self.btn_save = QPushButton("Guardar matriz")
        self.btn_save.clicked.connect(self.save_matrix)
        acciones_layout.addWidget(self.btn_save)
        self.btn_show = QPushButton("Mostrar seleccionada")
        self.btn_show.clicked.connect(self.show_selected)
        acciones_layout.addWidget(self.btn_show)
        self.btn_transpose = QPushButton("Transponer seleccionada")
        self.btn_transpose.clicked.connect(self.transpose_selected)
        acciones_layout.addWidget(self.btn_transpose)
        self.btn_delete = QPushButton("Eliminar seleccionada")
        self.btn_delete.clicked.connect(self.delete_selected)
        acciones_layout.addWidget(self.btn_delete)
        layout.addWidget(acciones_group)

        # Panel de operaciones y lista (grupo)
        panel_group = QGroupBox("Matrices guardadas y operaciones")
        panel_layout = QHBoxLayout()
        panel_group.setLayout(panel_layout)

        left = QVBoxLayout()
        left.addWidget(QLabel("Matrices guardadas:"))
        self.list_widget = QListWidget()
        self.list_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        left.addWidget(self.list_widget)
        # lista de vectores guardados
        left.addWidget(QLabel("Vectores guardados:"))
        self.vectors_list = QListWidget()
        self.vectors_list.setFixedWidth(200)
        left.addWidget(self.vectors_list)
        # boton para eliminar vector seleccionado
        self.btn_delete_vector = QPushButton("Eliminar vector")
        self.btn_delete_vector.clicked.connect(self._delete_selected_vector)
        left.addWidget(self.btn_delete_vector)
        panel_layout.addLayout(left, 1)

        right = QVBoxLayout()
        # selección para multiplicar
        sel_layout = QHBoxLayout()
        sel_layout.addWidget(QLabel("A (nombre):"))
        self.sel_a = QLineEdit()
        self.sel_a.setFixedWidth(120)
        sel_layout.addWidget(self.sel_a)
        sel_layout.addWidget(QLabel("B (nombre):"))
        self.sel_b = QLineEdit()
        self.sel_b.setFixedWidth(120)
        sel_layout.addWidget(self.sel_b)
        self.btn_mult = QPushButton("Multiplicar A x B")
        self.btn_mult.clicked.connect(self.multiply_selected)
        sel_layout.addWidget(self.btn_mult)
        right.addLayout(sel_layout)

        # segunda fila: controles de vector y escalar para evitar solapamiento
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
        # botón para multiplicar usando vector guardado seleccionado
        self.btn_mult_saved_vec = QPushButton("A x vec guard.")
        self.btn_mult_saved_vec.clicked.connect(self.multiply_matrix_by_saved_vector)
        vec_layout.addWidget(self.btn_mult_saved_vec)
        vec_layout.addStretch()
        vec_layout.addWidget(QLabel("Escalar:"))
        self.scalar_input = QLineEdit()
        self.scalar_input.setFixedWidth(100)
        self.scalar_input.setPlaceholderText("ej: 2.5")
        vec_layout.addWidget(self.scalar_input)
        self.btn_scalar = QPushButton("A * escalar")
        self.btn_scalar.clicked.connect(self.multiply_by_scalar_selected)
        vec_layout.addWidget(self.btn_scalar)
        right.addLayout(vec_layout)

        right.addWidget(QLabel("Resultado / Mensajes:"))
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setFixedHeight(220)
        right.addWidget(self.result_text, 1)

        panel_layout.addLayout(right, 2)

        layout.addWidget(panel_group)

        self.setLayout(layout)

        self.reload_saved()

    def generate_fields(self):
        try:
            r = int(self.rows_input.text())
            c = int(self.cols_input.text())
            if r <= 0 or c <= 0:
                raise ValueError()
        except Exception:
            QMessageBox.warning(self, "Error", "Filas y columnas deben ser enteros positivos.")
            return
        # limpiar grid previo
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
            self.result_text.setPlainText(f"Matriz '{name}' guardada correctamente.")
            self.reload_saved()
        except Exception as e:
            QMessageBox.critical(self, "Error al guardar", str(e))

    def reload_saved(self):
        self.list_widget.clear()
        saved = Matrices.load_saved_matrices()
        for k in sorted(saved.keys()):
            rows = len(saved[k])
            cols = len(saved[k][0]) if rows>0 else 0
            self.list_widget.addItem(f"{k}  ({rows}x{cols})")
        # cargar vectores guardados en la lista y en memoria
        self.saved_vectors = load_saved_vectors()
        self.vectors_list.clear()
        for name, vec in sorted(self.saved_vectors.items()):
            self.vectors_list.addItem(f"{name}  ({len(vec)})")
        # conectar doble clic para cargar vector en el input
        self.vectors_list.itemDoubleClicked.connect(self._load_vector_into_input)

    def ir_a_menu(self):
        try:
            from gui.MenuGui import MenuGui
            self.menu = MenuGui()
            self.menu.show()
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir MenuGui:\n{e}")

    def _get_name_from_list_item(self, item_text: str) -> str:
        # formato: "name  (RxC)"
        return item_text.split('  ')[0]

    def show_selected(self):
        """Muestra la matriz seleccionada en el área de resultado y ofrece volcarla a los campos de entrada."""
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
        # mostrar en el cuadro de texto
        txt = f"Matriz '{name}' ({len(mat)}x{len(mat[0]) if mat else 0}):\n"
        for row in mat:
            txt += "[ " + ", ".join(str(x) for x in row) + " ]\n"
        self.result_text.setPlainText(txt)

        # opcional: volcar a campos de entrada
        r = len(mat)
        c = len(mat[0]) if r>0 else 0
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
            vals = [float(p) for p in parts]
            return vals
        except Exception:
            raise ValueError('Formato de vector inválido. Usa números separados por comas.')

    def multiply_matrix_by_vector(self):
        # Usa la matriz A indicada en self.sel_a o la matriz seleccionada en la lista
        a_name = self.sel_a.text().strip()
        if not a_name:
            # intentar usar la matriz seleccionada
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
        # parsear vector
        vec_txt = self.vector_input.text().strip()
        if not vec_txt:
            QMessageBox.warning(self, 'Error', 'Introduce un vector en el campo correspondiente.')
            return
        try:
            v = self._parse_vector_text(vec_txt)
        except Exception as e:
            QMessageBox.warning(self, 'Error', str(e))
            return
        # verificar compatibilidad: A (n x m) * v (m) -> result n
        if not a:
            QMessageBox.warning(self, 'Error', 'Matriz A vacía.')
            return
        m = len(a[0])
        if len(v) != m:
            QMessageBox.warning(self, 'Error', f'Dimensiones incompatibles: A tiene {m} columnas, el vector tiene {len(v)} componentes.')
            return
        # convertir vector a formato columna (mx1) y usar multiply_with_steps
        b = [[float(x)] for x in v]
        try:
            res, pasos = Matrices.multiply_with_steps(a, b)
            # res es n x 1
            pasos.append('Resultado vector columna:')
            pasos.append('\n'.join(str(row[0]) for row in res))
            self.result_text.setPlainText('\n'.join(pasos))
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
            # refrescar lista visual
            self.vectors_list.clear()
            for nm, vec in sorted(self.saved_vectors.items()):
                self.vectors_list.addItem(f"{nm}  ({len(vec)})")
            self.result_text.setPlainText(f"Vector '{name.strip()}' guardado.")
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
            self.result_text.setPlainText(f"Vector '{name}' eliminado.")

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
        # usar la matriz A indicada o seleccionada
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
            pasos.append('\n'.join(str(row[0]) for row in res))
            self.result_text.setPlainText('\n'.join(pasos))
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
            t, pasos = Matrices.transpose_with_steps(mat)
            self.result_text.setPlainText("\n".join(pasos))
            reply = QMessageBox.question(self, "Guardar transpuesta", f"¿Guardar transpuesta como '{name}_T'?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                Matrices.save_matrix(f"{name}_T", t)
                self.reload_saved()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

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
            self.result_text.setPlainText("\n".join(pasos))
            reply = QMessageBox.question(self, "Guardar resultado", f"¿Guardar resultado como '{a_name}_x_{b_name}'?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                Matrices.save_matrix(f"{a_name}_x_{b_name}", res)
                self.reload_saved()
        except Exception as e:
            QMessageBox.critical(self, "Error al multiplicar", str(e))

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
            scalar = float(scalar_txt)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Escalar no válido: {e}")
            return
        a = saved[name]
        try:
            res = Matrices.multiply_scalar(a, scalar)
            txt = f"Resultado {name} * {scalar}:\n" + '\n'.join(str(r) for r in res)
            self.result_text.setPlainText(txt)
            reply = QMessageBox.question(self, "Guardar resultado", f"¿Guardar resultado como '{name}_x_{scalar}'?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                Matrices.save_matrix(f"{name}_x_{scalar}", res)
                self.reload_saved()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def delete_selected(self):
        item = self.list_widget.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Selecciona una matriz a eliminar.")
            return
        name = self._get_name_from_list_item(item.text())
        reply = QMessageBox.question(self, "Confirmar eliminación", f"Eliminar '{name}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            Matrices.delete_saved_matrix(name)
            self.reload_saved()
            self.result_text.setPlainText(f"Matriz '{name}' eliminada.")

    def _delete_selected_vector(self):
        item = self.vectors_list.currentItem()
        if not item:
            QMessageBox.warning(self, 'Error', 'Selecciona un vector a eliminar.')
            return
        name = item.text().split('  ')[0]
        reply = QMessageBox.question(self, 'Confirmar eliminación', f"Eliminar '{name}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            delete_saved_vector(name)
            self.reload_saved()
            self.result_text.setPlainText(f"Vector '{name}' eliminado.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = OperacionesMatricesGui()
    w.showFullScreen()
    sys.exit(app.exec())

