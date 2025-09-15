from fractions import Fraction


def pedir_vectores():
    print("\n--- Ingreso de vectores ---")
    tam = int(input("Tamaño del vector (número de filas): "))
    cant = int(input("Cantidad de vectores a trabajar: "))
    nombres = [chr(97 + i) for i in range(cant)]  # 'a', 'b', 'c', ...
    vectores = []
    for idx, nombre in enumerate(nombres):
        print(f"\nValores para el vector \033[1m{nombre}\033[0m:")
        vec = []
        for j in range(tam):
            val = input(f"Fila {j+1}: ")
            vec.append(Fraction(val))
        vectores.append(vec)
    print("\n--- Vectores creados ---")
    for idx, nombre in enumerate(nombres):
        print(f"\033[1m{nombre}\033[0m =")
        for val in vectores[idx]:
            print(f"|  {val}  |")
        print()
    return vectores, nombres

def operar_vectores(vectores, nombres):
    resultados = {}
    while True:
        print("\n¿Qué operación desea realizar?")
        print("1. Operar entre dos vectores (+, -, *)")
        print("2. Multiplicar uno o varios vectores por un escalar")
        print("3. Determinar combinación lineal")
        print("4. Salir")
        opcion = input("Seleccione opción (1/2/3/4): ").strip()
        if opcion == '1':
            if len(vectores) + len(resultados) < 2:
                print("Se requieren al menos dos vectores para operar.")
                continue
            print("\nOperaciones disponibles entre dos vectores:")
            print("+ : Suma")
            print("- : Resta")
            print("* : Producto elemento a elemento")
            op = input("Ingrese el signo de la operación (+, -, *): ").strip()
            todos_nombres = nombres + list(resultados.keys())
            print(f"Seleccione los vectores a operar (por nombre, ej: a b):")
            seleccion = input(f"Nombres de los dos vectores ({' '.join(todos_nombres)}): ").strip().split()
            if len(seleccion) != 2 or seleccion[0] not in todos_nombres or seleccion[1] not in todos_nombres:
                print("Selección inválida.")
                continue
            v1 = vectores[nombres.index(seleccion[0])] if seleccion[0] in nombres else resultados[seleccion[0]]
            v2 = vectores[nombres.index(seleccion[1])] if seleccion[1] in nombres else resultados[seleccion[1]]
            if len(v1) != len(v2):
                print("Los vectores deben tener el mismo tamaño.")
                continue
            if op == '+':
                resultado = [v1[i] + v2[i] for i in range(len(v1))]
                op_str = '+'
            elif op == '-':
                resultado = [v1[i] - v2[i] for i in range(len(v1))]
                op_str = '-'
            elif op == '*':
                resultado = [v1[i] * v2[i] for i in range(len(v1))]
                op_str = '*'
            else:
                print("Operación no soportada.")
                continue
            nombre_res = f"r{len(resultados)+1}"
            resultados[nombre_res] = resultado
            print(f"\nResultado de \033[1m{seleccion[0]} {op_str} {seleccion[1]}\033[0m =")
            for val in resultado:
                print(f"|  {val}  |")
            print(f"Guardado como vector \033[1m{nombre_res}\033[0m")
        elif opcion == '2':
            print("\nVectores disponibles para multiplicar por escalar:")
            todos_nombres = nombres + list(resultados.keys())
            print(" ".join(todos_nombres))
            seleccion = input("Ingrese los nombres de los vectores a multiplicar (separados por espacio): ").strip().split()
            escalar = Fraction(input("Ingrese el escalar: "))
            for nombre in seleccion:
                if nombre not in todos_nombres:
                    print(f"Vector {nombre} no existe.")
                    continue
                vec = vectores[nombres.index(nombre)] if nombre in nombres else resultados[nombre]
                resultado = [escalar * v for v in vec]
                nombre_res = f"r{len(resultados)+1}"
                resultados[nombre_res] = resultado
                print(f"\nResultado de \033[1m{escalar}*{nombre}\033[0m =")
                for val in resultado:
                    print(f"|  {val}  |")
                print(f"Guardado como vector \033[1m{nombre_res}\033[0m")
        elif opcion == '3':
            # Combinación lineal
            todos_nombres = nombres + list(resultados.keys())
            print("\nVectores disponibles:", " ".join(todos_nombres))
            seleccion = input("Ingrese los nombres de los vectores para la combinación lineal (separados por espacio): ").strip().split()
            if len(seleccion) == 0:
                print("Debe seleccionar al menos un vector.")
                continue
            vectores_sel = []
            for nombre in seleccion:
                if nombre not in todos_nombres:
                    print(f"Vector {nombre} no existe.")
                    break
                vec = vectores[nombres.index(nombre)] if nombre in nombres else resultados[nombre]
                vectores_sel.append(vec)
            else:
                print("Ingrese el vector objetivo (los valores separados por espacio, o '0' para vector cero):")
                objetivo_str = input(f"Vector objetivo de tamaño {len(vectores_sel[0])}: ").strip().split()
                if objetivo_str == ['0']:
                    objetivo = [Fraction(0) for _ in range(len(vectores_sel[0]))]
                elif len(objetivo_str) != len(vectores_sel[0]):
                    print("Tamaño incorrecto del vector objetivo.")
                    continue
                else:
                    objetivo = [Fraction(x) for x in objetivo_str]
                # Resolver sistema lineal: vectores_sel * [escalares] = objetivo
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
                        for i, nombre in enumerate(seleccion):
                            print(f"{sol.args[0][i]}*{nombre}")
                        print("Vector objetivo:")
                        for val in objetivo:
                            print(f"|  {val}  |")
                except ImportError:
                    print("Se requiere la librería sympy para esta operación.")
        elif opcion == '4':
            print("Saliendo del módulo de operaciones de vectores.")
            break
        else:
            print("Opción inválida.")

if __name__ == "__main__":
    vectores, nombres = pedir_vectores()
    operar_vectores(vectores, nombres)
