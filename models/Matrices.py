from typing import List, Tuple, Dict, Any
from fractions import Fraction
import json
import os

EPS = 1e-10

class GaussResult:
    def __init__(self, pasos: List[str], augmented: List[List[float]], pivotes: List[Tuple[int,int]]):
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
                for j in range(m+1):
                    augmented[col][j] /= piv
                pasos.append(f"f{col+1} --> (1/{piv:.4f})*f{col+1}")
                pasos.append(Matrices._mat_to_str(augmented))
            for row in range(col+1, n):
                factor = augmented[row][col]
                if abs(factor) > EPS:
                    for j in range(m+1):
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
                for j in range(m+1):
                    augmented[row][j] /= piv
                pasos.append(f"f{row+1} --> (1/{piv:.4f})*f{row+1}")
                pasos.append(Matrices._mat_to_str(augmented))
            for r in range(n):
                if r != row and abs(augmented[r][col]) > EPS:
                    factor = augmented[r][col]
                    for j in range(m+1):
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
        usados = set([c for c in pivote_col if c != -1])
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

    # -------------------- Nuevas utilidades --------------------
    @staticmethod
    def multiply(a: List[List[float]], b: List[List[float]]) -> List[List[float]]:
        """Multiplica dos matrices a (n x m) y b (m x p) devolviendo (n x p)."""
        if not a or not b:
            raise ValueError("Ambas matrices deben ser no vacías.")
        n = len(a)
        m = len(a[0])
        if any(len(row) != m for row in a):
            raise ValueError("Todas las filas de A deben tener la misma longitud.")
        mb = len(b)
        pb = len(b[0])
        if any(len(row) != pb for row in b):
            raise ValueError("Todas las filas de B deben tener la misma longitud.")
        if m != mb:
            raise ValueError(f"Dimensiones incompatibles: A es {n}x{m} pero B es {mb}x{pb}.")
        # resultado n x p
        res = [[0.0 for _ in range(pb)] for _ in range(n)]
        for i in range(n):
            for j in range(pb):
                s = 0.0
                for k in range(m):
                    s += a[i][k] * b[k][j]
                res[i][j] = s
        return res

    @staticmethod
    def transpose(a: List[List[float]]) -> List[List[float]]:
        """Devuelve la transpuesta de A."""
        if not a:
            return []
        m = len(a[0])
        if any(len(row) != m for row in a):
            raise ValueError("Todas las filas de A deben tener la misma longitud.")
        return [[a[r][c] for r in range(len(a))] for c in range(m)]

    @staticmethod
    def _get_storage_path() -> str:
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        data_dir = os.path.join(base, 'data')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
        return os.path.join(data_dir, 'matrices.json')

    @staticmethod
    def load_saved_matrices() -> dict:
        """Carga todas las matrices guardadas desde data/matrices.json -> dict nombre -> matrix"""
        path = Matrices._get_storage_path()
        if not os.path.exists(path):
            return {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # validar estructura esperada: dict nombre -> lista de filas
            res = {}
            for k, v in data.items():
                # convertir elementos a float
                res[k] = [[float(x) for x in row] for row in v]
            return res
        except Exception:
            return {}

    @staticmethod
    def save_matrix(name: str, matrix: List[List[float]]):
        """Guarda (o sobrescribe) una matriz con el nombre proporcionado en el archivo JSON."""
        if not name or not isinstance(name, str):
            raise ValueError("El nombre debe ser una cadena no vacía.")
        path = Matrices._get_storage_path()
        cur = Matrices.load_saved_matrices()
        cur[name] = matrix
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(cur, f, indent=2)

    @staticmethod
    def delete_saved_matrix(name: str):
        path = Matrices._get_storage_path()
        cur = Matrices.load_saved_matrices()
        if name in cur:
            del cur[name]
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(cur, f, indent=2)

    @staticmethod
    def multiply_scalar(a: List[List[float]], scalar: float) -> List[List[float]]:
        """Multiplica cada elemento de la matriz por el escalar dado."""
        if not a:
            raise ValueError("La matriz no puede estar vacía.")
        m = len(a[0])
        if any(len(row) != m for row in a):
            raise ValueError("Todas las filas de la matriz deben tener la misma longitud.")
        return [[float(x) * float(scalar) for x in row] for row in a]