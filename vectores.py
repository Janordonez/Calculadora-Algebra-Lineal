from fractions import Fraction 



def operar_vectores(vectores, nombres):
    resultados = {}
    while True:
        print("\n¿Qué operación desea realizar?")
        print("1. Operar entre dos vectores (+, -, *)")
        print("2. Multiplicar uno o varios vectores por un escalar")
        print("3. Determinar combinación lineal")
        print("4. Resolver sistema de ecuaciones con vectores")
        print("5. Multiplicación de matriz por vector como combinación lineal de columnas")
        print("6. Salir")
        opcion = input("Seleccione opción (1/2/3/4/5/6): ").strip()

        if opcion == '1':
            tam = int(input("Tamaño de los vectores: "))
            print("Ingrese los valores del primer vector:")
            v1 = [Fraction(input(f"Elemento {i+1}: ")) for i in range(tam)]
            print("Ingrese los valores del segundo vector:")
            v2 = [Fraction(input(f"Elemento {i+1}: ")) for i in range(tam)]
            op = input("Ingrese el signo de la operación (+, -, *): ").strip()
            if op == '+':
                resultado = [v1[i] + v2[i] for i in range(tam)]
                op_str = '+'
            elif op == '-':
                resultado = [v1[i] - v2[i] for i in range(tam)]
                op_str = '-'
            elif op == '*':
                resultado = [v1[i] * v2[i] for i in range(tam)]
                op_str = '*'
            else:
                print("Operación no soportada.")
                break
            print(f"\nResultado de v1 {op_str} v2 =")
            for val in resultado:
                print(f"|  {val}  |")

        elif opcion == '2':
            tam = int(input("Tamaño de los vectores: "))
            cantidad = int(input("Cantidad de vectores a multiplicar por escalar: "))
            vectores = []
            for idx in range(cantidad):
                print(f"Ingrese los valores del vector {idx+1}:")
                vec = [Fraction(input(f"Elemento {i+1}: ")) for i in range(tam)]
                vectores.append(vec)
            escalar = Fraction(input("Ingrese el escalar: "))
            for idx, vec in enumerate(vectores):
                resultado = [escalar * v for v in vec]
                print(f"\nResultado de {escalar}*vector{idx+1} =")
                for val in resultado:
                    print(f"|  {val}  |")

        elif opcion == '3':
            cantidad = int(input("Cantidad de vectores para la combinación lineal: "))
            tam = int(input("Tamaño de los vectores: "))
            vectores_sel = []
            for idx in range(cantidad):
                print(f"Ingrese los valores del vector {idx+1}:")
                vec = [Fraction(input(f"Elemento {i+1}: ")) for i in range(tam)]
                vectores_sel.append(vec)
            print("Ingrese el vector objetivo (los valores separados por espacio, o '0' para vector cero):")
            objetivo_str = input(f"Vector objetivo de tamaño {tam}: ").strip().split()
            if objetivo_str == ['0']:
                objetivo = [Fraction(0) for _ in range(tam)]
            elif len(objetivo_str) != tam:
                print("Tamaño incorrecto del vector objetivo.")
                break
            else:
                objetivo = [Fraction(x) for x in objetivo_str]
            try:
                from sympy import Matrix, linsolve, symbols
                mat = Matrix(vectores_sel).T
                b = Matrix(objetivo)
                escalares = symbols(f'c1:{len(vectores_sel)+1}')
                sol = linsolve((mat, b), *escalares)
                if not sol or len(sol) == 0:
                    print("No existe una combinación lineal que genere el vector objetivo.")
                else:
                    print("Existe una combinación lineal:")
                    for i in range(cantidad):
                        print(f"{sol.args[0][i]}*vector{i+1}")
                    print("Vector objetivo:")
                    for val in objetivo:
                        print(f"|  {val}  |")
            except ImportError:
                print("Se requiere la librería sympy para esta operación.")

        elif opcion == '4':
            # Resolver sistema de ecuaciones con vectores y mostrar Ax = b y combinación lineal de columnas
            m = int(input("Número de variables (incógnitas): "))
            n = int(input("Número de ecuaciones (tamaño del vector, filas): "))
            print("Introduce las variables (ejemplo: x y z):")
            while True:
                variables = input().strip().split()
                if len(variables) != m:
                    print(f"Debes ingresar exactamente {m} variables. Intenta de nuevo.")
                else:
                    break
            matriz = []
            print(f"\nVas a ingresar {n} ecuaciones, cada una con {m} variables y el término independiente.")
            print("Ejemplo para 2 ecuaciones y 2 variables:")
            print("Ecuación 1: coef_x1 coef_x2 término_independiente")
            print("Ecuación 2: coef_x1 coef_x2 término_independiente")
            for i in range(n):
                while True:
                    fila = input(f"Ecuación {i+1}: Ingresa los {m} coeficientes y el término independiente separados por espacio: ").strip().split()
                    if len(fila) != m+1:
                        print(f"Cantidad incorrecta. Debes ingresar exactamente {m} coeficientes y 1 término independiente. Intenta de nuevo.")
                    else:
                        matriz.append([Fraction(x) for x in fila])
                        break
            # Separar coeficientes y términos independientes
            coef_matrix = [[matriz[i][j] for i in range(n)] for j in range(m)]  # columnas: cada variable
            b = [matriz[i][-1] for i in range(n)]
            # Paso 1: mostrar matriz A
            print("\nMatriz A:")
            A = [[matriz[i][j] for j in range(m)] for i in range(n)]
            for fila in A:
                print(fila)
            # Paso 2: mostrar vector incógnitas
            print("\nVector de incógnitas x:")
            print(variables)
            # Paso 3: mostrar vector b
            print("\nVector b:")
            print(b)
            # Paso 4: Forma matricial Ax = b
            print("\nForma matricial Ax = b:")
            comb_str = []
            for j in range(m):
                columna = [A[i][j] for i in range(n)]
                comb_str.append(f"{variables[j]} * {columna}")
            print(" + ".join(comb_str), "=", b)
            # Paso 5: mostrar vectores individuales de cada variable
            print("\nVectores individuales de cada variable:")
            for idx, col in enumerate(coef_matrix):
                print(f"Vector {variables[idx]}:")
                for val in col:
                    print(f"| {val} |")
                print()
            print("Vector de términos independientes:")
            for val in b:
                print(f"| {val} |")
            print()
            # Matriz aumentada por columnas
            print("Matriz aumentada inicial (columnas: x1, x2, ..., xn, término independiente):")
            aug = [[matriz[i][j] for j in range(m)] + [matriz[i][-1]] for i in range(n)]
            for fila in aug:
                print("[ " + "  ".join(str(x) for x in fila) + " ]")
            from sympy import Matrix
            aug_matrix = Matrix(aug)
            print("\n--- Paso a paso de reducción de filas ---")
            matriz_pasos = aug_matrix.copy()
            nrows, ncols = matriz_pasos.shape
            for i in range(min(nrows, ncols-1)):
                # Buscar pivote
                if matriz_pasos[i, i] == 0:
                    for k in range(i+1, nrows):
                        if matriz_pasos[k, i] != 0:
                            matriz_pasos.row_swap(i, k)
                            print(f"f{i+1} <-> f{k+1} (Intercambio de filas)")
                            for fila in matriz_pasos.tolist():
                                print("[ " + "  ".join(str(x) for x in fila) + " ]")
                            break
                # Hacer pivote 1
                pivote = matriz_pasos[i, i]
                if pivote != 0 and pivote != 1:
                    matriz_pasos.row_op(i, lambda x, _: x / pivote)
                    print(f"f{i+1} -> (1/{pivote})*f{i+1}")
                    for fila in matriz_pasos.tolist():
                        print("[ " + "  ".join(str(x) for x in fila) + " ]")
                # Eliminar debajo
                for k in range(i+1, nrows):
                    factor = matriz_pasos[k, i]
                    if factor != 0:
                        matriz_pasos.row_op(k, lambda x, j: x - factor * matriz_pasos[i, j])
                        print(f"f{k+1} -> f{k+1} - ({factor})*f{i+1}")
                        for fila in matriz_pasos.tolist():
                            print("[ " + "  ".join(str(x) for x in fila) + " ]")
            print("\nMatriz en forma escalonada reducida (rref):")
            rref, pivots = aug_matrix.rref()
            for fila in rref.tolist():
                print("[ " + "  ".join(str(x) for x in fila) + " ]")
            # Mostrar pivotes y variables en formato usuario
            print("Pivotes en columnas:", [p+1 for p in pivots])
            basicas = [p+1 for p in pivots]
            libres = [i+1 for i in range(m) if (i+1) not in basicas]
            print("Variables básicas:", [variables[b-1] for b in basicas])
            print("Variables libres:", [variables[l-1] for l in libres])

            # Determinar si el sistema es homogéneo o no
            es_homogeneo = all(val == 0 for val in b)
            if es_homogeneo:
                print("\nEl sistema es homogéneo (Ax = 0)")
                if len(libres) > 0:
                    print("La ecuación homogénea Ax = 0 tiene una solución no trivial porque hay al menos una variable libre.")
                else:
                    print("La ecuación homogénea Ax = 0 solo tiene la solución trivial (todas las variables son básicas).")
            else:
                print("\nEl sistema es no homogéneo (Ax = b)")
            # Mostrar conjunto solución (solo mensaje informativo)
            print("Conjunto solución del sistema lineal:")
            print("Variables básicas:", [variables[b-1] for b in basicas])
            print("Variables libres:", [variables[l-1] for l in libres])
        elif opcion == '5':
            # Multiplicación de matriz por vector como combinación lineal de columnas
            filas = int(input("Número de filas de la matriz: "))
            columnas = int(input("Número de columnas de la matriz: "))
            matriz = []
            print("Introduce la matriz fila por fila (separando elementos con espacio):")
            for i in range(filas):
                fila = list(map(Fraction, input(f"Fila {i+1}: ").split()))
                if len(fila) != columnas:
                    print(f"La fila debe tener exactamente {columnas} elementos.")
                    return
                matriz.append(fila)
            print("Introduce el vector columna (separando elementos con espacio):")
            vector = list(map(Fraction, input().split()))
            if len(vector) != columnas:
                print(f"El vector debe tener exactamente {columnas} elementos.")
                return
            # Calcular producto
            resultado = [0] * filas
            for j in range(columnas):
                for i in range(filas):
                    resultado[i] += matriz[i][j] * vector[j]
            # Verificar si el resultado es combinación lineal de las columnas de la matriz
            from sympy import Matrix
            matriz_sym = Matrix(matriz)
            resultado_sym = Matrix(resultado)
            try:
                sol = matriz_sym.solve_least_squares(resultado_sym)
                if matriz_sym * sol == resultado_sym:
                    print("\nEl resultado SÍ puede expresarse como combinación lineal de las columnas de la matriz.\n")
                    print("PROCESO de la combinación lineal:")
                    print("Sea x1, x2, ..., xn los escalares que multiplican cada columna:")
                    print("\nSistema de ecuaciones:")
                    for i in range(filas):
                        ecuacion = " + ".join([f"({matriz[i][j]})*x{j+1}" for j in range(columnas)])
                        print(f"{ecuacion} = {resultado[i]}")
                    print("\nResolviendo el sistema, se obtiene:")
                    for idx, escalar in enumerate(sol):
                        print(f"x{idx+1} = {escalar}")
                    print("\nCombinación lineal explícita:")
                    cols = [ [matriz[i][j] for i in range(filas)] for j in range(columnas)]
                    suma = " + ".join([f"({escalar})*{col}" for escalar, col in zip(sol, cols)])
                    print(f"{resultado} = {suma}")
                else:
                    print("\nEl resultado NO puede expresarse exactamente como combinación lineal de las columnas de la matriz.\n")
                    print("PROCESO del intento de combinación lineal:")
                    print("Sea x1, x2, ..., xn los escalares que multiplican cada columna:")
                    print("\nSistema de ecuaciones:")
                    for i in range(filas):
                        ecuacion = " + ".join([f"({matriz[i][j]})*x{j+1}" for j in range(columnas)])
                        print(f"{ecuacion} = {resultado[i]}")
                    print("\nAl resolver el sistema, no se obtiene una solución exacta para los escalares.")
            except Exception as e:
                print("\nNo se pudo determinar si el resultado es combinación lineal de las columnas de la matriz:", e)
            # Mostrar resultado
            print("\nResultado del producto:", resultado)
            # Mostrar combinación lineal
            print("\nCombinación lineal de columnas:")
            for j in range(columnas):
                col = [matriz[i][j] for i in range(filas)]
                print(f"{vector[j]} * {col}")
        elif opcion == '6':
            print("Saliendo del menú de operaciones de vectores.")
            return



# --- Bloque main para pruebas en terminal ---
if __name__ == "__main__":
    print("Calculadora de Álgebra Lineal - Modo Terminal")
    # Se puede iniciar con vectores vacíos y nombres vacíos
    operar_vectores([], [])