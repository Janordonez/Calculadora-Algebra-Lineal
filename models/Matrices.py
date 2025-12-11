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
    @staticmethod
    def inverse_with_steps(mat: List[List[float]], det_method: str = 'Eliminación'):
        """
        Calcula la inversa de una matriz cuadrada con pasos detallados y verifica AA^(-1)=I.
        Devuelve (inversa, pasos:list[str]).
        """
        if not Matrices._is_square(mat):
            raise ValueError("La matriz debe ser cuadrada para calcular la inversa.")
        n = len(mat)
        # Calcular determinante
        if det_method == 'Eliminación':
            det, det_pasos = Matrices.determinant_with_steps(mat)
        elif det_method == 'Cofactores':
            det, det_pasos = Matrices.determinant_cofactor_with_steps(mat)
        elif det_method == 'Sarrus':
            det, det_pasos = Matrices.determinant_sarrus_with_steps(mat)
        elif det_method == 'Cramer':
            det, det_pasos = Matrices.determinant_cramer_with_steps(mat)
        else:
            raise ValueError(f"Método de determinante desconocido: {det_method}")
        pasos = [f"Método para inversa: {det_method}"] + det_pasos
        if abs(det) < EPS:
            pasos.append("La matriz no es invertible (det=0)")
            return None, pasos
        # Construir matriz aumentada [A | I]
        A = [row[:] for row in mat]
        I = [[float(i == j) for j in range(n)] for i in range(n)]
        aug = [A[i] + I[i] for i in range(n)]
        pasos.append("Matriz aumentada [A | I]:")
        pasos.append(Matrices._mat_to_str_frac(aug))
        # Gauss-Jordan para obtener [I | A^{-1}]
        for col in range(n):
            # Selección de pivote con pivoteo parcial (máximo absoluto) para mayor estabilidad
            max_row = max(range(col, n), key=lambda r: abs(aug[r][col]))
            if abs(aug[max_row][col]) < EPS:
                pasos.append(f"No hay pivote significativo en columna {col+1}, inversa no existe.")
                return None, pasos
            sel = max_row
            if sel != col:
                aug[col], aug[sel] = aug[sel], aug[col]
                pasos.append(f"Intercambio de fila {col+1} con fila {sel+1}")
                pasos.append(Matrices._mat_to_str_frac(aug))
            piv = aug[col][col]
            for j in range(2*n):
                aug[col][j] /= piv
            pasos.append(f"Normalizando fila {col+1} por pivote {format_val(piv)}")
            pasos.append(Matrices._mat_to_str_frac(aug))
            for r in range(n):
                if r != col:
                    factor = aug[r][col]
                    for j in range(2*n):
                        aug[r][j] -= factor * aug[col][j]
                    pasos.append(f"f{r+1} --> f{r+1} - ({format_val(factor)})*f{col+1}")
                    pasos.append(Matrices._mat_to_str_frac(aug))
        # Extraer inversa
        inv = [row[n:] for row in aug]
        pasos.append("Matriz inversa A^{-1}:")
        pasos.append(Matrices._mat_to_str_frac(inv))
        # Verificación AA^{-1} = I
        verif = Matrices.multiply(mat, inv)
        pasos.append("Verificación AA^{-1} = I:")
        pasos.append(Matrices._mat_to_str_frac(verif))
        return inv, pasos
        
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
            # Selección de pivote con pivoteo parcial en la submatriz (row..n-1, col)
            max_row = max(range(row, n), key=lambda r: abs(augmented[r][col])) if row < n else row
            if row < n and abs(augmented[max_row][col]) < EPS:
                pasos.append(f"No hay pivote en columna {col+1}, se salta.")
                continue
            sel = max_row
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
            # Construir la solución paramétrica en términos de parámetros t1, t2, ...
            # libres: índices de variables libres
            param_names = {col: f"t{idx+1}" for idx, col in enumerate(libres)}
            solucion_param = ["0"] * m

            # mapa de columna básica -> fila donde está el pivote
            basic_row_of_col = {}
            for i, col in enumerate(pivote_col):
                if col != -1:
                    basic_row_of_col[col] = i

            for var in range(m):
                if var in libres:
                    solucion_param[var] = param_names[var]
                else:
                    # variable básica: x_var = rhs - sum(coeff_free * t_k)
                    row = basic_row_of_col.get(var)
                    if row is None:
                        solucion_param[var] = "0"
                        continue
                    rhs = mat[row][-1]
                    parts = []
                    # formato del término constante
                    const_str = format_val(rhs)
                    if const_str != "0":
                        parts.append(const_str)
                    # términos en función de parámetros libres
                    for fc in libres:
                        coeff = mat[row][fc]
                        if abs(coeff) > EPS:
                            coeff_str = format_val(abs(coeff))
                            pname = param_names[fc]
                            # signo: x_var = rhs - coeff*param  (si coeff>0)
                            if coeff > 0:
                                parts.append(f"- {coeff_str}*{pname}")
                            else:
                                parts.append(f"+ {coeff_str}*{pname}")
                    if not parts:
                        solucion_param[var] = "0"
                    else:
                        # unir partes con espacios y limpiar signos duplicados
                        solucion_param[var] = " ".join(parts)

            return {"tipo": tipo, "solucion_parametrica": solucion_param, "libres": libres}

    @staticmethod
    def _mat_to_str(mat: List[List[float]]) -> str:
        # Formato tipo [1.0000 | 0.0625 | ... ]
        return "\n".join(
            " | ".join(f"{x:8.4f}" for x in row)
            for row in mat
        )

    @staticmethod
    def _mat_to_str_frac(mat: List[List[float]]) -> str:
        """
        Representa una matriz usando `format_val` para cada elemento (enteros o fracciones).
        """
        return "\n".join(
            "[ " + ", ".join(format_val(x) for x in row) + " ]"
            for row in mat
        )

    @staticmethod
    def _is_square(mat: List[List[float]]) -> bool:
        return bool(mat) and all(len(row) == len(mat) for row in mat)

    @staticmethod
    def determinant_sarrus_with_steps(mat: List[List[float]]):
        """Calcula determinante por la regla de Sarrus (solo 3x3) y devuelve (det, pasos:list[str])."""
        if not Matrices._is_square(mat) or len(mat) != 3:
            raise ValueError("Sarrus aplica solo a matrices cuadradas 3x3")
        a = mat
        pasos = ["Regla de Sarrus (3x3):"]
        pasos.append("Matriz:")
        pasos.append(Matrices._mat_to_str_frac(a))
        # diagonales principales
        p1 = a[0][0] * a[1][1] * a[2][2]
        p2 = a[0][1] * a[1][2] * a[2][0]
        p3 = a[0][2] * a[1][0] * a[2][1]
        s1 = p1 + p2 + p3
        pasos.append(f"Suma diagonales principales: {format_val(p1)} + {format_val(p2)} + {format_val(p3)} = {format_val(s1)}")
        # diagonales secundarias
        q1 = a[0][2] * a[1][1] * a[2][0]
        q2 = a[0][0] * a[1][2] * a[2][1]
        q3 = a[0][1] * a[1][0] * a[2][2]
        s2 = q1 + q2 + q3
        pasos.append(f"Suma diagonales secundarias: {format_val(q1)} + {format_val(q2)} + {format_val(q3)} = {format_val(s2)}")
        det = s1 - s2
        pasos.append(f"det = {format_val(s1)} - {format_val(s2)} = {format_val(det)}")
        return det, pasos

    @staticmethod
    def determinant_cofactor_with_steps(mat: List[List[float]]):
        """Calcula determinante por expansión en cofactores (recursivo) con pasos detallados."""
        # Validación robusta de la entrada
        if not isinstance(mat, list) or not mat:
            raise ValueError("La matriz debe ser una lista no vacía de filas.")
        n = len(mat)
        for i, row in enumerate(mat):
            if not isinstance(row, list):
                raise ValueError(f"Fila {i+1} no es una lista.")
            if len(row) != n:
                raise ValueError(f"La matriz debe ser cuadrada: fila {i+1} tiene longitud {len(row)} (esperada {n}).")

        pasos: List[str] = []

        def choose_best_expansion(m):
            nloc = len(m)
            # contar ceros por fila y por columna
            # inicializar con -1 para asegurar que la primera fila/col sea candidata
            best_row = (-1, 0)  # (zeros, index)
            for i in range(nloc):
                zeros = sum(1 for x in m[i] if abs(x) < EPS)
                if zeros > best_row[0]:
                    best_row = (zeros, i)
            best_col = (-1, 0)
            for j in range(nloc):
                zeros = sum(1 for i in range(nloc) if abs(m[i][j]) < EPS)
                if zeros > best_col[0]:
                    best_col = (zeros, j)
            # preferir fila en empate
            if best_row[0] >= best_col[0]:
                return ('row', best_row[1])
            else:
                return ('col', best_col[1])

        def det_recursive(m, level=0):
            indent = '  ' * level
            n = len(m)
            if n == 1:
                val = m[0][0]
                pasos.append(f"{indent}Det( [ {format_val(val)} ] ) = {format_val(val)}")
                return val
            if n == 2:
                val = m[0][0] * m[1][1] - m[0][1] * m[1][0]
                pasos.append(f"{indent}Det 2x2: {format_val(m[0][0])}*{format_val(m[1][1])} - {format_val(m[0][1])}*{format_val(m[1][0])} = {format_val(val)}")
                return val

            total = 0.0
            choice_type, idx = choose_best_expansion(m)
            if choice_type == 'row':
                pasos.append(f"{indent}Expansión por la fila {idx+1} (nivel {level}), fila = [{', '.join(format_val(x) for x in m[idx])}]")
                for j in range(n):
                    a_ij = m[idx][j]
                    if abs(a_ij) < EPS:
                        pasos.append(f"{indent}Elemento f{idx+1},{j+1} = 0 -> contribuye 0")
                        continue
                    # construir submatriz (eliminar fila idx y columna j)
                    sub = [ [m[r][c] for c in range(n) if c != j] for r in range(n) if r != idx ]
                    pasos.append(f"{indent}Termino: a[{idx+1},{j+1}] = {format_val(a_ij)}, signo (-1)^{idx+1 + j+1}")
                    pasos.append(f"{indent}Menor {idx+1},{j+1} =")
                    pasos.append(Matrices._mat_to_str_frac(sub))
                    try:
                        subdet = det_recursive(sub, level+1)
                    except IndexError as ie:
                        raise IndexError(f"IndexError al expandir fila {idx+1}, columna {j+1} en nivel {level}: submatriz tamaño {len(sub)}x{len(sub[0]) if sub else 0} -> {ie}")
                    sign = (-1) ** (idx + j)
                    contrib = sign * a_ij * subdet
                    pasos.append(f"{indent}Contribución = {format_val(a_ij)} * ({format_val(subdet)}) * {format_val(sign)} = {format_val(contrib)}")
                    total += contrib
            else:
                pasos.append(f"{indent}Expansión por la columna {idx+1} (nivel {level}), columna = [{', '.join(format_val(m[r][idx]) for r in range(n))}]")
                for i in range(n):
                    a_ij = m[i][idx]
                    if abs(a_ij) < EPS:
                        pasos.append(f"{indent}Elemento f{i+1},{idx+1} = 0 -> contribuye 0")
                        continue
                    sub = [ [m[r][c] for c in range(n) if c != idx] for r in range(n) if r != i ]
                    pasos.append(f"{indent}Termino: a[{i+1},{idx+1}] = {format_val(a_ij)}, signo (-1)^{i+1 + idx+1}")
                    pasos.append(f"{indent}Menor {i+1},{idx+1} =")
                    pasos.append(Matrices._mat_to_str_frac(sub))
                    try:
                        subdet = det_recursive(sub, level+1)
                    except IndexError as ie:
                        raise IndexError(f"IndexError al expandir fila {i+1}, columna {idx+1} en nivel {level}: submatriz tamaño {len(sub)}x{len(sub[0]) if sub else 0} -> {ie}")
                    sign = (-1) ** (i + idx)
                    contrib = sign * a_ij * subdet
                    pasos.append(f"{indent}Contribución = {format_val(a_ij)} * ({format_val(subdet)}) * {format_val(sign)} = {format_val(contrib)}")
                    total += contrib

            pasos.append(f"{indent}Subtotal (nivel {level}) = {format_val(total)}")
            return total

        det = det_recursive(mat, 0)
        pasos.insert(0, "Determinante por cofactores:")

        # Para matrices 3x3, añadimos una representación condensada tipo expansión
        # sobre la primera fila, mostrando las matrices menores 2x2 y la evaluación.
        n = len(mat)
        if n == 3:
            a0 = mat[0]
            compact_parts = []
            compact_minors_calc = []
            compact_minors_vals = []
            compact_minors_nums = []
            for j in range(3):
                a_0j = a0[j]
                exp = 1 + (j + 1)  # 1-based: exponent (1+(j+1)) matches image: 2,3,4
                # construir menor 2x2 (eliminar fila0 y columna j)
                minor = [ [mat[r][c] for c in range(3) if c != j] for r in range(1,3) ]
                # calcular determinant del menor 2x2
                m00, m01 = minor[0][0], minor[0][1]
                m10, m11 = minor[1][0], minor[1][1]
                minor_expr = f"|{format_val(m00)} {format_val(m01)}|\n|{format_val(m10)} {format_val(m11)}|"
                minor_calc = f"{format_val(m00)}*{format_val(m11)} - {format_val(m01)}*{format_val(m10)}"
                minor_val = m00 * m11 - m01 * m10
                # signo en la expansión
                sign_symbol = '+' if ((-1) ** (0 + j)) > 0 else '-'
                compact_parts.append(f"{format_val(a_0j)}(-1)^{exp} {minor_expr}")
                compact_minors_calc.append(minor_calc)
                compact_minors_vals.append(format_val(minor_val))
                compact_minors_nums.append(minor_val)

            # Formatear líneas similares al ejemplo provisto
            pasos.append("")
            pasos.append("Expansión por la primera fila (forma compacta):")
            # primera línea: show terms with minors inline (single-line may be long)
            inline_terms = ' + '.join(compact_parts)
            pasos.append(f"|A| = {inline_terms}")

            # segunda línea: mostrar cálculo interno de cada menor como [a*d - b*c]
            minor_calc_line = '  -  '.join(compact_minors_calc)
            pasos.append(f"Evaluación de menores 2x2: {', '.join(compact_minors_calc)}")
            # tercera línea: mostrar resultados de cada menor y operación en corchetes
            bracketed = []
            for idx, val in enumerate(compact_minors_vals):
                bracketed.append(f"{val}")
            pasos.append(f"Menores evaluados: {', '.join(bracketed)}")
            # finalmente, mostrar la suma ponderada por los elementos de la primera fila y signos
            weighted_terms = []
            for j in range(3):
                coeff = a0[j]
                mval = compact_minors_nums[j]
                term_val = coeff * mval * ((-1) ** (0 + j))
                weighted_terms.append(format_val(term_val))
            pasos.append(f"Suma ponderada: {' + '.join(weighted_terms)}")

        pasos.append(f"Resultado: {format_val(det)}")
        # Fórmula para la inversa usando cofactores / adjunta
        pasos.append("")
        pasos.append("Si A es invertible entonces:\n  A^{-1} = (1 / det(A)) · adj(A)  (adj(A) = matriz adjunta / adjugada)")
        return det, pasos

    @staticmethod
    def determinant_with_steps(mat: List[List[float]]):
        """Calcula determinante mediante eliminación (Gauss) registrando pasos.
        Devuelve (determinante, pasos:list[str])."""
        if not Matrices._is_square(mat):
            raise ValueError("La matriz debe ser cuadrada para calcular el determinante.")
        # trabajar con copia en float
        n = len(mat)
        A = [ [float(x) for x in row] for row in mat ]
        pasos: List[str] = []
        pasos.append("Cálculo por eliminación Gaussiana (convertir a triangular superior):")
        pasos.append(Matrices._mat_to_str_frac(A))
        swaps = 0
        for i in range(n):
            # buscar pivote (máximo por valor absoluto) para estabilidad
            pivot_row = max(range(i, n), key=lambda r: abs(A[r][i]))
            if abs(A[pivot_row][i]) < EPS:
                pasos.append(f"Pivote en columna {i+1} es aproximadamente 0 -> determinante es 0")
                return 0.0, pasos
            if pivot_row != i:
                A[i], A[pivot_row] = A[pivot_row], A[i]
                swaps += 1
                pasos.append(f"Intercambio de fila {i+1} con fila {pivot_row+1} -> signo invertido")
                pasos.append(Matrices._mat_to_str_frac(A))
            piv = A[i][i]
            for r in range(i+1, n):
                factor = A[r][i] / piv
                if abs(factor) < EPS:
                    continue
                for c in range(i, n):
                    A[r][c] -= factor * A[i][c]
                pasos.append(f"f{r+1} --> f{r+1} - ({format_val(factor)})*f{i+1}")
                pasos.append(Matrices._mat_to_str_frac(A))
        # producto de la diagonal
        prod = 1.0
        for i in range(n):
            prod *= A[i][i]
        det = prod * ((-1) ** swaps)
        pasos.append(f"Producto diagonal = {' * '.join(format_val(A[i][i]) for i in range(n))} = {format_val(prod)}")
        if swaps:
            pasos.append(f"Número de intercambios: {swaps} -> signo final * (-1)^{swaps}")
        pasos.append(f"det = {format_val(det)}")
        return det, pasos

    @staticmethod
    def determinant_cramer_with_steps(mat: List[List[float]]):
        """Alias: usa cofactores pero lo etiqueta como 'Cramer' para la GUI que lo solicita."""
        pasos = ["Método 'Cramer' (implementado como expansión por cofactores para mostrar pasos):"]
        det, cof_pasos = Matrices.determinant_cofactor_with_steps(mat)
        pasos.extend(cof_pasos)
        pasos.append(f"(Etiquetado Cramer) Resultado det = {format_val(det)}")
        return det, pasos

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

    @staticmethod
    def add_with_steps(A: List[List[float]], B: List[List[float]]):
        """Suma A + B con pasos: devuelve (resultado, pasos:list[str])."""
        Matrices._ensure_rectangular(A)
        Matrices._ensure_rectangular(B)
        if len(A) != len(B) or len(A[0]) != len(B[0]):
            raise ValueError("Dimensiones incompatibles para suma.")
        pasos = ["Suma de matrices elemento a elemento:"]
        m = len(A)
        n = len(A[0])
        res = [[0.0]*n for _ in range(m)]
        for i in range(m):
            for j in range(n):
                aij = A[i][j]
                bij = B[i][j]
                val = aij + bij
                pasos.append(f"C[{i+1},{j+1}] = {format_val(aij)} + {format_val(bij)} = {format_val(val)}")
                res[i][j] = val
        return res, pasos

    @staticmethod
    def subtract_with_steps(A: List[List[float]], B: List[List[float]]):
        """Resta A - B con pasos: devuelve (resultado, pasos:list[str])."""
        Matrices._ensure_rectangular(A)
        Matrices._ensure_rectangular(B)
        if len(A) != len(B) or len(A[0]) != len(B[0]):
            raise ValueError("Dimensiones incompatibles para resta.")
        pasos = ["Resta de matrices elemento a elemento:"]
        m = len(A)
        n = len(A[0])
        res = [[0.0]*n for _ in range(m)]
        for i in range(m):
            for j in range(n):
                aij = A[i][j]
                bij = B[i][j]
                val = aij - bij
                pasos.append(f"C[{i+1},{j+1}] = {format_val(aij)} - {format_val(bij)} = {format_val(val)}")
                res[i][j] = val
        return res, pasos

    @staticmethod
    def multiply_with_steps(A: List[List[float]], B: List[List[float]]):
        """Multiplicación A*B con pasos elementales: devuelve (resultado, pasos:list[str])."""
        Matrices._ensure_rectangular(A)
        Matrices._ensure_rectangular(B)
        m = len(A)
        n = len(A[0])
        n2 = len(B)
        p = len(B[0])
        if n != n2:
            raise ValueError(f"No se puede multiplicar: A es {m}x{n} y B es {n2}x{p}.")
        pasos = [f"Multiplicación de matrices A({m}x{n}) * B({n2}x{p}):"]
        res = [[0.0]*p for _ in range(m)]
        for i in range(m):
            for j in range(p):
                terms = []
                s = 0.0
                for k in range(n):
                    a = A[i][k]
                    b = B[k][j]
                    terms.append(f"{format_val(a)}*{format_val(b)}")
                    s += a*b
                pasos.append(f"C[{i+1},{j+1}] = " + " + ".join(terms) + f" = {format_val(s)}")
                res[i][j] = s
        return res, pasos

    @staticmethod
    def multiply_scalar_with_steps(A: List[List[float]], scalar: float):
        """Multiplica matriz por escalar con pasos: devuelve (resultado, pasos:list[str])."""
        Matrices._ensure_rectangular(A)
        pasos = [f"Multiplicación de matriz por escalar {format_val(scalar)}:"]
        m = len(A)
        n = len(A[0])
        res = [[0.0]*n for _ in range(m)]
        for i in range(m):
            for j in range(n):
                val = scalar * A[i][j]
                pasos.append(f"C[{i+1},{j+1}] = {format_val(scalar)} * {format_val(A[i][j])} = {format_val(val)}")
                res[i][j] = val
        return res, pasos
