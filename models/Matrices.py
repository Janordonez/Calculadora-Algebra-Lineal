from typing import List, Tuple, Dict, Any, Optional
from fractions import Fraction
import json
import os
import copy

EPS = 1e-10

class GaussResult:
    def __init__(self, pasos: List[str], augmented: List[List[float]], pivotes: List[Tuple[int, int]]):
        self.pasos = pasos
        self.augmented = augmented
        self.pivotes = pivotes

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

class Matrices:
    @staticmethod
    def _is_identity(mat: List[List[float]], tol: float = 1e-8) -> bool:
        if not mat:
            return False
        n = len(mat)
        m = len(mat[0])
        if n != m:
            return False
        for i in range(n):
            for j in range(m):
                if i == j:
                    if abs(mat[i][j] - 1.0) > tol:
                        return False
                else:
                    if abs(mat[i][j]) > tol:
                        return False
        return True

    @staticmethod
    def _aug_to_str(aug: List[List[float]], split: int) -> str:
        lines = []
        for i in range(len(aug)):
            left = " ".join(f"{aug[i][j]:8.4f}" for j in range(split))
            right = " ".join(f"{aug[i][j]:8.4f}" for j in range(split, len(aug[i])))
            lines.append(f"[ {left} | {right} ]")
        return "\n".join(lines)

    @staticmethod
    def _mat_to_str_frac(mat: List[List[float]]) -> str:
        return "\n".join(
            "[ " + " ".join(format_val(x) for x in row) + " ]" for row in mat
        )

    @staticmethod
    def _aug_to_str_frac(aug: List[List[float]], split: int) -> str:
        lines = []
        for i in range(len(aug)):
            left = " ".join(format_val(aug[i][j]) for j in range(split))
            right = " ".join(format_val(aug[i][j]) for j in range(split, len(aug[i])))
            lines.append(f"[ {left} | {right} ]")
        return "\n".join(lines)

    @staticmethod
    def _mat_side_by_side_equal(lhs: List[List[float]], rhs: List[List[float]]) -> str:
        if not lhs or not rhs:
            return ""
        if len(lhs) != len(rhs) or len(lhs[0]) != len(rhs[0]):
            l = Matrices._mat_to_str_frac(lhs)
            r = Matrices._mat_to_str_frac(rhs)
            return l + "\n=\n" + r
        left_rows = ["[ " + " ".join(format_val(x) for x in row) + " ]" for row in lhs]
        right_rows = ["[ " + " ".join(format_val(x) for x in row) + " ]" for row in rhs]
        width = max(len(s) for s in left_rows) if left_rows else 0
        lines = []
        for i in range(len(left_rows)):
            lines.append(left_rows[i].ljust(width) + "  =  " + right_rows[i])
        return "\n".join(lines)

    @staticmethod
    def _identity_with_steps(n: int) -> Tuple[List[List[float]], List[str]]:
        I = [[0.0 for _ in range(n)] for _ in range(n)]
        pasos: List[str] = []
        for i in range(n):
            for j in range(n):
                if i == j:
                    I[i][j] = 1.0
                    pasos.append(f"I[{i+1},{j+1}] = 1 (i=j)")
                else:
                    I[i][j] = 0.0
                    pasos.append(f"I[{i+1},{j+1}] = 0 (i≠j)")
        return I, pasos

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
                pasos.append(f"f{col+1} --> {format_val(1.0/piv)}*f{col+1}")
                pasos.append(Matrices._mat_to_str_frac(augmented))
            for row in range(col+1, n):
                factor = augmented[row][col]
                if abs(factor) > EPS:
                    for j in range(m+1):
                        augmented[row][j] -= factor * augmented[col][j]
                    signo = "+" if factor > 0 else "-"
                    pasos.append(f"f{row+1} --> f{row+1} {signo} ({format_val(abs(factor))})*f{col+1}")
                    pasos.append(Matrices._mat_to_str_frac(augmented))
        pasos.append("Estado final:\n" + Matrices._mat_to_str_frac(augmented))
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
                pasos.append(Matrices._mat_to_str_frac(augmented))
            pivotes.append((row, col))
            piv = augmented[row][col]
            if abs(piv - 1) > EPS:
                for j in range(m+1):
                    augmented[row][j] /= piv
                pasos.append(f"f{row+1} --> {format_val(1.0/piv)}*f{row+1}")
                pasos.append(Matrices._mat_to_str_frac(augmented))
            for r in range(n):
                if r != row and abs(augmented[r][col]) > EPS:
                    factor = augmented[r][col]
                    for j in range(m+1):
                        augmented[r][j] -= factor * augmented[row][j]
                    signo = "+" if factor > 0 else "-"
                    pasos.append(f"f{r+1} --> f{r+1} {signo} ({format_val(abs(factor))})*f{row+1}")
                    pasos.append(Matrices._mat_to_str_frac(augmented))
            row += 1
            if row == n:
                break
        pasos.append("Estado final:\n" + Matrices._mat_to_str_frac(augmented))
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
        return "\n".join(
            " | ".join(f"{x:8.4f}" for x in row)
            for row in mat
        )

    # -------------------- Utilidades --------------------
    @staticmethod
    def multiply(a: List[List[float]], b: List[List[float]]) -> List[List[float]]:
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
        res = [[0.0 for _ in range(pb)] for _ in range(n)]
        for i in range(n):
            for j in range(pb):
                s = 0.0
                for k in range(m):
                    s += a[i][k] * b[k][j]
                res[i][j] = s
        return res

    @staticmethod
    def multiply_with_steps(a: List[List[float]], b: List[List[float]]) -> Tuple[List[List[float]], List[str]]:
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
        res = [[0.0 for _ in range(pb)] for _ in range(n)]
        pasos: List[str] = []
        pasos.append(f"Multiplicando A ({n}x{m}) por B ({mb}x{pb}):")
        for i in range(n):
            for j in range(pb):
                terms = []
                s = 0.0
                for k in range(m):
                    aij = float(a[i][k])
                    bjk = float(b[k][j])
                    terms.append(f"{format_val(aij)}*{format_val(bjk)}")
                    s += aij * bjk
                res[i][j] = s
                pasos.append(f"C[{i+1},{j+1}] = " + " + ".join(terms) + f" = {format_val(s)}")
        pasos.append("Resultado final:")
        pasos.append(Matrices._mat_to_str_frac(res))
        return res, pasos

    @staticmethod
    def determinant(a: List[List[float]]) -> float:
        if not a:
            raise ValueError("La matriz no puede estar vacía.")
        n = len(a)
        m = len(a[0])
        if any(len(row) != m for row in a) or n != m:
            raise ValueError("El determinante solo está definido para matrices cuadradas.")
        M = [[float(x) for x in row] for row in a]
        det = 1.0
        swaps = 0
        for i in range(n):
            pivot_row = max(range(i, n), key=lambda r: abs(M[r][i]))
            if abs(M[pivot_row][i]) < EPS:
                return 0.0
            if pivot_row != i:
                M[i], M[pivot_row] = M[pivot_row], M[i]
                swaps += 1
            piv = M[i][i]
            det *= piv
            for r in range(i+1, n):
                factor = M[r][i] / piv
                for c in range(i, n):
                    M[r][c] -= factor * M[i][c]
        if swaps % 2 == 1:
            det = -det
        return det

    @staticmethod
    def determinant_with_steps(a: List[List[float]]) -> Tuple[float, List[str]]:
        if not a:
            raise ValueError("La matriz no puede estar vacía.")
        n = len(a)
        m = len(a[0])
        if any(len(row) != m for row in a) or n != m:
            raise ValueError("El determinante solo está definido para matrices cuadradas.")
        M = [[float(x) for x in row] for row in a]
        pasos: List[str] = []
        pivotes: List[float] = []
        swaps = 0
        for i in range(n):
            pivot_row = max(range(i, n), key=lambda r: abs(M[r][i]))
            pasos.append(f"Columna {i+1}: pivote elegido en fila {pivot_row+1} con valor {format_val(M[pivot_row][i])}")
            if abs(M[pivot_row][i]) < EPS:
                pasos.append("Pivote 0 -> det(A) = 0")
                return 0.0, pasos
            if pivot_row != i:
                M[i], M[pivot_row] = M[pivot_row], M[i]
                swaps += 1
                pasos.append(f"Intercambio f{i+1} ↔ f{pivot_row+1} (cambia el signo del determinante)")
                pasos.append("Estado tras intercambio:")
                pasos.append(Matrices._mat_to_str_frac(M))
            piv = M[i][i]
            pivotes.append(piv)
            pasos.append(f"Pivote p{i+1} = {format_val(piv)}")
            for r in range(i+1, n):
                factor = M[r][i] / piv
                if abs(M[r][i]) > EPS:
                    pasos.append(f"f{r+1} -> f{r+1} - ({format_val(factor)})*f{i+1}")
                for c in range(i, n):
                    M[r][c] -= factor * M[i][c]
                if abs(M[r][i]) > EPS:
                    pasos.append(Matrices._mat_to_str_frac(M))
        pasos.append("Matriz triangular superior final:")
        pasos.append(Matrices._mat_to_str_frac(M))
        pasos.append("Diagonal de la triangular: [" + ", ".join(format_val(M[i][i]) for i in range(n)) + "]")
        prod = 1.0
        for p in pivotes:
            prod *= p
        signo = -1.0 if (swaps % 2 == 1) else 1.0
        det = signo * prod
        pasos.append("Producto de pivotes: " + " * ".join(format_val(p) for p in pivotes) + f" = {format_val(prod)}")
        pasos.append(f"Intercambios de filas: {swaps} -> factor signo = {'-1' if signo < 0 else '+1'}")
        pasos.append("En una matriz triangular superior, det(A) es el producto de su diagonal, ajustado por el signo de los intercambios.")
        pasos.append(f"det(A) = {format_val(signo)} * {format_val(prod)} = {format_val(det)}")
        return det, pasos

    @staticmethod
    def _minor(mat: List[List[float]], row: int, col: int) -> List[List[float]]:
        return [[mat[i][j] for j in range(len(mat)) if j != col] for i in range(len(mat)) if i != row]

    @staticmethod
    def determinant_cofactor_with_steps(a: List[List[float]]) -> Tuple[float, List[str]]:
        if not a:
            raise ValueError("La matriz no puede estar vacía.")
        n = len(a)
        m = len(a[0])
        if any(len(row) != m for row in a) or n != m:
            raise ValueError("El determinante solo está definido para matrices cuadradas.")

        pasos: List[str] = []

        def det_recursive(mat: List[List[float]], depth: int=0) -> Tuple[float, List[str]]:
            indent = '  ' * depth
            steps_loc: List[str] = []
            size = len(mat)
            if size == 1:
                val = float(mat[0][0])
                steps_loc.append(f"{indent}Determinante 1x1 = {format_val(val)}")
                return val, steps_loc
            if size == 2:
                val = float(mat[0][0])*float(mat[1][1]) - float(mat[0][1])*float(mat[1][0])
                steps_loc.append(f"{indent}Determinante 2x2 = a11*a22 - a12*a21 = {format_val(mat[0][0])}*{format_val(mat[1][1])} - {format_val(mat[0][1])}*{format_val(mat[1][0])} = {format_val(val)}")
                return val, steps_loc
            total = 0.0
            steps_loc.append(f"{indent}Desarrollo por cofactores (fila 1) de matriz {size}x{size}:")
            for j in range(size):
                a_1j = float(mat[0][j])
                minor = Matrices._minor(mat, 0, j)
                sign = -1 if (0 + j) % 2 else 1
                sub_det, sub_steps = det_recursive(minor, depth+1)
                cofactor = sign * sub_det
                contrib = a_1j * cofactor
                steps_loc.append(f"{indent}  a[1,{j+1}] = {format_val(a_1j)} -> Menor {size-1}x{size-1} det = {format_val(sub_det)}; Cofactor = {format_val(sign)}*{format_val(sub_det)} = {format_val(cofactor)}; Contribución = {format_val(a_1j)}*{format_val(cofactor)} = {format_val(contrib)}")
                for s in sub_steps:
                    steps_loc.append(s)
                total += contrib
            steps_loc.append(f"{indent}Suma de contribuciones -> det = {format_val(total)}")
            return total, steps_loc

        det_val, det_steps = det_recursive(a, 0)
        pasos.extend(det_steps)
        pasos.append(f"det(A) = {format_val(det_val)}")
        return det_val, pasos

    @staticmethod
    def determinant_sarrus_with_steps(a: List[List[float]]) -> Tuple[float, List[str]]:
        if not a:
            raise ValueError("La matriz no puede estar vacía.")
        if len(a) != 3 or any(len(row) != 3 for row in a):
            raise ValueError("La regla de Sarrus aplica sólo a matrices 3x3.")
        pasos: List[str] = []
        pasos.append("Aplicando la regla de Sarrus a la matriz 3x3:")
        pasos.append(Matrices._mat_to_str_frac(a))
        a11,a12,a13 = float(a[0][0]), float(a[0][1]), float(a[0][2])
        a21,a22,a23 = float(a[1][0]), float(a[1][1]), float(a[1][2])
        a31,a32,a33 = float(a[2][0]), float(a[2][1]), float(a[2][2])
        pos1 = a11*a22*a33
        pos2 = a12*a23*a31
        pos3 = a13*a21*a32
        neg1 = a13*a22*a31
        neg2 = a11*a23*a32
        neg3 = a12*a21*a33
        pasos.append(f"Diagonales positivas: {format_val(a11)}*{format_val(a22)}*{format_val(a33)} = {format_val(pos1)}, {format_val(a12)}*{format_val(a23)}*{format_val(a31)} = {format_val(pos2)}, {format_val(a13)}*{format_val(a21)}*{format_val(a32)} = {format_val(pos3)}")
        pasos.append(f"Diagonales negativas: {format_val(a13)}*{format_val(a22)}*{format_val(a31)} = {format_val(neg1)}, {format_val(a11)}*{format_val(a23)}*{format_val(a32)} = {format_val(neg2)}, {format_val(a12)}*{format_val(a21)}*{format_val(a33)} = {format_val(neg3)}")
        pos_sum = pos1 + pos2 + pos3
        neg_sum = neg1 + neg2 + neg3
        det = pos_sum - neg_sum
        pasos.append(f"Suma positivas = {format_val(pos_sum)}; Suma negativas = {format_val(neg_sum)}")
        pasos.append(f"det(A) = Suma_positivas - Suma_negativas = {format_val(pos_sum)} - {format_val(neg_sum)} = {format_val(det)}")
        return det, pasos

    @staticmethod
    def determinant_cramer_with_steps(a: List[List[float]]) -> Tuple[float, List[str]]:
        if not a:
            raise ValueError("La matriz no puede estar vacía.")
        n = len(a)
        if any(len(row) != n for row in a):
            raise ValueError("El determinante solo está definido para matrices cuadradas.")
        pasos: List[str] = []
        pasos.append("Cálculo del determinante por desarrollo en la primera fila (Cramer):")
        pasos.append(Matrices._mat_to_str_frac(a))
        total = 0.0
        for j in range(n):
            a_1j = float(a[0][j])
            minor = Matrices._minor(a, 0, j)
            sub_det, sub_steps = Matrices.determinant_cofactor_with_steps(minor) if len(minor) > 1 else (float(minor[0][0]) if minor else 1.0, [])
            sign = -1 if (0 + j) % 2 else 1
            cofactor = sign * sub_det
            contrib = a_1j * cofactor
            pasos.append(f"a[1,{j+1}] = {format_val(a_1j)} -> det(Minor) = {format_val(sub_det)}; Cofactor = {format_val(sign)}*{format_val(sub_det)} = {format_val(cofactor)}; Contribución = {format_val(contrib)}")
            for s in sub_steps:
                pasos.append("  " + s)
            total += contrib
        pasos.append(f"Suma de contribuciones -> det(A) = {format_val(total)}")
        return total, pasos

    @staticmethod
    def determinant_by_method(a: List[List[float]], method: str) -> Tuple[float, List[str]]:
        m = method.lower()
        if m in ('eliminación', 'eliminacion', 'eliminate', 'elimination'):
            return Matrices.determinant_with_steps(a)
        if m in ('cofactores', 'cofactor', 'laplace'):
            return Matrices.determinant_cofactor_with_steps(a)
        if m in ('sarrus',):
            return Matrices.determinant_sarrus_with_steps(a)
        if m in ('cramer',):
            return Matrices.determinant_cramer_with_steps(a)
        return Matrices.determinant_with_steps(a)

    @staticmethod
    def transpose(a: List[List[float]]) -> List[List[float]]:
        if not a:
            return []
        m = len(a[0])
        if any(len(row) != m for row in a):
            raise ValueError("Todas las filas de A deben tener la misma longitud.")
        return [[a[r][c] for r in range(len(a))] for c in range(m)]

    @staticmethod
    def transpose_with_steps(a: List[List[float]]) -> Tuple[List[List[float]], List[str]]:
        if not a:
            return [], ["Matriz vacía -> transpuesta vacía"]
        m = len(a[0])
        if any(len(row) != m for row in a):
            raise ValueError("Todas las filas de A deben tener la misma longitud.")
        t = [[a[r][c] for r in range(len(a))] for c in range(m)]
        pasos: List[str] = []
        pasos.append(f"Transponiendo matriz {len(a)}x{m}:")
        pasos.append("Matriz original:")
        pasos.append(Matrices._mat_to_str(a))
        pasos.append("Pasos (mapeo de índices):")
        for i in range(len(a)):
            for j in range(m):
                pasos.append(f"T[{j+1},{i+1}] = A[{i+1},{j+1}] = {format_val(a[i][j])}")
        pasos.append("Transpuesta resultante:")
        pasos.append(Matrices._mat_to_str(t))
        return t, pasos

    @staticmethod
    def _get_storage_path() -> str:
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        data_dir = os.path.join(base, 'data')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
        return os.path.join(data_dir, 'matrices.json')

    @staticmethod
    def load_saved_matrices() -> dict:
        path = Matrices._get_storage_path()
        if not os.path.exists(path):
            return {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            res = {}
            for k, v in data.items():
                res[k] = [[float(x) for x in row] for row in v]
            return res
        except Exception:
            return {}

    @staticmethod
    def save_matrix(name: str, matrix: List[List[float]]):
        if not name or not isinstance(name, str):
            raise ValueError("El nombre debe ser una cadena no vacía.")
        try:
            from models.Vectores import load_saved_vectors
            vecs = load_saved_vectors()
            if name in vecs:
                raise ValueError(f"Ya existe un vector llamado '{name}'. Usa un nombre distinto para la matriz.")
        except Exception:
            pass
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
        if not a:
            raise ValueError("La matriz no puede estar vacía.")
        m = len(a[0])
        if any(len(row) != m for row in a):
            raise ValueError("Todas las filas de la matriz deben tener la misma longitud.")
        return [[float(x) * float(scalar) for x in row] for row in a]

    @staticmethod
    def multiply_scalar_with_steps(a: List[List[float]], scalar: float) -> Tuple[List[List[float]], List[str]]:
        if not a:
            raise ValueError("La matriz no puede estar vacía.")
        m = len(a[0])
        if any(len(row) != m for row in a):
            raise ValueError("Todas las filas de la matriz deben tener la misma longitud.")
        k = float(scalar)
        res = [[0.0 for _ in row] for row in a]
        pasos: List[str] = []
        pasos.append(f"Multiplicando matriz {len(a)}x{m} por escalar {format_val(k)}:")
        for i in range(len(a)):
            for j in range(m):
                val = float(a[i][j])
                r = k * val
                res[i][j] = r
                pasos.append(f"C[{i+1},{j+1}] = {format_val(k)}*{format_val(val)} = {format_val(r)}")
        pasos.append("Resultado final:")
        pasos.append(Matrices._mat_to_str_frac(res))
        return res, pasos

    @staticmethod
    def add(a: List[List[float]], b: List[List[float]]) -> List[List[float]]:
        if not a or not b:
            raise ValueError("Ambas matrices deben ser no vacías.")
        n = len(a)
        m = len(a[0])
        if any(len(row) != m for row in a):
            raise ValueError("Todas las filas de A deben tener la misma longitud.")
        if len(b) != n or any(len(row) != m for row in b):
            raise ValueError(f"Dimensiones incompatibles: A es {n}x{m} pero B tiene forma distinta.")
        return [[float(a[i][j]) + float(b[i][j]) for j in range(m)] for i in range(n)]

    @staticmethod
    def add_with_steps(a: List[List[float]], b: List[List[float]]) -> Tuple[List[List[float]], List[str]]:
        if not a or not b:
            raise ValueError("Ambas matrices deben ser no vacías.")
        n = len(a)
        m = len(a[0])
        if any(len(row) != m for row in a):
            raise ValueError("Todas las filas de A deben tener la misma longitud.")
        if len(b) != n or any(len(row) != m for row in b):
            raise ValueError(f"Dimensiones incompatibles: A es {n}x{m} pero B tiene forma distinta.")
        res = [[0.0 for _ in range(m)] for _ in range(n)]
        pasos: List[str] = []
        pasos.append(f"Sumando A ({n}x{m}) + B ({n}x{m}):")
        for i in range(n):
            for j in range(m):
                aij = float(a[i][j])
                bij = float(b[i][j])
                s = aij + bij
                res[i][j] = s
                pasos.append(f"C[{i+1},{j+1}] = {format_val(aij)} + {format_val(bij)} = {format_val(s)}")
        pasos.append("Resultado final:")
        pasos.append(Matrices._mat_to_str_frac(res))
        return res, pasos

    @staticmethod
    def subtract(a: List[List[float]], b: List[List[float]]) -> List[List[float]]:
        if not a or not b:
            raise ValueError("Ambas matrices deben ser no vacías.")
        n = len(a)
        m = len(a[0])
        if any(len(row) != m for row in a):
            raise ValueError("Todas las filas de A deben tener la misma longitud.")
        if len(b) != n or any(len(row) != m for row in b):
            raise ValueError(f"Dimensiones incompatibles: A es {n}x{m} pero B tiene forma distinta.")
        return [[float(a[i][j]) - float(b[i][j]) for j in range(m)] for i in range(n)]

    @staticmethod
    def subtract_with_steps(a: List[List[float]], b: List[List[float]]) -> Tuple[List[List[float]], List[str]]:
        if not a or not b:
            raise ValueError("Ambas matrices deben ser no vacías.")
        n = len(a)
        m = len(a[0])
        if any(len(row) != m for row in a):
            raise ValueError("Todas las filas de A deben tener la misma longitud.")
        if len(b) != n or any(len(row) != m for row in b):
            raise ValueError(f"Dimensiones incompatibles: A es {n}x{m} pero B tiene forma distinta.")
        res = [[0.0 for _ in range(m)] for _ in range(n)]
        pasos: List[str] = []
        pasos.append(f"Restando A ({n}x{m}) - B ({n}x{m}):")
        for i in range(n):
            for j in range(m):
                aij = float(a[i][j])
                bij = float(b[i][j])
                d = aij - bij
                res[i][j] = d
                pasos.append(f"C[{i+1},{j+1}] = {format_val(aij)} - {format_val(bij)} = {format_val(d)}")
        pasos.append("Resultado final:")
        pasos.append(Matrices._mat_to_str_frac(res))
        return res, pasos

    @staticmethod
    def equal(a: List[List[float]], b: List[List[float]], tol: float = 1e-8) -> bool:
        if not a and not b:
            return True
        if (not a) or (not b):
            return False
        if len(a) != len(b) or len(a[0]) != len(b[0]):
            return False
        n, m = len(a), len(a[0])
        for i in range(n):
            for j in range(m):
                if abs(float(a[i][j]) - float(b[i][j])) > tol:
                    return False
        return True

    @staticmethod
    def inverse(a: List[List[float]]) -> List[List[float]]:
        if not a:
            raise ValueError("La matriz no puede estar vacía.")
        n = len(a)
        m = len(a[0])
        if any(len(row) != m for row in a):
            raise ValueError("Todas las filas de la matriz deben tener la misma longitud.")
        if n != m:
            raise ValueError("Solo se puede invertir una matriz cuadrada.")
        aug = [ [float(x) for x in row] + [1.0 if i==j else 0.0 for j in range(n)] for i, row in enumerate(a) ]
        for col in range(n):
            pivot_row = max(range(col, n), key=lambda r: abs(aug[r][col]))
            if abs(aug[pivot_row][col]) < EPS:
                raise ValueError("La matriz es singular y no tiene inversa.")
            if pivot_row != col:
                aug[col], aug[pivot_row] = aug[pivot_row], aug[col]
            piv = aug[col][col]
            if abs(piv - 1.0) > EPS:
                for j in range(2*n):
                    aug[col][j] /= piv
            for r in range(n):
                if r == col:
                    continue
                factor = aug[r][col]
                if abs(factor) > EPS:
                    for j in range(2*n):
                        aug[r][j] -= factor * aug[col][j]
        for i in range(n):
            for j in range(n):
                if i == j:
                    if abs(aug[i][j] - 1.0) > 1e-8:
                        raise ValueError("La matriz no se redujo a la identidad; no es invertible.")
                else:
                    if abs(aug[i][j]) > 1e-8:
                        raise ValueError("La matriz no se redujo a la identidad; no es invertible.")
        inv = [ [aug[i][n + j] for j in range(n)] for i in range(n) ]
        return inv

    @staticmethod
    def inverse_with_steps(a: List[List[float]], det_method: str = 'Eliminación') -> Tuple[List[List[float]], List[str]]:
        if not a:
            raise ValueError("La matriz no puede estar vacía.")
        n = len(a)
        m = len(a[0])
        if any(len(row) != m for row in a):
            raise ValueError("Todas las filas de la matriz deben tener la misma longitud.")
        if n != m:
            raise ValueError("Solo se puede invertir una matriz cuadrada.")
        aug = [[float(x) for x in row] + [1.0 if i == j else 0.0 for j in range(n)]
               for i, row in enumerate(a)]
        pasos: List[str] = []
        pasos.append(f"Calculando inversa de matriz {n}x{n} por reducción por filas")
        pasos.append("[Matriz | Matriz reducida] inicial:")
        pasos.append(Matrices._aug_to_str_frac(aug, n))
        pivot_positions: List[Tuple[int, int]] = []
        for col in range(n):
            pivot_row = max(range(col, n), key=lambda r: abs(aug[r][col]))
            if abs(aug[pivot_row][col]) < EPS:
                pasos.append(f"No se encontró pivote distinto de 0 en la columna {col+1}. A es singular.")
                raise ValueError("La matriz es singular y no tiene inversa.")
            if pivot_row != col:
                aug[col], aug[pivot_row] = aug[pivot_row], aug[col]
                pasos.append(f"f{col+1} <-> f{pivot_row+1}")
                pasos.append(Matrices._aug_to_str_frac(aug, n))
            piv = aug[col][col]
            pivot_positions.append((col, col))
            if abs(piv - 1.0) > EPS:
                for j in range(2*n):
                    aug[col][j] /= piv
                coef = format_val(1.0/piv)
                pasos.append(f"f{col+1} --> {coef}*f{col+1}")
                pasos.append(Matrices._aug_to_str_frac(aug, n))
            for r in range(n):
                if r == col:
                    continue
                factor = aug[r][col]
                if abs(factor) > EPS:
                    for j in range(2*n):
                        aug[r][j] -= factor * aug[col][j]
                    pasos.append(f"f{r+1} --> f{r+1} - {format_val(abs(factor))}*f{col+1}")
                    pasos.append(Matrices._aug_to_str_frac(aug, n))
        ok = True
        for i in range(n):
            for j in range(n):
                if i == j:
                    if abs(aug[i][j] - 1.0) > 1e-8:
                        ok = False
                        break
                else:
                    if abs(aug[i][j]) > 1e-8:
                        ok = False
                        break
            if not ok:
                break
        if not ok:
            pasos.append("La parte izquierda no se redujo a la identidad; A no es invertible.")
            raise ValueError("La matriz no se redujo a la identidad; no es invertible.")
        inv = [[aug[i][n + j] for j in range(n)] for i in range(n)]
        pasos.append("Parte izquierda reducida a I; extraemos A^{-1} de la derecha:")
        pasos.append(Matrices._mat_to_str_frac(inv))
        pasos.append("\nVerificaciones de invertibilidad:")
        try:
            prod = Matrices.multiply(a, inv)
            is_I = Matrices._is_identity(prod)
            estado = "CUMPLE" if is_I else "NO CUMPLE"
            pasos.append("1) A·A^{-1} = I")
            pasos.append("Producto A·A^{-1}:")
            pasos.append(Matrices._mat_to_str_frac(prod))
            pasos.append(f"Construcción de la identidad I (n = {n}):")
            I_calc, pasos_I = Matrices._identity_with_steps(n)
            pasos.extend(pasos_I)
            pasos.append("Resultado I:")
            pasos.append(Matrices._mat_to_str_frac(I_calc))
            pasos.append("Comparación explícita A·A^{-1} = I:")
            pasos.append(Matrices._mat_side_by_side_equal(prod, I_calc))
            pasos.append(f"Veredicto: {estado}")
        except Exception as e:
            pasos.append(f"1) A·A^{-1} = I  -> No hay igualdad  ({e})")
        cumple_pivotes = (len(pivot_positions) == n)
        pasos.append(
            f"2) (c) A tiene n posiciones pivote -> "
            f"{'Cumple (A es una matriz invertible)' if cumple_pivotes else 'No Cumple (A no es una matriz invertible)'}; "
            + "pivotes: " + ", ".join(f"(f{r+1},c{c+1})" for r,c in pivot_positions)
        )
        pasos.append(
            f"3) (d) Ax = 0 solo tiene la solución trivial -> "
            f"{'Cumple (A^-1 existe)' if cumple_pivotes else 'No Cumple (A^-1 no existe)'}"
        )
        pasos.append(
            f"4) (e) Las columnas de A forman un conjunto L.I. -> "
            f"{'Cumple (A es una matriz invertible)' if cumple_pivotes else 'No Cumple (A es no invertible)'}"
        )
        return inv, pasos

    @staticmethod
    def inverse_adjugate_with_steps(a: List[List[float]], det_method: str = 'Cofactores') -> Tuple[List[List[float]], List[str]]:
        raise NotImplementedError("inverse_adjugate_with_steps ha sido removida. Use funciones de determinante independientes.")

    # Wrappers compatibles con versiones anteriores (det_sarrus, det_cofactor, cramer)
    @staticmethod
    def det_sarrus(a: List[List[float]]) -> Tuple[float, List[str]]:
        return Matrices.determinant_sarrus_with_steps(a)

    @staticmethod
    def det_cofactor(a: List[List[float]]) -> Tuple[float, List[str]]:
        return Matrices.determinant_cofactor_with_steps(a)

    @staticmethod
    def cramer(a: List[List[float]], b: List[List[float]]) -> Tuple[Optional[List[float]], List[str]]:
        try:
            sol, pasos = Matrices.determinant_cramer_with_steps(a)
            # cramer wrapper in original expected a solution vector; use determinant_cramer... to compute dets.
            # Here, if determinant_cramer_with_steps returns det only, fallback to proper implementation:
            # implement actual Cramer solution if possible:
            Matrices._validate_a_b(a, b)  # ensures shapes
            n = len(a)
            if any(len(row) != n for row in a):
                return None, ["Cramer requiere A cuadrada."]
            detA = Matrices.determinant(a)
            pasos_out: List[str] = []
            pasos_out.append("Aplicando la regla de Cramer (wrapper):")
            pasos_out.append(f"det(A) = {format_val(detA)}")
            if abs(detA) < EPS:
                pasos_out.append("Determinante cero -> Cramer no aplica.")
                return None, pasos_out
            solucion = []
            for col in range(n):
                Ai = [row[:] for row in a]
                for i in range(n):
                    Ai[i][col] = b[i][0]
                detAi = Matrices.determinant(Ai)
                xi = detAi / detA
                pasos_out.append(f"det(A_{col+1}) = {format_val(detAi)} -> x{col+1} = {format_val(xi)}")
                solucion.append(xi)
            pasos_out.append("Solución por Cramer:")
            pasos_out.append("[" + ", ".join(format_val(x) for x in solucion) + "]")
            return solucion, pasos_out
        except Exception as e:
            return None, [f"Error en Cramer: {e}"]

    # helper interno de compatibilidad
    @staticmethod
    def _fmt_num(x: float) -> str:
        return format_val(x)