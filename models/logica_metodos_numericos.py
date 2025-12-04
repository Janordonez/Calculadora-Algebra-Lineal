"""
logica_metodos_numericos.py

Lógica de métodos numéricos:
- Evaluar funciones f(x) con parser avanzado (√, superíndices, sen, ln, etc.)
- Bisección
- Regla Falsa
- Newton-Raphson
- Secante
"""

import math
import re

# =============================================================================
# CONSTANTES PARA SUPERÍNDICES
# =============================================================================

SUP_DIGITS = "⁰¹²³⁴⁵⁶⁷⁸⁹"
SUP_SIGNS = "⁻⁺"
NORMAL_DIGITS = "0123456789"
NORMAL_SIGNS = "-+"
SUP_MAP = str.maketrans(SUP_DIGITS + SUP_SIGNS, NORMAL_DIGITS + NORMAL_SIGNS)
DIGIT_TO_SUP = str.maketrans(NORMAL_DIGITS + "-", SUP_DIGITS + "⁻")


# =============================================================================
# PARSER PARA SUPERÍNDICES
# =============================================================================

def _reemplazar_superindices(expr: str) -> str:
    """
    Convierte cosas como x², x³, a⁻¹ en x**(2), x**(3), a**(-1)
    """
    patt = r"(?P<base>(?:\d+|\w+|[\)\]])+)(?P<sup>[" + SUP_DIGITS + SUP_SIGNS + "]+)"

    def repl(m):
        base = m.group("base")
        sup = m.group("sup").translate(SUP_MAP)
        return f"{base}**({sup})"

    return re.sub(patt, repl, expr)


# =============================================================================
# NORMALIZADOR DE EXPRESIONES DEL USUARIO
# =============================================================================

def normalizar_expresion_usuario(expr: str) -> str:
    """
    Normaliza la expresión escrita por el usuario para poder evaluarla con eval().
    Soporta:
    - √x, √(x), ∛x, etc.
    - π, e
    - sen(x) -> sin(x)
    - ln(x)  -> log natural (se maneja en contexto, NO se reemplaza aquí)
    - log(x) -> log base 10 (y log(x,b) base b) vía función log en contexto
    - multiplicación implícita: 2x, 3(x+1), (x+1)(x-2)
    - superíndices: x², x³, x⁻¹, etc.
    - ^ como potencia
    """
    s = expr.strip()
    if not s:
        return s

    # Raíces y constantes
    s = s.replace("√", "sqrt").replace("∛", "cbrt")
    s = s.replace("π", "pi")
    # IMPORTANTE: YA NO se reemplaza 'e' aquí.
    # El símbolo 'e' se maneja en el contexto como la constante de Euler.

    # Superíndices tipo x², x⁻¹
    s = _reemplazar_superindices(s)

    # Potencia con ^
    s = s.replace("^", "**")

    # Multiplicación implícita:
    #  - número seguido de letra o paréntesis: 5x, 2(x+1) -> 5*x, 2*(x+1)
    s = re.sub(r'(\d)([a-zA-Z(])', r'\1*\2', s)
    #  - paréntesis seguido de letra/número/paréntesis: (x+1)x, (x+1)2, (x+1)(x-2)
    s = re.sub(r'(\))([a-zA-Z0-9(])', r'\1*\2', s)

    # Funciones específicas:
    # sen(x) -> sin(x)
    s = re.sub(r"\bsen\(", "sin(", s)

    # OJO: ln(x) y log(x) se dejan tal cual.
    #  - ln se mapeará a log natural en el contexto.
    #  - log será log base 10 o log base b según parámetros.

    return s


# =============================================================================
# CONTEXTO MATEMÁTICO SEGURO PARA eval()
# =============================================================================

def _log_personalizado(*args):
    """
    log(x)      -> base 10
    log(x, b)   -> base b
    """
    if len(args) == 1:
        x = args[0]
        return math.log10(x)
    elif len(args) == 2:
        x, base = args
        return math.log(x, base)
    else:
        raise TypeError("log() acepta 1 o 2 argumentos: log(x) o log(x, base)")


def contexto_matematico():
    """
    Contexto seguro con funciones matemáticas permitidas para eval().

    - ln(x)  -> log natural (base e)
    - log(x) -> log base 10
    - log(x, b) -> log base b
    """
    return {
        "x": 0.0,
        # Trigonométricas
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "asin": math.asin,
        "acos": math.acos,
        "atan": math.atan,

        # Logaritmos
        "ln": math.log,           # natural
        "log": _log_personalizado,
        "log10": math.log10,      # por si acaso

        # Otras funciones
        "exp": math.exp,
        "sqrt": math.sqrt,
        "abs": abs,

        # Constantes
        "pi": math.pi,
        "e": math.e,

        # Raíz cúbica con signo preservado
        "cbrt": lambda t: math.copysign(abs(t) ** (1 / 3), t),
    }


# =============================================================================
# EVALUACIÓN DE f(x)
# =============================================================================

def evaluar_funcion(expr: str, x: float) -> float:
    """
    Evalúa f(x) con el parser avanzado.
    Soporta trigonométricas, ln, log, raíces, superíndices, etc.
    """
    expr_norm = normalizar_expresion_usuario(expr)
    ctx = contexto_matematico()
    ctx["x"] = float(x)
    try:
        # __builtins__ vacío para evitar funciones peligrosas
        val = eval(expr_norm, {"__builtins__": {}}, ctx)
        return float(val)
    except Exception as e:
        raise ValueError(f"Error al evaluar la función en x = {x}: {e}")


# =============================================================================
# MÉTODO DE BISECCIÓN
# =============================================================================

def biseccion(expr: str, a: float, b: float, tol: float, max_iter: int = 100):
    """
    Método de Bisección.

    Parámetros:
        expr: cadena con la función f(x)
        a, b: extremos del intervalo [a,b]
        tol: tolerancia para el error relativo (NO en %, ej: 0.0001)
        max_iter: máximo de iteraciones

    Retorna:
        raiz_aprox: float
        historia: lista de dicts con:
            - iter, a, b, x, fa, fb, fx, error_pct, len_interval
        intervalo_final: (a_final, b_final)
        error_final: error relativo porcentual final
    """
    fa = evaluar_funcion(expr, a)  # evalúa f(a)
    fb = evaluar_funcion(expr, b)  # evalúa f(b)

    if fa * fb > 0:  # revisa que haya cambio de signo en los extremos
        raise ValueError("El intervalo no es válido: f(a) y f(b) tienen el mismo signo.")  # error si mismo signo

    historia = []  # inicializa la lista de historial
    x_old = None  # guarda la aproximación anterior
    error_final = None  # guardará el error final en %

    for i in range(1, max_iter + 1):  # ciclo principal de iteraciones
        x_mid = (a + b) / 2.0  # calcula el punto medio
        fx_mid = evaluar_funcion(expr, x_mid)  # evalúa f en el punto medio
        len_interval = abs(b - a)  # longitud del intervalo actual

        if x_old is None:  # sin aproximación anterior en la primera iteración
            error_rel = None  # no hay error relativo aún
        else:
            if x_mid != 0:  # evita división por cero al calcular error relativo
                error_rel = abs((x_mid - x_old) / x_mid)  # error relativo
            else:
                error_rel = abs(x_mid - x_old)  # error absoluto si x_mid == 0

        error_pct = None if error_rel is None else error_rel * 100.0  # error en porcentaje

        historia.append(  # añade registro de la iteración al historial
            {
                "iter": i,  # número de iteración
                "a": a,  # extremo izquierdo
                "b": b,  # extremo derecho
                "x": x_mid,  # aproximación actual (punto medio)
                "fa": fa,  # f(a)
                "fb": fb,  # f(b)
                "fx": fx_mid,  # f(x_mid)
                "error_pct": error_pct,  # error en %
                "len_interval": len_interval,  # tamaño del intervalo
            }
        )

        # Criterio de paro con tolerancia en término relativo (no en %)
        if error_rel is not None and error_rel < tol:  # verifica si se cumple la tolerancia
            error_final = error_pct  # guarda el error final
            break  # sale del bucle

        # Actualizar intervalo según el signo
        if fa * fx_mid < 0:  # la raíz está en [a, x_mid]
            b = x_mid  # actualiza extremo derecho
            fb = fx_mid  # actualiza f(b)
        else:
            a = x_mid  # actualiza extremo izquierdo
            fa = fx_mid  # actualiza f(a)

        x_old = x_mid  # actualiza la aproximación anterior

    raiz_aprox = x_mid  # aproximación final de la raíz
    if error_final is None:  # si no se alcanzó la tolerancia
        error_final = error_pct  # usa el último error calculado

    intervalo_final = (a, b)  # intervalo final que contiene la raíz
    return raiz_aprox, historia, intervalo_final, error_final  # retorna resultados


# =============================================================================
# MÉTODO DE REGLA FALSA
# =============================================================================

def regla_falsa(expr: str, a: float, b: float, tol: float, max_iter: int = 100):
    """
    Método de Regla Falsa (Falsa Posición).

    Parámetros:
        expr: cadena con f(x)
        a, b: extremos del intervalo [a,b]
        tol: tolerancia para error relativo (NO en %)
        max_iter: máx. iteraciones

    Retorna:
        raiz_aprox, historia, intervalo_final, error_final
    """
    fa = evaluar_funcion(expr, a)  # evalúa f(a)
    fb = evaluar_funcion(expr, b)  # evalúa f(b)

    if fa * fb > 0:  # verifica que haya cambio de signo en los extremos
        raise ValueError("El intervalo no es válido: f(a) y f(b) tienen el mismo signo.")  # error si mismo signo

    historia = []  # lista para guardar historial de iteraciones
    x_old = None  # aproximación anterior inicial nula
    error_final = None  # guardará el error final en %

    for i in range(1, max_iter + 1):  # bucle principal de iteraciones
        denom = (fb - fa)  # denominador de la fórmula de regla falsa
        if denom == 0:  # evita división por cero
            raise ZeroDivisionError("fb - fa = 0, no se puede continuar en Regla Falsa.")  # error crítico

        # Fórmula de Regla Falsa:
        # x_r = b - f(b)*(b - a)/(f(b) - f(a))
        x_r = b - fb * (b - a) / denom  # nueva aproximación por regla falsa
        f_xr = evaluar_funcion(expr, x_r)  # evalúa f en la nueva aproximación
        len_interval = abs(b - a)  # longitud actual del intervalo

        if x_old is None:  # sin aproximación anterior en la primera iteración
            error_rel = None  # no se puede calcular error relativo aún
        else:
            if x_r != 0:  # evita división por cero al calcular error relativo
                error_rel = abs((x_r - x_old) / x_r)  # error relativo
            else:
                error_rel = abs(x_r - x_old)  # usa error absoluto si x_r == 0

        error_pct = None if error_rel is None else error_rel * 100.0  # error en porcentaje
        ea_less_tol = False  # bandera si el error es menor que la tolerancia
        if error_rel is not None and error_rel < tol:  # verifica criterio de paro
            ea_less_tol = True  # marca que se alcanzó la tolerancia

        historia.append(  # añade registro de la iteración al historial
            {
                "iter": i,  # número de iteración
                "a": a,  # extremo izquierdo actual
                "b": b,  # extremo derecho actual
                "x": x_r,  # aproximación actual
                "fa": fa,  # f(a) actual
                "fb": fb,  # f(b) actual
                "fx": f_xr,  # f(x_r)
                "error_pct": error_pct,  # error en %
                "ea_less_tol": ea_less_tol,  # si cumple la tolerancia
                "len_interval": len_interval,  # tamaño del intervalo
            }
        )

        if ea_less_tol:  # si se alcanzó la tolerancia, se finaliza
            error_final = error_pct  # guarda el error final
            break  # sale del bucle

        # Actualizar intervalo según el signo
        if fa * f_xr < 0:  # la raíz está en [a, x_r]
            b = x_r  # actualiza extremo derecho
            fb = f_xr  # actualiza f(b)
        else:
            a = x_r  # actualiza extremo izquierdo
            fa = f_xr  # actualiza f(a)

        x_old = x_r  # actualiza la aproximación anterior

    raiz_aprox = x_r  # aproximación final de la raíz
    if error_final is None:  # si no se alcanzó la tolerancia
        error_final = error_pct  # usa el último error calculado

    intervalo_final = (a, b)  # intervalo final que contiene la raíz
    return raiz_aprox, historia, intervalo_final, error_final  # retorna resultados


# =============================================================================
# DERIVADA NUMÉRICA (PARA NEWTON-RAPHSON)
# =============================================================================

def derivada_numerica(expr: str, x: float, h: float = 1e-6) -> float:
    """
    f'(x) ≈ (f(x+h) - f(x-h)) / (2h), con h adaptativo.
    """
    h_aj = h * (1.0 + abs(x))
    try:
        f_mas = evaluar_funcion(expr, x + h_aj)
        f_menos = evaluar_funcion(expr, x - h_aj)
    except Exception as e:
        raise ValueError(f"Error al evaluar la función para la derivada en x={x}: {e}")
    return (f_mas - f_menos) / (2.0 * h_aj)


# =============================================================================
# MÉTODO DE NEWTON-RAPHSON (MÉTODO ABIERTO, SOLO x_i)
# =============================================================================

def newton_raphson(expr: str, x0: float, tol: float, max_iter: int = 100):
    """
    Método de Newton-Raphson (ABIERTO).

    Parámetros:
        expr   : f(x)
        x0     : punto inicial x_i
        tol    : tolerancia para error relativo (NO en %)
        max_iter : máximo de iteraciones

    Retorna:
        raiz_aprox : float
        historia   : lista de dicts:
            - iter, x, fx, dfx, error_pct
        error_final: error relativo porcentual final
    """
    historia = []

    try:
        x = float(x0)
    except Exception:
        raise ValueError("El punto inicial x0 no es válido.")

    try:
        fx = evaluar_funcion(expr, x)
    except Exception as e:
        raise ValueError(f"Error al evaluar f(x0): {e}")

    error_final = None

    for i in range(1, max_iter + 1):
        dfx = derivada_numerica(expr, x)

        if dfx == 0:
            raise ZeroDivisionError(
                f"Derivada nula en la iteración {i}. "
                f"No se puede continuar (división entre cero en Newton-Raphson)."
            )

        x_next = x - fx / dfx

        if math.isnan(x_next) or math.isinf(x_next) or abs(x_next) > 1e12:
            raise ValueError(
                "El método de Newton-Raphson parece divergir o producir valores "
                "numéricamente inestables."
            )

        fx_next = evaluar_funcion(expr, x_next)

        if x_next != 0:
            error_rel = abs((x_next - x) / x_next)
        else:
            error_rel = abs(x_next - x)

        error_pct = error_rel * 100.0

        historia.append(
            {
                "iter": i,
                "x": x_next,
                "fx": fx_next,
                "dfx": dfx,
                "error_pct": error_pct,
            }
        )

        if error_rel < tol:
            error_final = error_pct
            x = x_next
            fx = fx_next
            break

        x = x_next
        fx = fx_next

    raiz_aprox = x
    if error_final is None and historia:
        error_final = historia[-1]["error_pct"]

    return raiz_aprox, historia, error_final


# =============================================================================
# MÉTODO DE LA SECANTE (MÉTODO ABIERTO, x0 y x1)
# =============================================================================

def metodo_secante(expr: str, x0: float, x1: float, tol: float, max_iter: int = 100):
    """
    Método de la Secante (ABIERTO).

    Parámetros:
        expr   : f(x)
        x0, x1 : aproximaciones iniciales (no es intervalo que encierre raíz)
        tol    : tolerancia para error relativo (NO en %)
        max_iter : máximo de iteraciones

    Retorna:
        raiz_aprox : float
        historia   : lista de dicts:
            - iter, x_prev, x, fx_prev, fx, error_pct
        error_final: error relativo porcentual final
    """
    try:
        x_prev = float(x0)
        x = float(x1)
    except Exception:
        raise ValueError("Los valores iniciales x0 y x1 no son válidos.")

    if x_prev == x:
        raise ValueError("Para la Secante, x0 y x1 deben ser distintos.")

    try:
        f_prev = evaluar_funcion(expr, x_prev)
        f = evaluar_funcion(expr, x)
    except Exception as e:
        raise ValueError(f"Error al evaluar la función en los valores iniciales: {e}")

    if f == f_prev:
        raise ZeroDivisionError(
            "f(x0) y f(x1) son iguales; se produce división entre cero en la Secante."
        )

    historia = []
    error_final = None

    for i in range(1, max_iter + 1):
        denom = (f - f_prev)
        if denom == 0:
            raise ZeroDivisionError(
                f"División entre cero en la iteración {i}: f(x_n) - f(x_{i-1}) = 0."
            )

        x_next = x - f * (x - x_prev) / denom

        if math.isnan(x_next) or math.isinf(x_next) or abs(x_next) > 1e12:
            raise ValueError(
                "El método de la Secante parece divergir o producir valores "
                "numéricamente inestables."
            )

        f_next = evaluar_funcion(expr, x_next)

        if x_next != 0:
            error_rel = abs((x_next - x) / x_next)
        else:
            error_rel = abs(x_next - x)

        error_pct = error_rel * 100.0

        historia.append(
            {
                "iter": i,
                "x_prev": x_prev,
                "x": x_next,
                "fx_prev": f_prev,
                "fx": f_next,
                "error_pct": error_pct,
            }
        )

        if error_rel < tol:
            error_final = error_pct
            x = x_next
            f = f_next
            break

        x_prev, f_prev = x, f
        x, f = x_next, f_next

    raiz_aprox = x
    if error_final is None and historia:
        error_final = historia[-1]["error_pct"]

    return raiz_aprox, historia, error_final
