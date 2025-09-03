from matriz import ingresar_matriz_vector, gauss_elimination

def main():
	print("--- Resolución de sistemas por método de Gauss ---")
	try:
		matriz, vector = ingresar_matriz_vector()
		sol = gauss_elimination(matriz, vector)
		if sol is None:
			print("No existe una solución única para el sistema ingresado. Por favor revise los datos.")
		else:
			print("Solución:", sol)
	except ValueError as e:
		print(f"Error: {e}\nPor favor revise los datos ingresados e intente nuevamente.")

if __name__ == "__main__":
	main()
