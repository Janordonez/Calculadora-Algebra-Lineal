from typing import List

class Vector:
    def __init__(self, datos: List[float]):
        self.datos = datos[:]

    def suma(self, otro: 'Vector') -> 'Vector':
        if len(self.datos) != len(otro.datos):
            raise ValueError('Los vectores deben tener el mismo tamaño para sumar.')
        return Vector([self.datos[i] + otro.datos[i] for i in range(len(self.datos))])

    def resta(self, otro: 'Vector') -> 'Vector':
        if len(self.datos) != len(otro.datos):
            raise ValueError('Los vectores deben tener el mismo tamaño para restar.')
        return Vector([self.datos[i] - otro.datos[i] for i in range(len(self.datos))])

    def escalar(self, esc: float) -> 'Vector':
        return Vector([x * esc for x in self.datos])

    def multiplicacion(self, otro: 'Vector') -> 'Vector':
        if len(self.datos) != len(otro.datos):
            raise ValueError('Los vectores deben tener el mismo tamaño para multiplicar.')
        return Vector([self.datos[i] * otro.datos[i] for i in range(len(self.datos))])

    def eliminar_coma_punto(self) -> 'Vector':
        datos_limpios = []
        for x in self.datos:
            s = str(x).replace(',', '').replace('.', '')
            try:
                datos_limpios.append(float(s))
            except ValueError:
                datos_limpios.append(0.0)
        return Vector(datos_limpios)

    def mostrar(self):
        print(self.datos)

def solucionMatrizVector(vectores: list[list[float]]) -> str:
    """
    Muestra el proceso de reducción de la matriz paso a paso, indicando la matriz antes y después de cada operación,
    la fila pivote y las operaciones realizadas, con formato tipo calculadora visual.
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
        elif len(libres) > 0:
            proceso.append("El sistema tiene infinitas soluciones (parámetros libres).")
        else:
            sol = [clean(fila[-1]) for fila in A]
            proceso.append(f"Solución única: {sol}")

    return "\n".join(proceso)

# --- Dependencia e independencia lineal ---
def dependencia_lineal(vectores: List[List[float]]) -> bool:
    """
    Devuelve True si los vectores son linealmente dependientes, False si son independientes.
    Usa reducción por filas (Gauss) para calcular el rango.
    """
    import copy
    if not vectores:
        return False
    matriz = [list(col) for col in zip(*vectores)]
    filas = len(matriz)
    columnas = len(matriz[0]) if filas > 0 else 0
    A = copy.deepcopy(matriz)
    rango = 0
    EPS = 1e-10
    row = 0
    for col in range(columnas):
        sel = None
        for i in range(row, filas):
            if abs(A[i][col]) > EPS:
                sel = i
                break
        if sel is None:
            continue
        if sel != row:
            A[row], A[sel] = A[sel], A[row]
        piv = A[row][col]
        if abs(piv) < 1e-10:
            continue
        A[row] = [aij / piv if abs(piv) > 1e-10 else 0.0 for aij in A[row]]
        A[row] = [0.0 if abs(x) < 1e-10 else x for x in A[row]]
        for i in range(filas):
            if i != row and abs(A[i][col]) > 1e-10:
                factor = A[i][col]
                A[i] = [aij - factor * arj for aij, arj in zip(A[i], A[row])]
                A[i] = [0.0 if abs(x) < 1e-10 else x for x in A[i]]
        rango += 1
        row += 1
        if row == filas:
            break
    return rango < len(vectores)

def texto_dependencia_lineal(vectores: List[List[float]]) -> str:
    if dependencia_lineal(vectores):
        return "Los vectores son linealmente dependientes."
    else:
        return "Los vectores son linealmente independientes."

def dependencia_lineal_pasos(vectores: List[List[float]]) -> str:
    """
    Devuelve el paso a paso del método de Gauss para dependencia/independencia lineal.
    """
    import copy
    if not vectores:
        return "No se ingresaron vectores."
    matriz = [list(col) for col in zip(*vectores)]
    filas = len(matriz)
    columnas = len(matriz[0]) if filas > 0 else 0
    A = copy.deepcopy(matriz)
    pasos = []
    def clean(x):
        return 0.0 if abs(x) < 1e-10 else x
    pasos.append("Matriz formada por los vectores como columnas:")
    for fila in A:
        pasos.append("  " + "  ".join(f"{clean(x):8.4f}" for x in fila))
    rango = 0
    EPS = 1e-10
    row = 0
    for col in range(columnas):
        sel = None
        for i in range(row, filas):
            if abs(A[i][col]) > EPS:
                sel = i
                break
        if sel is None:
            pasos.append(f"Columna {col+1}: No hay pivote (columna nula o combinación lineal).")
            continue
        if sel != row:
            pasos.append(f"Intercambio de filas: fila {row+1} <-> fila {sel+1}")
            A[row], A[sel] = A[sel], A[row]
            for fila in A:
                pasos.append("  " + "  ".join(f"{clean(x):8.4f}" for x in fila))
        piv = A[row][col]
        if abs(piv) < 1e-10:
            pasos.append(f"No se puede dividir por cero en la fila {row+1}.")
            continue
        if abs(piv - 1.0) > 1e-10:
            pasos.append(f"Normalización de fila {row+1}: dividir por {piv:.4f}")
            A[row] = [aij / piv if abs(piv) > 1e-10 else 0.0 for aij in A[row]]
            A[row] = [clean(x) for x in A[row]]
            for fila in A:
                pasos.append("  " + "  ".join(f"{clean(x):8.4f}" for x in fila))
        for i in range(filas):
            if i != row and abs(A[i][col]) > 1e-10:
                factor = A[i][col]
                signo = "+" if factor > 0 else "-"
                pasos.append(f"Fila {i+1} --> Fila {i+1} {signo} ({abs(factor):.4f}) * Fila {row+1}")
                A[i] = [aij - factor * arj for aij, arj in zip(A[i], A[row])]
                A[i] = [clean(x) for x in A[i]]
                for fila in A:
                    pasos.append("  " + "  ".join(f"{clean(x):8.4f}" for x in fila))
        rango += 1
        row += 1
        if row == filas:
            break
    pasos.append(f"\nRango de la matriz: {rango}")
    if rango < len(vectores):
        pasos.append("⇒ Los vectores son linealmente dependientes.")
    else:
        pasos.append("⇒ Los vectores son linealmente independientes.")
    return "\n".join(pasos)