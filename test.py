import numpy as np
np.random.seed(seed=69)

import seaborn as sns

# How to import necessary code
from maps import generate_mahjong_heatmap

# Cargar la matriz modificada desde heatmap.py
try:
    mock_matrix = np.load('modified_matrix.npy')
    print(f"Matriz cargada desde heatmap.py con dimensiones: {mock_matrix.shape}")
except FileNotFoundError:
    print("No se encontró el archivo 'modified_matrix.npy'. Ejecuta heatmap.py primero.")
    # Matriz de respaldo en caso de que no exista el archivo
    mock_matrix = np.array([
        [   1,    1,    0,    0,    0,   41,   25,   38,   18,   20,    0,    0,    0,    0, -128, -128, -128, -128, -128, -128, -128, -128, -128, -128, -128, -128, -128, -128, -128, -128, -128, -128,    9,  -66],
        [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0],
        [   0,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1,    1,    0,    1,    0,    0,    1,    4,    1,    0,    0,    1,    2,    1,    0],
        [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0],
        [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    3,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0],
        [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0],
        [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    3,    0,    0,    0,    0,    0],
        [   0,    1,    0,    0,    0,    0,    0,    1,    0,    2,    0,    0,    0,    0,    0,    0,    1,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0],
        [   0,    0,    0,    1,    0,    1,    0,    1,    1,    0,    1,    0,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1],
        [   1,    0,    0,    0,    0,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    2,    0,    1,    1,    0],
        [   0,    0,    0,    0,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    1,    0,    2,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1,    0,    1,    1],
        [   0,    1,    0,    0,    0,    0,    0,    1,    0,    2,    0,    0,    1,    0,    0,    0,    1,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0],
        [   0,    0,    0,    1,    0,    1,    0,    1,    1,    0,    1,    0,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1,    0,    0,    0,    0,    1],
        [   1,    0,    0,    0,    0,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    2,    0,    1,    1,    0],
        [   0,    0,    0,    0,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    1,    0,    2,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1,    0,    1,    1]], 
        dtype=np.int8)

# Generar heatmaps para cada matriz individual
print(f"Matriz total cargada con dimensiones: {mock_matrix.shape}")
print(f"Total de matrices individuales: {mock_matrix.shape[0]}")

# Configurar cuántas matrices procesar (cambia este número según necesites)
num_matrices_to_process = 5  # Procesar solo las primeras 5 para prueba rápida
# Para procesar todas, usa: num_matrices_to_process = mock_matrix.shape[0]

print(f"Generando heatmaps para las primeras {num_matrices_to_process} matrices...")

for i in range(min(num_matrices_to_process, len(mock_matrix))):
    # Obtener la fila individual y reformatearla a matriz 2D (15x34)
    single_row = mock_matrix[i]  # Obtener fila individual (510 elementos)
    single_matrix = single_row.reshape(15, 34)  # Reformatear a matriz 2D de 15x34
    
    print(f"Procesando matriz {i+1}: forma {single_matrix.shape}")
    
    try:
        generate_mahjong_heatmap(
            input_matrix=single_matrix,
            title="",  # Título eliminado
            output_path=f"./resources/mahjong_board_{i+1}_black"
        )
        print(f"  ✓ Heatmap negro generado para matriz {i+1}")
    except Exception as e:
        print(f"  ✗ Error generando heatmap para matriz {i+1}: {e}")
    
    print(f"Matriz {i+1}/{min(num_matrices_to_process, len(mock_matrix))} completada")

print("¡Proceso completado!")
