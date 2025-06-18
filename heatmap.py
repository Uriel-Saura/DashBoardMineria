# Standard imports
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Needed for sparse matrix creation
from scipy.sparse import csr_matrix

file = '2019010100gm-00a9-0000-1f1a5f1f.npz'
npz = np.load(file)
mat1 = np.array(csr_matrix((npz['data'], npz['indices'], npz['indptr']), shape=npz['shape']).toarray())

# Verificar las dimensiones originales
print(f"Dimensiones originales de mat1: {mat1.shape}")

print(mat1[0])  

# Quitar el elemento 510 de cada matriz (fila)
# Esto elimina la columna en el índice 510 de todas las filas
if mat1.shape[1] > 510:
    mat1 = np.delete(mat1, 510, axis=1)
    print(f"Dimensiones después de eliminar elemento 510: {mat1.shape}")
else:
    print(f"No se puede eliminar el elemento 510. La matriz solo tiene {mat1.shape[1]} columnas.")

print(f"Primera fila después de la modificación: {mat1[0]}")

# Guardar la matriz modificada para usar en test.py
np.save('modified_matrix.npy', mat1)
print("Matriz modificada guardada en 'modified_matrix.npy'")