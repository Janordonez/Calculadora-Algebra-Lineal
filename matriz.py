from fractions import Fraction
# Función para ingresar matriz y vector por consola estilo Excel
def ingresar_matriz_vector():
	while True:
		print("Ingrese el número de filas de la matriz (máximo 10):")
		try:
			filas = int(input())
		except ValueError:
			print("Por favor ingrese un número entero.")
			continue
		if filas < 1 or filas > 10:
			print("El número de filas debe ser entre 1 y 10.")
			continue
		print("Ingrese el número de columnas de la matriz (máximo 10):")
		try:
			columnas = int(input())
		except ValueError:
			print("Por favor ingrese un número entero.")
			continue
		if columnas < 1 or columnas > 10:
			print("El número de columnas debe ser entre 1 y 10.")
			continue
		print(f"La matriz será de {filas}x{columnas}. Ingrese cada valor individualmente.")
		matriz = []
		for i in range(filas):
			fila = []
			for j in range(columnas):
				while True:
					valor = input(f"A f{i+1},c{j+1}: ")
					if valor.strip() == "":
						print("No puede dejar el valor vacío. Intente de nuevo.")
						continue
					try:
						num = float(valor)
						if num < -500 or num > 500:
							print("El valor debe estar entre -500 y 500.")
							continue
						fila.append(Fraction(num).limit_denominator())
						break
					except ValueError:
						print(f"El valor '{valor}' no es válido. Ingrese un número.")
			matriz.append(fila)
		print("Ingrese los valores de los términos independientes, uno por uno:")
		vector = []
		for i in range(filas):
			while True:
				valor = input(f"b f{i+1}: ")
				if valor.strip() == "":
					print("No puede dejar el valor vacío. Intente de nuevo.")
					continue
				try:
					num = float(valor)
					if num < -500 or num > 500:
						print("El valor debe estar entre -500 y 500.")
						continue
					vector.append(Fraction(num).limit_denominator())
					break
				except ValueError:
					print(f"El valor '{valor}' no es válido. Ingrese un número.")
		print("\nMatriz ingresada:")
		def fraccion_str(frac):
			if frac.denominator == 1:
				return str(frac.numerator)
			return f"{frac.numerator}/{frac.denominator}"
		for fila in matriz:
			print(" | ".join(fraccion_str(v) for v in fila))
		print("Vector de términos independientes:")
		print(" | ".join(fraccion_str(v) for v in vector))
		confirm = input("¿Desea continuar con estos datos? (s/n): ").lower()
		if confirm == "s":
			break
		else:
			print("Reiniciando ingreso de datos...")
	return matriz, vector

# Método de Gauss para resolver sistemas de ecuaciones lineales

def gauss_elimination(matrix, vector):
	"""
	Resuelve el sistema de ecuaciones lineales Ax = b usando eliminación gaussiana.
	matrix: lista de listas (coeficientes)
	vector: lista (términos independientes)
	Retorna una lista con la solución x.
	"""
	filas = len(matrix)
	columnas = len(matrix[0]) if matrix else 0
	if any(len(row) != columnas for row in matrix):
		raise ValueError("Todas las filas deben tener el mismo número de columnas.")
	if len(vector) != filas:
		raise ValueError("El vector debe tener la misma cantidad de filas que la matriz.")
	if filas != columnas:
		print("Advertencia: El sistema no es cuadrado. Se intentará resolver, pero puede no tener solución única.")
	n = min(filas, columnas)
	aug = [row[:] + [vector[i]] for i, row in enumerate(matrix)]

	def mostrar_matriz(aug):
		def fraccion_str(frac):
			if isinstance(frac, Fraction):
				if frac.denominator == 1:
					return str(frac.numerator)
				return f"{frac.numerator}/{frac.denominator}"
			return str(frac)
		col_widths = [max(len(fraccion_str(fila[j])) for fila in aug) for j in range(len(aug[0]))]
		for fila in aug:
			fila_str = " | ".join(fraccion_str(v).rjust(col_widths[j]) for j, v in enumerate(fila))
			print(fila_str)
		print()

	def nombre_incognita(idx):
		subindices = "₁₂₃₄₅₆₇₈₉"
		return f"x{subindices[idx] if idx < len(subindices) else str(idx+1)}"

	# Validación de matriz singular y sistemas incompatibles
	for i in range(n):
		if all(abs(aug[i][j]) < 1e-12 for j in range(columnas)) and abs(aug[i][columnas]) > 1e-12:
			print(f"Fila {i+1} es incompatible: todos los coeficientes son cero pero el término independiente no lo es.")
			print("El sistema no tiene solución.")
			return None
		if all(abs(aug[i][j]) < 1e-12 for j in range(columnas)) and abs(aug[i][columnas]) < 1e-12:
			print(f"Fila {i+1} es redundante: todos los coeficientes y el término independiente son cero.")
			# Puede continuar, pero la fila no aporta información

	print("\n--- Eliminación hacia adelante ---")
	for i in range(n):
		max_row = max(range(i, filas), key=lambda r: abs(aug[r][i]))
		if abs(aug[max_row][i]) < 1e-12:
			print(f"No se puede continuar, pivote nulo en columna {i+1}. El sistema puede ser singular o tener infinitas soluciones.")
			return 'infinitas'  # No solución única
		if max_row != i:
			print(f"f{i+1} <--> f{max_row+1}")
			aug[i], aug[max_row] = aug[max_row], aug[i]
			mostrar_matriz(aug)
		pivot = aug[i][i]
		if abs(pivot - 1.0) > 1e-12:
			def fraccion_str(frac):
				if isinstance(frac, Fraction):
					if frac.denominator == 1:
						return str(frac.numerator)
					return f"{frac.numerator}/{frac.denominator}"
				return str(frac)
			print(f"f{i+1} --> (1/{fraccion_str(pivot)})*f{i+1}")
			aug[i] = [x / pivot for x in aug[i]]
			mostrar_matriz(aug)
		for j in range(i+1, filas):
			factor = aug[j][i]
			if abs(factor) > 1e-12:
				def fraccion_str(frac):
					if isinstance(frac, Fraction):
						if frac.denominator == 1:
							return str(frac.numerator)
						return f"{frac.numerator}/{frac.denominator}"
					return str(frac)
				print(f"f{j+1} --> f{j+1} + ({fraccion_str(-factor)})*f{i+1}")
				aug[j] = [aug[j][k] - factor * aug[i][k] for k in range(columnas+1)]
				mostrar_matriz(aug)

	# Sustitución hacia atrás con paso a paso
	x = [Fraction(0)] * columnas
	print("\n--- Sustitución hacia atrás ---")
	def fraccion_str(frac):
		if isinstance(frac, Fraction):
			if frac.denominator == 1:
				return str(frac.numerator)
			return f"{frac.numerator}/{frac.denominator}"
		return str(frac)
	for i in range(n-1, -1, -1):
		suma = sum(aug[i][j] * x[j] for j in range(i+1, columnas))
		x[i] = aug[i][columnas] - suma
		incog = nombre_incognita(i)
		sum_str = " + ".join(f"({fraccion_str(aug[i][j])}*{nombre_incognita(j)})" for j in range(i+1, columnas))
		print(f"{incog} = {fraccion_str(aug[i][columnas])} - [{sum_str if sum_str else '0'}] = {fraccion_str(x[i])}")

	# Resumen final
	print("\n--- Matriz final escalonada ---")
	mostrar_matriz(aug)
	print("--- Solución final ---")
	for i in range(n):
		print(f"{nombre_incognita(i)} = {fraccion_str(x[i])}")

	# Determinar tipo de solución
	# Ninguna solución: fila incompatible detectada antes
	if 'infinitas' in x:
		print("El sistema tiene infinitas soluciones o no tiene solución única.")
		return None
	# Verificar si hay filas redundantes (infinitas soluciones)
	filas_redundantes = 0
	for i in range(filas):
		if all(abs(aug[i][j]) < 1e-12 for j in range(columnas)) and abs(aug[i][columnas]) < 1e-12:
			filas_redundantes += 1
	if filas_redundantes > 0:
		print("El sistema tiene infinitas soluciones.")
		return x[:filas] if filas <= columnas else x
	# Si pivotes no nulos y no hay incompatibilidad
	if filas == columnas:
		print("El sistema tiene una única solución.")
	else:
		print("El sistema puede tener varias soluciones.")
	return x[:filas] if filas <= columnas else x

if __name__ == "__main__":
	print("--- Resolución de sistemas por método de Gauss ---")
	matriz, vector = ingresar_matriz_vector()
	sol = gauss_elimination(matriz, vector)
	print("Solución:", sol)
