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

    def matriz_str(m):
        # Formato tipo [1.0000 | 0.0625 | ... ]
        return "\n".join(
            " | ".join(f"{x:8.4f}" for x in fila)
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
        if abs(piv - 1.0) > 1e-10:
            proceso.append(f"\nf{row+1} --> (1/{piv:.4f})*f{row+1}")
            A[row] = [aij / piv for aij in A[row]]
            proceso.append(matriz_str(A))
        # Hacer ceros en la columna del pivote
        for i in range(n):
            if i != row and abs(A[i][col]) > 1e-10:
                factor = A[i][col]
                signo = "+" if factor > 0 else "-"
                proceso.append(f"\nf{i+1} --> f{i+1} {signo} ({abs(factor):.4f})*f{row+1}")
                A[i] = [aij - factor * arj for aij, arj in zip(A[i], A[row])]
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
            sol = [fila[-1] for fila in A]
            proceso.append(f"Solución única: {sol}")

    return "\n".join(proceso)