# Método Gauss-Jordan sin librerías externas

def gauss_jordan(a):
    n = len(a)
    m = len(a[0])
    
    for i in range(n):
        # Pivote
        pivot = a[i][i]
        if pivot == 0:
            for j in range(i+1, n):
                if a[j][i] != 0:
                    a[i], a[j] = a[j], a[i]
                    pivot = a[i][i]
                    break
        
        # Normalizar fila
        for k in range(i, m):
            a[i][k] = a[i][k] / pivot
        
        # Hacer ceros arriba y abajo
        for j in range(n):
            if j != i:
                factor = a[j][i]
                for k in range(i, m):
                    a[j][k] -= factor * a[i][k]
    
    return a

# Matriz aumentada
matriz = [
    [3, 0, -2, 0, 0, 0],
    [1, 3, -1, 0, -2, 0],
    [0, 1, 0, -1, 0, 0],
    [0, 1, 0, 0, -1, 0]
]

resultado = gauss_jordan(matriz)

print("Matriz reducida:")
for fila in resultado:
    print([round(x, 2) for x in fila])
