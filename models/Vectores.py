from typing import List

class Vector:
    def __init__(self, datos: List[float]):
        self.datos = datos

    def suma(self, otro: 'Vector') -> 'Vector':
        return Vector([a + b for a, b in zip(self.datos, otro.datos)])

    def resta(self, otro: 'Vector') -> 'Vector':
        return Vector([a - b for a, b in zip(self.datos, otro.datos)])

    def escalar(self, esc: float) -> 'Vector':
        return Vector([esc * a for a in self.datos])

    def multiplicacion(self, otro: 'Vector') -> 'Vector':
        return Vector([a * b for a, b in zip(self.datos, otro.datos)])

    def eliminar_coma_punto(self) -> 'Vector':
        return Vector([float(str(a).replace(',', '').replace('.', '')) for a in self.datos])

    def mostrar(self):
        return str(self.datos)

def solucionMatrizVector(vectores: list[list[float]]) -> str:
    """
    Muestra el proceso de reducción de la matriz paso a paso, indicando la matriz antes y después de cada operación,
    la fila pivote y las operaciones realizadas, con formato tipo calculadora visual.
    Al final, muestra el proceso explícito de combinación lineal, usando la reducción ya realizada.
    """
    import copy
    matriz = [v[:] for v in vectores]
    filas = len(matriz)
    columnas = len(matriz[0]) if filas > 0 else 0

    def clean(x):
        return 0.0 if abs(x) < 1e-10 else x

    def matriz_str(m):
        return "\n".join(
            " | ".join(f"{clean(x):8.4f}" for x in fila)
            for fila in m
        )

    proceso = []
    proceso.append("Matriz inicial:")
    proceso.append(matriz_str(matriz))

    es_homogenea = all(abs(fila[-1]) < 1e-10 for fila in matriz)
    proceso.append("\n¿Es homogénea?: " + ("Sí" if es_homogenea else "No"))

    A = copy.deepcopy(matriz)
    n = filas
    m = columnas
    pivots = []

    row = 0
    for col in range(m-1):
        # Buscar el pivote
        sel = None
        for i in range(row, n):
            if abs(A[i][col]) > 1e-10:
                sel = i
                break
        if sel is None:
            proceso.append(f"\nColumna {col+1}: No hay pivote (variable libre)")
            continue
        # Intercambiar filas si es necesario
        if sel != row:
            proceso.append(f"\nf{row+1} <-> f{sel+1}")
            A[row], A[sel] = A[sel], A[row]
            proceso.append(matriz_str(A))
        # Normalizar la fila del pivote
        piv = A[row][col]
        if abs(piv) < 1e-10:
            proceso.append(f"\nNo se puede dividir por cero en la fila {row+1}.")
            continue
        if abs(piv - 1.0) > 1e-10:
            proceso.append(f"\nf{row+1} --> (1/{piv:.4f})*f{row+1}")
            A[row] = [aij / piv if abs(piv) > 1e-10 else 0.0 for aij in A[row]]
            A[row] = [clean(x) for x in A[row]]
            proceso.append(matriz_str(A))
        # Hacer ceros en la columna del pivote
        for i in range(n):
            if i != row and abs(A[i][col]) > 1e-10:
                factor = A[i][col]
                signo = "+" if factor > 0 else "-"
                proceso.append(f"\nf{i+1} --> f{i+1} {signo} ({abs(factor):.4f})*f{row+1}")
                A[i] = [aij - factor * arj for aij, arj in zip(A[i], A[row])]
                A[i] = [clean(x) for x in A[i]]
                proceso.append(matriz_str(A))
        pivots.append(col)
        row += 1
        if row == n:
            break

    proceso.append("\nMatriz escalonada reducida final:")
    proceso.append(matriz_str(A))

    # Variables básicas y libres
    basicas = [f"x{p+1}" for p in pivots]
    libres = [f"x{j+1}" for j in range(m-1) if j not in pivots]
    proceso.append(f"\nVariables básicas (VB): {', '.join(basicas) if basicas else 'Ninguna'}")
    proceso.append(f"Variables libres (VL): {', '.join(libres) if libres else 'Ninguna'}")

    # Solución del sistema
    if es_homogenea:
        if len(libres) > 0:
            proceso.append("El sistema homogéneo tiene infinitas soluciones (parámetros libres).")
        else:
            proceso.append("El sistema homogéneo solo tiene la solución trivial (todos ceros).")
    else:
        inconsistente = False
        for fila in A:
            if all(abs(fila[j]) < 1e-10 for j in range(m-1)) and abs(fila[-1]) > 1e-10:
                inconsistente = True
                break
        if inconsistente:
            proceso.append("El sistema es incompatible (no tiene solución).")
            proceso.append("Nota: La comprobación de dependencia lineal que sigue sólo usa las columnas de coeficientes (Ax=0).")
        elif len(libres) > 0:
            proceso.append("El sistema tiene infinitas soluciones (parámetros libres).")
            # Construir la solución paramétrica: x = x_particular + sum t_k * v_k
            num_vars = m - 1
            # inicializar solución particular con ceros
            x_particular = [0.0] * num_vars
            # identificar pivotes por fila (primera columna no-nula)
            pivot_of_row = [-1] * n
            for i in range(n):
                for j in range(num_vars):
                    if abs(A[i][j]) > 1e-10:
                        pivot_of_row[i] = j
                        break
            # rellenar la solución particular (tomando parámetros libres = 0)
            for i in range(n):
                pc = pivot_of_row[i]
                if pc != -1:
                    x_particular[pc] = clean(A[i][-1])
            proceso.append("\nSolución particular (tomando parámetros libres = 0):")
            proceso.append(str([clean(v) for v in x_particular]))
            # construir vectores de la base del núcleo (uno por cada variable libre)
            vectores_nucleo = []
            libres_indices = [int(s[1:]) - 1 for s in libres]
            for free_idx in range(num_vars):
                if free_idx in libres_indices:
                    vec = [0.0] * num_vars
                    vec[free_idx] = 1.0
                    # para cada ecuación/pivote, coef en la variable básica = -A[row][free_idx]
                    for i in range(n):
                        pc = pivot_of_row[i]
                        if pc != -1:
                            coef = -A[i][free_idx]
                            vec[pc] = clean(coef)
                    vectores_nucleo.append((free_idx, vec))
            proceso.append("\nVectores asociados a parámetros libres (direcciones del espacio solución):")
            for idx, v in vectores_nucleo:
                proceso.append(f"t{idx+1} · {v}")
            # Mostrar la forma general
            sol_expr = "x = " + str([clean(v) for v in x_particular])
            for idx, v in vectores_nucleo:
                sol_expr += f" + t{idx+1}*{v}"
            proceso.append("\nSolución general en forma paramétrica:")
            proceso.append(sol_expr)
        else:
            sol = [clean(fila[-1]) for fila in A]
            proceso.append(f"Solución única: {sol}")

    # --- Proceso explícito de combinación lineal ---
    proceso.append("\n--- Proceso explícito de combinación lineal ---")
    # Tomamos solo la parte de coeficientes (sin la columna de términos independientes)
    coeficientes = [fila[:-1] for fila in matriz]
    vectores = [list(col) for col in zip(*coeficientes)]
    num_vars = len(vectores)
    # 1. Mostrar la ecuación general
    ecuacion = " + ".join([f"c{j+1}·v{j+1}" for j in range(num_vars)]) + " = 0"
    proceso.append("Combinación lineal de los vectores:")
    proceso.append(ecuacion)
    # 2. Obtener la solución general del sistema homogéneo Ax=0
    # Usamos la matriz escalonada A (ya reducida arriba)
    # Determinar variables libres y básicas
    # Use the reduced row-echelon coefficient matrix (from `A`) to determine pivots
    m_coef = len(A)
    n_coef = num_vars
    # Take the coefficient part from the reduced augmented matrix `A`
    A_coef = [fila[:-1] for fila in A]
    # Determine pivots by scanning each row of the reduced matrix for the first non-zero
    pivots_coef = []
    pivot_of_row = [-1] * m_coef
    for i in range(m_coef):
        for j in range(n_coef):
            if abs(A_coef[i][j]) > 1e-10:
                pivots_coef.append(j)
                pivot_of_row[i] = j
                break
    pivots_coef = list(dict.fromkeys(pivots_coef))
    libres_coef = [j for j in range(n_coef) if j not in pivots_coef]
    # Si hay libres, solución no trivial
    if not libres_coef:
        proceso.append("La única solución es c1 = c2 = ... = cn = 0 (trivial).")
        proceso.append("Por lo tanto, los vectores son LINEALMENTE INDEPENDIENTES.")
        valores_c = [0 for _ in range(num_vars)]
    else:
        proceso.append("Existen parámetros libres:")
        for l in libres_coef:
            proceso.append(f"  c{l+1} es libre (puede tomar cualquier valor).")
        proceso.append("Por lo tanto, los vectores son LINEALMENTE DEPENDIENTES.")
        # Para mostrar una solución no trivial, asigna 1 a la primera libre y despeja las básicas
        valores_c = [0 for _ in range(num_vars)]
        # Assign 1 to each free parameter to exhibit a non-trivial combination
        for l in libres_coef:
            valores_c[l] = 1
        # Despejar las variables básicas usando la matriz reducida
        # Recorremos las filas que tienen pivote y despejamos la variable básica correspondiente
        for i in range(m_coef):
            col = pivot_of_row[i]
            if col == -1:
                continue
            # suma de contribuciones de las variables libres en esta fila
            suma = 0
            for j in libres_coef:
                suma += A_coef[i][j] * valores_c[j]
            # En la forma reducida, el coeficiente de la variable básica debería ser 1
            valores_c[col] = -suma
        valores_c = [0 if abs(x) < 1e-10 else x for x in valores_c]
        proceso.append("Una combinación lineal no trivial es:")
        proceso.append("  " + ", ".join([f"c{j+1} = {valores_c[j]:.4f}" for j in range(num_vars)]))
    # 3. Reemplazar en la combinación lineal y mostrar el resultado
    proceso.append("\nReemplazando en la combinación lineal:")
    for i in range(len(vectores[0])):
        suma = sum(valores_c[j] * vectores[j][i] for j in range(num_vars))
        proceso.append("  " + " + ".join([f"{valores_c[j]:.4f}·{vectores[j][i]:.4f}" for j in range(num_vars)]) + f" = {suma:.4f}")
    # 4. Verificar si da 0=0 en todas las componentes
    if all(abs(sum(valores_c[j] * vectores[j][i] for j in range(num_vars))) < 1e-8 for i in range(len(vectores[0]))):
        proceso.append("\nLa combinación lineal da 0=0 en todas las componentes.")
        if not libres_coef:
            proceso.append("Por lo tanto, los vectores son LINEALMENTE INDEPENDIENTES.")
        else:
            proceso.append("Por lo tanto, los vectores son LINEALMENTE DEPENDIENTES.")
    else:
        proceso.append("\nLa combinación lineal NO da 0=0 en todas las componentes (¡esto no debería ocurrir si el proceso es correcto!).")

    return "\n".join(proceso)

# --- Dependencia e independencia lineal ---
def dependencia_lineal(vectores: List[List[float]]) -> bool:
    # Devuelve True si los vectores son linealmente dependientes
    import copy
    if not vectores:
        return False
    filas = len(vectores[0])
    columnas = len(vectores)
    matriz = [ [vectores[j][i] for j in range(columnas)] for i in range(filas) ]
    A = copy.deepcopy(matriz)
    n = filas
    m = columnas
    pivots = []
    row = 0
    for col in range(m):
        sel = None
        for i in range(row, n):
            if abs(A[i][col]) > 1e-10:
                sel = i
                break
        if sel is None:
            continue
        if sel != row:
            A[row], A[sel] = A[sel], A[row]
        piv = A[row][col]
        if abs(piv) < 1e-10:
            continue
        A[row] = [aij / piv for aij in A[row]]
        for i in range(n):
            if i != row and abs(A[i][col]) > 1e-10:
                factor = A[i][col]
                A[i] = [aij - factor * arj for aij, arj in zip(A[i], A[row])]
        pivots.append(col)
        row += 1
        if row == n:
            break
    libres = [j for j in range(m) if j not in pivots]
    return len(libres) > 0

def texto_dependencia_lineal(vectores: List[List[float]]) -> str:
    if dependencia_lineal(vectores):
        return "Los vectores son linealmente dependientes."
    else:
        return "Los vectores son linealmente independientes."

def dependencia_lineal_pasos(vectores: List[List[float]]) -> str:
    import copy
    if not vectores:
        return "No hay vectores."
    filas = len(vectores[0])
    columnas = len(vectores)
    matriz = [ [vectores[j][i] for j in range(columnas)] for i in range(filas) ]
    A = copy.deepcopy(matriz)
    n = filas
    m = columnas
    pivots = []
    row = 0
    pasos = []
    for col in range(m):
        sel = None
        for i in range(row, n):
            if abs(A[i][col]) > 1e-10:
                sel = i
                break
        if sel is None:
            pasos.append(f"Columna {col+1}: No hay pivote (variable libre)")
            continue
        if sel != row:
            pasos.append(f"f{row+1} <-> f{sel+1}")
            A[row], A[sel] = A[sel], A[row]
        piv = A[row][col]
        if abs(piv) < 1e-10:
            pasos.append(f"No se puede dividir por cero en la fila {row+1}.")
            continue
        if abs(piv - 1.0) > 1e-10:
            pasos.append(f"f{row+1} --> (1/{piv:.4f})*f{row+1}")
            A[row] = [aij / piv for aij in A[row]]
        for i in range(n):
            if i != row and abs(A[i][col]) > 1e-10:
                factor = A[i][col]
                signo = "+" if factor > 0 else "-"
                pasos.append(f"f{i+1} --> f{i+1} {signo} ({abs(factor):.4f})*f{row+1}")
                A[i] = [aij - factor * arj for aij, arj in zip(A[i], A[row])]
        pivots.append(col)
        row += 1
        if row == n:
            break
    libres = [j for j in range(m) if j not in pivots]
    if len(libres) == 0:
        pasos.append("La única solución es la trivial (todos los escalares cero).")
    else:
        pasos.append("Existen parámetros libres, hay soluciones no triviales.")
    return "\n".join(pasos)

def analizar_sistema_vectores(vectores: list[list[float]], b: list[float]) -> str:
    import copy
    filas = len(vectores[0]) if vectores else 0
    columnas = len(vectores)
    es_homogeneo = all(abs(val) < 1e-10 for val in b)
    resultado = []
    resultado.append(f"El sistema es {'homogéneo' if es_homogeneo else 'NO homogéneo'}.\n")
    matriz = [ [vectores[j][i] for j in range(columnas)] + [b[i]] for i in range(filas) ]
    m = copy.deepcopy(matriz)
    n = filas
    p = columnas
    pivots = []
    row = 0
    for col in range(p):
        sel = None
        for i in range(row, n):
            if abs(m[i][col]) > 1e-10:
                sel = i
                break
        if sel is None:
            continue
        if sel != row:
            m[row], m[sel] = m[sel], m[row]
        piv = m[row][col]
        if abs(piv) < 1e-10:
            continue
        m[row] = [aij / piv for aij in m[row]]
        for i in range(n):
            if i != row and abs(m[i][col]) > 1e-10:
                factor = m[i][col]
                m[i] = [aij - factor * arj for aij, arj in zip(m[i], m[row])]
        pivots.append(col)
        row += 1
        if row == n:
            break
    basicas = [f"x{p+1}" for p in pivots]
    libres = [f"x{j+1}" for j in range(columnas) if j not in pivots]
    resultado.append(f"Variables básicas ({len(basicas)}): {', '.join(basicas) if basicas else 'Ninguna'}")
    resultado.append(f"Variables libres ({len(libres)}): {', '.join(libres) if libres else 'Ninguna'}\n")
    dep = dependencia_lineal(vectores)
    resultado.append("Dependencia lineal de los vectores:")
    if dep:
        resultado.append("⇒ Los vectores son linealmente DEPENDIENTES (existe una combinación lineal no trivial igual a cero).")
    else:
        resultado.append("⇒ Los vectores son linealmente INDEPENDIENTES (la única combinación lineal igual a cero es la trivial).")
    return "\n".join(resultado)

def proceso_combinacion_lineal(vectores: list[list[float]]) -> str:
    # Ya no es necesario, el proceso está integrado en solucionMatrizVector
    return ""