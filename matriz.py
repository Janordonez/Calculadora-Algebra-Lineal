# matriz.py
from fractions import Fraction

def gauss_elimination(A, b):
    """
    Resuelve Ax = b usando eliminación de Gauss con retro-sustitución.
    - A: lista de listas con Fraction
    - b: lista con Fraction
    Retorna: lista con la solución (Fraction) o None si no hay solución única.
    """
    n = len(A)
    # Creamos matriz aumentada
    M = [row[:] + [b[i]] for i, row in enumerate(A)]

    # Eliminación hacia adelante
    for i in range(n):
        # Buscar pivote
        if M[i][i] == 0:
            for k in range(i+1, n):
                if M[k][i] != 0:
                    M[i], M[k] = M[k], M[i]
                    break
            else:
                print("No hay solución única (matriz singular).")
                return None

        # Normalizar fila
        pivote = M[i][i]
        for j in range(i, n+1):
            M[i][j] = M[i][j] / pivote

        # Eliminar debajo
        for k in range(i+1, n):
            factor = M[k][i]
            for j in range(i, n+1):
                M[k][j] -= factor * M[i][j]

    # Retro-sustitución
    x = [Fraction(0) for _ in range(n)]
    for i in range(n-1, -1, -1):
        x[i] = M[i][n]
        for j in range(i+1, n):
            x[i] -= M[i][j] * x[j]

    # Imprimir resultados
    print("Solución única (exacta):")
    for i, val in enumerate(x):
        print(f"x{i+1} = {val} = {float(val)}")
    return x
