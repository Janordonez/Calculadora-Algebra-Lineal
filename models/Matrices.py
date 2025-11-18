from typing import List, Tuple, Dict, Any
from fractions import Fraction
import os
import json

EPS = 1e-10


class GaussResult:
    def __init__(self, pasos: List[str], augmented: List[List[float]], pivotes: List[Tuple[int, int]]):
        self.pasos = pasos
        self.augmented = augmented
        self.pivotes = pivotes


def format_val(x):
    if abs(x) < EPS:
        return "0"
    elif x == int(x):
        return str(int(x))
    else:
        return str(Fraction(x).limit_denominator())


class Matrices:
    """
    Clase que contiene:
      - Métodos para Gauss y Gauss-Jordan (lo que ya tenías).
      - Métodos para manejo de matrices guardadas en disco
        (usados por OperacionesMatricesGui):
          * save_matrix / load_saved_matrices / delete_saved_matrix
          * transpose / multiply / multiply_scalar
    """

    # Archivo JSON donde se guardan las matrices para OperacionesMatricesGui
    DATA_FILE = os.path.join(os.path.dirname(__file__), "saved_matrices.json")

    # =========================================================
    #   SECCIÓN 1: GAUSS Y GAUSS-JORDAN (TU CÓDIGO ORIGINAL)
    # =========================================================
    @staticmethod
    def _validate_a_b(a: List[List[float]], b: List[List[float]]):
        if not isinstance(a, list) or not a or not isinstance(b, list) or not b:
            raise ValueError("Las matrices A y B no pueden estar vacías.")
        m = len(a[0])
        if any(len(row) != m for row in a):
            raise ValueError("Todas las filas de A deben tener la misma longitud.")
        if len(b) != len(a):
            raise ValueError("El número de filas de B debe coincidir con A.")
        if any(len(row) != 1 for row in b):
            raise ValueError("B debe ser un vector columna (nx1).")
        if m < 2:
            raise ValueError("A debe tener al menos 2 columnas (2 incógnitas).")

    @staticmethod
    def gauss(a: List[List[float]], b: List[List[float]]) -> GaussResult:
        Matrices._validate_a_b(a, b)
        n = len(a)
        m = len(a[0])
        augmented = [a[i][:] + b[i][:] for i in range(n)]
        pasos = []
        pivotes = []
        for col in range(min(n, m)):
            max_row = max(range(col, n), key=lambda r: abs(augmented[r][col]))
            if abs(augmented[max_row][col]) < EPS:
                pasos.append(f"No hay pivote en columna {col+1}, se salta.")
                continue
            if max_row != col:
                augmented[col], augmented[max_row] = augmented[max_row], augmented[col]
                pasos.append(f"Intercambio de fila {col+1} con fila {max_row+1}")
            pivotes.append((col, col))
            piv = augmented[col][col]
            if abs(piv - 1) > EPS:
                for j in range(m + 1):
                    augmented[col][j] /= piv
                pasos.append(f"f{col+1} --> (1/{piv:.4f})*f{col+1}")
                pasos.append(Matrices._mat_to_str(augmented))
            for row in range(col + 1, n):
                factor = augmented[row][col]
                if abs(factor) > EPS:
                    for j in range(m + 1):
                        augmented[row][j] -= factor * augmented[col][j]
                    signo = "+" if factor > 0 else "-"
                    pasos.append(f"f{row+1} --> f{row+1} {signo} ({abs(factor):.4f})*f{col+1}")
                    pasos.append(Matrices._mat_to_str(augmented))
        pasos.append("Estado final:\n" + Matrices._mat_to_str(augmented))
        return GaussResult(pasos, augmented, pivotes)

    @staticmethod
    def gauss_jordan(a: List[List[float]], b: List[List[float]]) -> GaussResult:
        Matrices._validate_a_b(a, b)
        n = len(a)
        m = len(a[0])
        augmented = [a[i][:] + b[i][:] for i in range(n)]
        pasos = []
        pivotes = []
        row = 0
        for col in range(m):
            sel = None
            for r in range(row, n):
                if abs(augmented[r][col]) > EPS:
                    sel = r
                    break
            if sel is None:
                pasos.append(f"No hay pivote en columna {col+1}, se salta.")
                continue
            if sel != row:
                augmented[row], augmented[sel] = augmented[sel], augmented[row]
                pasos.append(f"Intercambio de fila {row+1} con fila {sel+1}")
                pasos.append(Matrices._mat_to_str(augmented))
            pivotes.append((row, col))
            piv = augmented[row][col]
            if abs(piv - 1) > EPS:
                for j in range(m + 1):
                    augmented[row][j] /= piv
                pasos.append(f"f{row+1} --> (1/{piv:.4f})*f{row+1}")
                pasos.append(Matrices._mat_to_str(augmented))
            for r in range(n):
                if r != row and abs(augmented[r][col]) > EPS:
                    factor = augmented[r][col]
                    for j in range(m + 1):
                        augmented[r][j] -= factor * augmented[row][j]
                    signo = "+" if factor > 0 else "-"
                    pasos.append(f"f{r+1} --> f{r+1} {signo} ({abs(factor):.4f})*f{row+1}")
                    pasos.append(Matrices._mat_to_str(augmented))
            row += 1
            if row == n:
                break
        pasos.append("Estado final:\n" + Matrices._mat_to_str(augmented))
        return GaussResult(pasos, augmented, pivotes)

    @staticmethod
    def clasificar_y_resolver_from_rref(gauss_result: GaussResult) -> Dict[str, Any]:
        mat = gauss_result.augmented
        n = len(mat)
        m = len(mat[0]) - 1
        tipo = "determinada"
        solucion = [0.0] * m
        libres = []
        for row in mat:
            if all(abs(x) < EPS for x in row[:-1]) and abs(row[-1]) > EPS:
                return {"tipo": "incompatible"}
        pivote_col = [-1] * n
        for i in range(n):
            for j in range(m):
                if abs(mat[i][j]) > EPS:
                    pivote_col[i] = j
                    break
        usados = set(c for c in pivote_col if c != -1)
        libres = [j for j in range(m) if j not in usados]
        if len(usados) < m:
            tipo = "indeterminada"
        if tipo == "determinada":
            for i in range(n):
                if pivote_col[i] != -1:
                    solucion[pivote_col[i]] = mat[i][-1]
            return {"tipo": tipo, "solucion": solucion, "libres": libres}
        else:
            return {"tipo": tipo, "solucion_parametrica": ["paramétrica"], "libres": libres}

    @staticmethod
    def _mat_to_str(mat: List[List[float]]) -> str:
        # Formato tipo [1.0000 | 0.0625 | ... ]
        return "\n".join(
            " | ".join(f"{x:8.4f}" for x in row)
            for row in mat
        )

    # =========================================================
    #   SECCIÓN 2: MANEJO DE MATRICES GUARDADAS Y OPERACIONES
    #   (USADAS POR OperacionesMatricesGui)
    # =========================================================
    @staticmethod
    def _ensure_rectangular(mat: List[List[float]]) -> None:
        """Verifica que la matriz sea rectangular."""
        if not mat:
            raise ValueError("La matriz está vacía.")
        cols = len(mat[0])
        for i, row in enumerate(mat):
            if len(row) != cols:
                raise ValueError(
                    f"La matriz no es rectangular. "
                    f"La fila {i+1} tiene longitud distinta."
                )

    @classmethod
    def _load_file(cls) -> Dict[str, Any]:
        """Carga el archivo JSON donde se guardan las matrices."""
        if not os.path.exists(cls.DATA_FILE):
            return {}
        try:
            with open(cls.DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                return {}
            return data
        except Exception:
            return {}

    @classmethod
    def _save_file(cls, data: Dict[str, Any]) -> None:
        """Guarda el diccionario de matrices en el archivo JSON."""
        with open(cls.DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # ---------- API pública para la GUI de Operaciones ---------- #
    @classmethod
    def load_saved_matrices(cls) -> Dict[str, List[List[float]]]:
        """
        Devuelve un diccionario {nombre: matriz}.
        Cada matriz es una lista de listas de floats.
        """
        data = cls._load_file()
        result: Dict[str, List[List[float]]] = {}
        for name, mat in data.items():
            if isinstance(mat, list):
                result[name] = mat
        return result

    @classmethod
    def save_matrix(cls, name: str, matrix: List[List[float]]) -> None:
        """
        Guarda o sobreescribe una matriz en el archivo JSON.
        """
        if not name:
            raise ValueError("El nombre de la matriz no puede estar vacío.")
        cls._ensure_rectangular(matrix)
        data = cls._load_file()
        data[name] = matrix
        cls._save_file(data)

    @classmethod
    def delete_saved_matrix(cls, name: str) -> None:
        """
        Elimina una matriz guardada (si existe).
        """
        data = cls._load_file()
        if name in data:
            del data[name]
            cls._save_file(data)

    @staticmethod
    def transpose(matrix: List[List[float]]) -> List[List[float]]:
        """
        Devuelve la transpuesta de una matriz.
        """
        Matrices._ensure_rectangular(matrix)
        if not matrix:
            return []
        rows = len(matrix)
        cols = len(matrix[0])
        return [[matrix[i][j] for i in range(rows)] for j in range(cols)]

    @staticmethod
    def multiply(A: List[List[float]], B: List[List[float]]) -> List[List[float]]:
        """
        Multiplicación de matrices A (m x n) y B (n x p).
        """
        Matrices._ensure_rectangular(A)
        Matrices._ensure_rectangular(B)

        m = len(A)
        n = len(A[0])
        n2 = len(B)
        p = len(B[0])

        if n != n2:
            raise ValueError(
                f"No se puede multiplicar: A es {m}x{n} y B es {n2}x{p}. "
                "Las columnas de A deben coincidir con las filas de B."
            )

        result = [[0.0 for _ in range(p)] for _ in range(m)]
        for i in range(m):
            for j in range(p):
                s = 0.0
                for k in range(n):
                    s += A[i][k] * B[k][j]
                result[i][j] = s
        return result

    @staticmethod
    def multiply_scalar(A: List[List[float]], scalar: float) -> List[List[float]]:
        """
        Multiplica una matriz por un escalar.
        """
        Matrices._ensure_rectangular(A)
        return [[scalar * x for x in row] for row in A]
