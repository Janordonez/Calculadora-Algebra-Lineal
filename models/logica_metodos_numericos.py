"""
logica_metodos_numericos.py

Módulo de lógica de los métodos numéricos:
- Evaluar funciones f(x)
- Método de Bisección
- Método de Regla Falsa

NO tiene interfaz, solo lógica reutilizable.
"""

import math


# ============================================================
# EVALUADOR SEGURO DE f(x)
# ============================================================

def evaluar_funcion(expr: str, x: float) -> float:
    """
    Evalúa f(x) a partir de una cadena, por ejemplo:
    - 'x**3 - 4*x + 1'
    - 'math.sin(x) - x/2'

    Se permite usar funciones del módulo math.
    """
    expr = expr.strip()
    entorno = {
        "__builtins__": None,
        "math": math,
        # atajos:
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "exp": math.exp,
        "log": math.log,
        "sqrt": math.sqrt,
        "pi": math.pi,
        "e": math.e,
    }
    try:
        return eval(expr, entorno, {"x": x})
    except Exception as e:
        raise ValueError(f"Error al evaluar la función en x={x}: {e}")


# ============================================================
# MÉTODO DE BISECCIÓN
# ============================================================

def biseccion(expr: str, a: float, b: float, tol: float, max_iter: int = 100):
    """
    Método de Bisección.

    Parámetros:
        expr: cadena con la función f(x)
        a, b: extremos del intervalo [a,b]
        tol: tolerancia para el error relativo (NO en %)
        max_iter: máximo de iteraciones

    Retorna:
        raiz_aprox: float
        historia: lista de diccionarios por iteración con:
            - iter         (número de iteración)
            - a            (xl)
            - b            (xu)
            - x            (xr = punto medio)
            - fa           (f(a))
            - fb           (f(b))
            - fx           (f(x))
            - error_pct    (Ea en %; None en la primera iteración)
            - len_interval (b - a)
        intervalo_final: (a_final, b_final)
        error_final: error relativo porcentual final
    """

    # f(a) y f(b) al inicio del intervalo
    fa = evaluar_funcion(expr, a)
    fb = evaluar_funcion(expr, b)

    if fa * fb > 0:
        raise ValueError("El intervalo no es válido: f(a) y f(b) tienen el mismo signo.")

    historia = []
    x_old = None
    error_final = None

    for i in range(1, max_iter + 1):
        # Punto medio
        x_mid = (a + b) / 2.0
        fx_mid = evaluar_funcion(expr, x_mid)

        # Longitud actual del intervalo
        len_interval = abs(b - a)

        # Error relativo porcentual (usando xr nuevo y xr anterior)
        if x_old is None:
            error_rel = None
        else:
            if x_mid != 0:
                error_rel = abs((x_mid - x_old) / x_mid)
            else:
                error_rel = abs(x_mid - x_old)

        error_pct = None if error_rel is None else error_rel * 100.0

        historia.append(
            {
                "iter": i,
                "a": a,           # xl
                "b": b,           # xu
                "x": x_mid,       # xr
                "fa": fa,         # f(xl)
                "fb": fb,         # f(xu)
                "fx": fx_mid,     # f(xr)
                "error_pct": error_pct,   # Ea (%)
                "len_interval": len_interval,  # xu - xl
            }
        )

        # Criterio de parada por error relativo
        if error_rel is not None and error_rel < tol:
            error_final = error_pct
            break

        # Actualizar el intervalo según el cambio de signo
        if fa * fx_mid < 0:
            # La raíz está en [a, x_mid]
            b = x_mid
            fb = fx_mid
        else:
            # La raíz está en [x_mid, b]
            a = x_mid
            fa = fx_mid

        x_old = x_mid

    raiz_aprox = x_mid
    if error_final is None:
        error_final = error_pct

    intervalo_final = (a, b)
    return raiz_aprox, historia, intervalo_final, error_final


# ============================================================
# MÉTODO DE REGLA FALSA
# ============================================================

def regla_falsa(expr: str, a: float, b: float, tol: float, max_iter: int = 100):
    """
    Método de Regla Falsa (falsa posición).

    Parámetros:
        expr: cadena con la función f(x)
        a, b: extremos del intervalo [a,b]
        tol: tolerancia para el error relativo (NO en %)
        max_iter: máximo de iteraciones

    Retorna:
        raiz_aprox: float
        historia: lista de diccionarios por iteración con:
            - iter
            - a, b
            - x            (xr de Regla Falsa)
            - fa, fb, fx   (f(a), f(b), f(x))
            - error_pct    (Ea en %)
            - ea_less_tol  (True/False según Ea < tol%)
            - len_interval (b - a)
        intervalo_final: (a_final, b_final)
        error_final: error relativo porcentual final
    """
    fa = evaluar_funcion(expr, a)
    fb = evaluar_funcion(expr, b)

    if fa * fb > 0:
        raise ValueError("El intervalo no es válido: f(a) y f(b) tienen el mismo signo.")

    historia = []
    x_old = None
    error_final = None

    for i in range(1, max_iter + 1):
        denom = (fb - fa)
        if denom == 0:
            raise ZeroDivisionError("fb - fa = 0, no se puede continuar.")

        x_r = b - fb * (b - a) / denom
        f_xr = evaluar_funcion(expr, x_r)

        len_interval = abs(b - a)

        if x_old is None:
            error_rel = None
        else:
            if x_r != 0:
                error_rel = abs((x_r - x_old) / x_r)
            else:
                error_rel = abs(x_r - x_old)

        error_pct = None if error_rel is None else error_rel * 100.0
        ea_less_tol = False
        if error_rel is not None and error_rel < tol:
            ea_less_tol = True

        historia.append(
            {
                "iter": i,
                "a": a,
                "b": b,
                "x": x_r,
                "fa": fa,
                "fb": fb,
                "fx": f_xr,
                "error_pct": error_pct,
                "ea_less_tol": ea_less_tol,
                "len_interval": len_interval,
            }
        )

        if ea_less_tol:
            error_final = error_pct
            break

        # Actualizar intervalo según el cambio de signo
        if fa * f_xr < 0:
            b = x_r
            fb = f_xr
        else:
            a = x_r
            fa = f_xr

        x_old = x_r

    raiz_aprox = x_r
    if error_final is None:
        error_final = error_pct

    intervalo_final = (a, b)
    return raiz_aprox, historia, intervalo_final, error_final


# ============================================================
# IMPRESIÓN EN CONSOLA
# ============================================================

def imprimir_tabla_iteraciones(historia, nombre_metodo: str):
    """
    Función de apoyo para la INTERFAZ de consola.
    Recibe la historia y escribe una tabla en stdout.

    - Para Bisección: muestra 9 columnas
      (iter, xl, xu, xr, Ea, vl, vu, vr, xu-xl)

    - Para Regla Falsa: muestra 9 columnas
      (iter, xl, xu, xr, Ea, vl, vu, vr, Ea<E)
    """
    if nombre_metodo.lower().startswith("bise"):
        print(f"\n=== Iteraciones (Bisección) ===")
        encabezado = (
            f"{'Iter':>4} | {'xl':>8} | {'xu':>8} | {'xr':>8} | "
            f"{'Ea %':>8} | {'f(xl)':>10} | {'f(xu)':>10} | "
            f"{'f(xr)':>10} | {'(xu-xl)':>10}"
        )
        print(encabezado)
        print("-" * len(encabezado))

        for fila in historia:
            err_str = "---"
            if fila["error_pct"] is not None:
                err_str = f"{fila['error_pct']:8.4f}"

            print(
                f"{fila['iter']:4d} | "
                f"{fila['a']:8.4f} | "
                f"{fila['b']:8.4f} | "
                f"{fila['x']:8.4f} | "
                f"{err_str:>8} | "
                f"{fila['fa']:10.4f} | "
                f"{fila['fb']:10.4f} | "
                f"{fila['fx']:10.4f} | "
                f"{fila['len_interval']:10.4f}"
            )

    else:  # Regla Falsa
        print(f"\n=== Iteraciones (Regla Falsa) ===")
        encabezado = (
            f"{'Iter':>4} | {'xl':>8} | {'xu':>8} | {'xr':>8} | "
            f"{'Ea %':>8} | {'f(xl)':>10} | {'f(xu)':>10} | "
            f"{'f(xr)':>10} | {'Ea<E':>6}"
        )
        print(encabezado)
        print("-" * len(encabezado))

        for fila in historia:
            err_str = "---"
            if fila["error_pct"] is not None:
                err_str = f"{fila['error_pct']:8.4f}"
            ea_flag = "True" if fila.get("ea_less_tol") else "False"

            print(
                f"{fila['iter']:4d} | "
                f"{fila['a']:8.4f} | "
                f"{fila['b']:8.4f} | "
                f"{fila['x']:8.4f} | "
                f"{err_str:>8} | "
                f"{fila['fa']:10.4f} | "
                f"{fila['fb']:10.4f} | "
                f"{fila['fx']:10.4f} | "
                f"{ea_flag:>6}"
            )
