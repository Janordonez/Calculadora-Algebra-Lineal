# errores.py
# ------------------------------------------------------------
# Módulo de apoyo para Métodos Numéricos:
# - Notación posicional (base 10 y base 2)
# - Tipos de error numérico
# - Errores de punto flotante
# - Taller de pérdidas de precisión
# - Cálculo de error absoluto, relativo y propagación del error
#
# Uso:
#   from errores import ejecutar_modulo_errores
#   ejecutar_modulo_errores()
#
# También puede ejecutarse directamente:
#   python errores.py
# ------------------------------------------------------------

import math

# Intentar importar NumPy para el taller guiado (no es obligatorio)
try:
    import numpy as np
    TIENE_NUMPY = True
except Exception:
    TIENE_NUMPY = False


# ============================================================
# 1. NOTACIÓN POSICIONAL
# ============================================================

def descomponer_base10(numero: int) -> None:
    """
    Descompone un número entero en base 10 usando potencias de 10.
    Muestra cada paso en la consola.
    """
    print("\n--- Descomposición en base 10 ---")
    print(f"Número: {numero}")

    signo = -1 if numero < 0 else 1
    num_abs = abs(numero)
    cadena = str(num_abs)
    longitud = len(cadena)

    terminos = []
    for i, digito_char in enumerate(cadena):
        digito = int(digito_char)
        posicion = longitud - i - 1      # posición de la potencia
        potencia = 10 ** posicion
        termino = digito * potencia
        terminos.append(termino)
        print(f"{digito} × 10^{posicion} = {termino}")

    suma = sum(terminos) * signo
    expresion = " + ".join(
        f"{cadena[i]}×10^{longitud-i-1}" for i in range(longitud)
    )
    if signo < 0:
        expresion = "-(" + expresion + ")"

    print(f"\nForma desarrollada: {expresion}")
    print(f"Suma final: {suma}")


def descomponer_base2(numero: int) -> None:
    """
    Descompone un número entero en base 2 usando potencias de 2.
    Muestra cada paso en la consola.
    """
    print("\n--- Descomposición en base 2 ---")
    print(f"Número (entero decimal): {numero}")

    if numero < 0:
        raise ValueError("Para este ejemplo usaremos solo enteros no negativos.")

    binario = bin(numero)[2:]  # quitar '0b'
    print(f"Representación binaria: {binario}")

    longitud = len(binario)
    terminos = []
    for i, bit_char in enumerate(binario):
        bit = int(bit_char)
        posicion = longitud - i - 1       # potencia de 2
        potencia = 2 ** posicion
        termino = bit * potencia
        terminos.append(termino)
        print(f"{bit} · 2^{posicion} = {termino}")

    suma = sum(terminos)
    expresion = " + ".join(
        f"{binario[i]}·2^{longitud-i-1}" for i in range(longitud)
    )

    print(f"\nForma desarrollada: {expresion}")
    print(f"Suma final: {suma}")


def ejemplos_notacion_posicional() -> None:
    """Muestra los ejemplos obligatorios del enunciado."""
    print("\n=== EJEMPLOS OBLIGATORIOS DE NOTACIÓN POSICIONAL ===")

    # Ejemplo en base 10: 84 506
    ejemplo_base10 = 84506
    print("\nEjemplo base 10 (84506):")
    descomponer_base10(ejemplo_base10)

    # Ejemplo en base 2: 1111001 (como binario equivale a 121 en decimal)
    print("\nEjemplo base 2 (1111001):")
    binario_ejemplo = "1111001"
    longitud = len(binario_ejemplo)
    terminos = []
    print(f"Representación binaria: {binario_ejemplo}")
    for i, bit_char in enumerate(binario_ejemplo):
        bit = int(bit_char)
        posicion = longitud - i - 1
        potencia = 2 ** posicion
        termino = bit * potencia
        terminos.append(termino)
        print(f"{bit} · 2^{posicion} = {termino}")
    suma = sum(terminos)
    expresion = " + ".join(
        f"{binario_ejemplo[i]}·2^{longitud-i-1}" for i in range(longitud)
    )
    print(f"\nForma desarrollada: {expresion}")
    print(f"Suma final: {suma} (en decimal)")

    # Ejemplo con número ingresado por el usuario
    print("\n--- Ahora tú ---")
    try:
        n_usuario = int(input("Ingresa un entero en base 10 para descomponer: "))
        descomponer_base10(n_usuario)
        descomponer_base2(abs(n_usuario))
    except ValueError:
        print("Entrada inválida. Debes escribir un número entero.")


# ============================================================
# 2. CONCEPTOS DE ERROR EN MÉTODOS NUMÉRICOS
# ============================================================

def explicar_tipos_de_error() -> None:
    """
    Imprime explicaciones breves de diferentes tipos de error numérico.
    Cada explicación incluye un ejemplo simple.
    """
    print("\n=== CONCEPTOS DE ERROR EN MÉTODOS NUMÉRICOS ===")

    print("\n1) Error inherente")
    print("   Es la diferencia entre el valor real del fenómeno físico y el")
    print("   valor exacto del modelo matemático que usamos para describirlo.")
    print("   Ejemplo: medir la altura de una persona con una regla casera.")

    print("\n2) Error de redondeo")
    print("   Ocurre al representar números reales con un número finito de dígitos.")
    x = 1/3
    print(f"   Ejemplo: 1/3 ≈ {x:.5f} (se corta la expansión infinita 0.3333...).")

    print("\n3) Error de truncamiento")
    print("   Se produce al sustituir un proceso infinito por uno finito.")
    print("   Ejemplo: usar pocas iteraciones de una serie de Taylor para")
    print("   aproximar sin(x).")

    print("\n4) Overflow y underflow")
    print("   Overflow: cuando un número es demasiado grande para ser representado.")
    print("   Underflow: cuando un número positivo es tan pequeño que se aproxima a 0.")
    print("   (En Python se manifiesta como 'inf' o como 0.0).")

    print("\n5) Error del modelo matemático")
    print("   Ocurre cuando el modelo no refleja perfectamente la realidad.")
    print("   Ejemplo: suponer que la resistencia de un material es constante")
    print("   cuando en realidad depende de la temperatura.")


# ============================================================
# 3. EJEMPLOS CON NÚMEROS EN PUNTO FLOTANTE
# ============================================================

def ejemplo_punto_flotante_basico() -> None:
    """
    Muestra el clásico ejemplo 0.1 + 0.2 == 0.3 y explica el resultado.
    """
    print("\n=== EJEMPLO DE PUNTO FLOTANTE ===")
    resultado = (0.1 + 0.2 == 0.3)
    print("Evaluando: 0.1 + 0.2 == 0.3")
    print(f"Resultado lógico: {resultado}")
    print(f"0.1 + 0.2 = {0.1 + 0.2:.17f}")
    print(f"0.3       = {0.3:.17f}")
    print("\nExplicación:")
    print("En base 2, números como 0.1 y 0.2 no tienen representación exacta.")
    print("La computadora guarda aproximaciones binarias y al sumarlas aparece")
    print("un pequeño error de redondeo. Por eso la comparación da False.")


# ============================================================
# 4. TALLER GUIADO DE PÉRDIDA DE PRECISIÓN
# ============================================================

def taller_guiado_precision() -> None:
    """
    Muestra operaciones donde se pierda precisión.
    Si NumPy está disponible, también muestra cómo maneja floats.
    """
    print("\n=== TALLER GUIADO DE PÉRDIDA DE PRECISIÓN ===")

    # Suma repetida de 0.1
    print("\n1) Suma repetida de 0.1 (error de redondeo acumulado)")
    suma = 0.0
    for i in range(10):
        suma += 0.1
    print(f"Suma de 0.1 repetida 10 veces: {suma:.17f}")
    print("Teóricamente debería ser 1.0 exacto.")

    # Cancelación catastrófica
    print("\n2) Cancelación catastrófica")
    a = 1e16 + 1.0
    b = 1e16
    diferencia = a - b
    print(f"a = 1e16 + 1 => {a}")
    print(f"b = 1e16     => {b}")
    print(f"a - b        => {diferencia}")
    print("Aunque añadimos 1, al restar se pierde debido a la escala de 1e16.")

    if TIENE_NUMPY:
        print("\n3) Uso de NumPy (si está instalado)")
        x = np.float64(0.1)
        suma_np = np.float64(0.0)
        for _ in range(10):
            suma_np += x
        print(f"Suma con np.float64: {suma_np:.17f}")
        print("NumPy usa doble precisión estándar IEEE 754,")
        print("por lo que el comportamiento es muy similar al de float de Python.")
    else:
        print("\nNumPy no está instalado. Se muestran solo ejemplos con float estándar.")


# ============================================================
# 5. EJERCICIO PRINCIPAL: ERRORES Y PROPAGACIÓN
# ============================================================

def f(x: float) -> float:
    """Función de ejemplo: f(x) = sin(x) + x^2"""
    return math.sin(x) + x**2


def f_derivada(x: float) -> float:
    """Derivada analítica de f(x): f'(x) = cos(x) + 2x"""
    return math.cos(x) + 2*x


def calcular_errores(x_verdadero: float, x_aproximado: float):
    """
    Calcula error absoluto y relativo para x,
    y error en la función f(x) (propagación).
    """
    # Error en x
    error_abs_x = abs(x_verdadero - x_aproximado)
    error_rel_x = error_abs_x / abs(x_verdadero) if x_verdadero != 0 else float('inf')

    # Propagación del error mediante la función
    f_v = f(x_verdadero)
    f_a = f(x_aproximado)
    error_abs_f = abs(f_v - f_a)
    error_rel_f = error_abs_f / abs(f_v) if f_v != 0 else float('inf')

    # Aproximación teórica usando derivada: |f'(x_v)| * error_abs_x
    error_prop_teorico = abs(f_derivada(x_verdadero)) * error_abs_x

    return {
        "error_abs_x": error_abs_x,
        "error_rel_x": error_rel_x,
        "f_v": f_v,
        "f_a": f_a,
        "error_abs_f": error_abs_f,
        "error_rel_f": error_rel_f,
        "error_prop_teorico": error_prop_teorico,
    }


def ejercicio_principal() -> None:
    """
    Pide al usuario valor verdadero y aproximado,
    calcula errores y muestra resultados en forma tabular,
    incluyendo interpretación breve.
    """
    print("\n=== EJERCICIO PRINCIPAL: ERROR Y PROPAGACIÓN ===")
    print("Usaremos la función f(x) = sin(x) + x^2")

    try:
        x_v = float(input("Ingresa el valor verdadero x_v: "))
        x_a = float(input("Ingresa el valor aproximado x_a: "))
    except ValueError:
        print("Entrada inválida. Debes introducir números reales.")
        return

    datos = calcular_errores(x_v, x_a)

    # Tabla de resultados
    print("\n--- Resultados ---")
    print("{:<35} {:>20}".format("Magnitud", "Valor"))
    print("-" * 57)
    print("{:<35} {:>20.10f}".format("x verdadero (x_v)", x_v))
    print("{:<35} {:>20.10f}".format("x aproximado (x_a)", x_a))
    print("{:<35} {:>20.10e}".format("Error absoluto en x (E_a)", datos["error_abs_x"]))
    print("{:<35} {:>20.10e}".format("Error relativo en x (E_r)", datos["error_rel_x"]))
    print("{:<35} {:>20.10f}".format("f(x_v)", datos["f_v"]))
    print("{:<35} {:>20.10f}".format("f(x_a)", datos["f_a"]))
    print("{:<35} {:>20.10e}".format("Error abs. en f(x)", datos["error_abs_f"]))
    print("{:<35} {:>20.10e}".format("Error rel. en f(x)", datos["error_rel_f"]))
    print("{:<35} {:>20.10e}".format("Aprox. teórica |f'(x_v)|·E_a", datos["error_prop_teorico"]))

    # Interpretación breve
    print("\n--- Interpretación ---")
    porcentaje_rel_x = datos["error_rel_x"] * 100
    porcentaje_rel_f = datos["error_rel_f"] * 100
    print(f"El error relativo en x es aproximadamente {porcentaje_rel_x:.4f} %.")
    print("Esto indica qué tan grande es el error respecto al valor verdadero de x.")
    print(f"Al pasar x por la función f(x), el error relativo en f(x) es")
    print(f"aproximadamente {porcentaje_rel_f:.4f} %.")
    print("Si el error relativo en f(x) es mayor que el error relativo en x,")
    print("decimos que la función amplifica los errores (propagación del error).")
    print("La cantidad |f'(x_v)|·E_a es una aproximación teórica del error en f(x)")
    print("debido a un pequeño error en x.")


# ============================================================
# 6. MENÚ PRINCIPAL DEL MÓDULO (PARA USO EN CONSOLA)
# ============================================================

def mostrar_menu():
    print("\n==============================================")
    print(" MÓDULO DE ERRORES NUMÉRICOS")
    print("==============================================")
    print("1) Notación posicional (base 10 y base 2)")
    print("2) Conceptos de error en métodos numéricos")
    print("3) Ejemplo 0.1 + 0.2 == 0.3")
    print("4) Taller guiado de precisión (float / NumPy)")
    print("5) Ejercicio principal: error y propagación")
    print("0) Salir")
    print("==============================================")


def ejecutar_modulo_errores():
    """
    Bucle de menú para usar el módulo desde consola.
    Puedes llamar a esta función desde tu Calculadora general.
    """
    while True:
        mostrar_menu()
        opcion = input("Elige una opción: ").strip()

        if opcion == "1":
            ejemplos_notacion_posicional()
        elif opcion == "2":
            explicar_tipos_de_error()
        elif opcion == "3":
            ejemplo_punto_flotante_basico()
        elif opcion == "4":
            taller_guiado_precision()
        elif opcion == "5":
            ejercicio_principal()
        elif opcion == "0":
            print("Saliendo del módulo de errores numéricos...")
            break
        else:
            print("Opción inválida, intenta de nuevo.")


# Permite ejecutar el módulo directamente
if __name__ == "__main__":
    ejecutar_modulo_errores()
