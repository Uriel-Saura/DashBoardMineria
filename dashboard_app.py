"""
Dashboard Web para Análisis de Matrices de Mahjong
"""

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
import os
import json
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Backend no interactivo para web
import seaborn as sns
import numpy as np
from scipy.sparse import csr_matrix

# Importar nuestros módulos de análisis
from config import CONFIG, SYMBOLS
from matrix_analyzer import MatrixAnalyzer
from matrix_comparator import MatrixComparator
from maps import generate_mahjong_heatmap

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mahjong-dashboard-secret-key'
app.config['DATA_FOLDER'] = CONFIG['data_folder']

class MahjongDashboard:
    """Clase principal del dashboard"""
    def __init__(self):
        self.matrix_file = None
        self.matrix = None
        self.analyzers = []
        self.summaries = []
        self.matrices_data = []
    
    def load_data(self, filename):
        """Carga y procesa los datos de un archivo de matriz .npz"""
        filepath = os.path.join(app.config['DATA_FOLDER'], filename)
        if not os.path.exists(filepath):
            print(f"Error: El archivo {filename} no existe.")
            return False
        
        try:
            self.matrix_file = filename
            
            # Cargar el archivo .npz que contiene la matriz dispersa
            with np.load(filepath) as npz:
                # Reconstruir la matriz densa desde el formato disperso CSR
                matrix = csr_matrix((npz['data'], npz['indices'], npz['indptr']), shape=npz['shape']).toarray()

            # Quitar el elemento 510 de cada matriz (fila) si existe
            if matrix.shape[1] > 510:
                matrix = np.delete(matrix, 510, axis=1)
            
            self.matrix = matrix
            self.analyze_matrices()
            return True
        except Exception as e:
            print(f"Error cargando y procesando datos de {filename}: {e}")
            self.matrix_file = None
            self.matrix = None
            return False
    
    def analyze_matrices(self):
        """Analiza todas las matrices del archivo cargado"""
        self.analyzers = []
        self.summaries = []
        self.matrices_data = []

        if self.matrix is None:
            return

        for i in range(self.matrix.shape[0]):
            vector = self.matrix[i]
            analyzer = MatrixAnalyzer(vector, i)
            self.analyzers.append(analyzer)
            self.summaries.append(analyzer.get_summary())
        
        for i in range(self.matrix.shape[0]):
            single_row = self.matrix[i]
            single_matrix = single_row.reshape(15, 34)
            self.matrices_data.append(single_matrix)

    def generate_heatmap_image(self, matrix_index, color="black"):
        """Genera imagen del heatmap para una matriz específica"""
        try:
            # Asegurarse de que el índice de la matriz es válido
            if matrix_index < 0 or matrix_index >= len(self.matrices_data):
                return None

            # Obtener la matriz específica
            matrix_data = self.matrices_data[matrix_index]

            # Generar heatmap usando la función de maps.py
            output_path = f"./resources/mahjong_board_{matrix_index + 1}_{color}"
            generate_mahjong_heatmap(
                input_matrix=matrix_data,
                title=f"Mahjong Board {matrix_index + 1} w/ {color} border",
                border_color=color,
                colormap="kaggle_mahjong",
                output_path=output_path,
                show_fig=False
            )

            # Leer la imagen generada e devolverla
            with open(f"{output_path}.png", "rb") as f:
                img_data = base64.b64encode(f.read()).decode('utf-8')
            
            return img_data

        except Exception as e:
            print(f"Error generando heatmap: {e}")
            return None
    
    def get_matrix_analysis(self, matrix_index):
        """Obtiene análisis detallado de una matriz"""
        if matrix_index >= len(self.analyzers):
            return None
        
        analyzer = self.analyzers[matrix_index]
        summary = self.summaries[matrix_index]
        
        # Convertir la composición de la mano al formato esperado por el frontend
        parsed_hand = analyzer.parser.hand
        hand_composition = {
            'total_tiles': parsed_hand['total_tiles'],
            'unique_types': parsed_hand['unique_types'],
            'tiles_detail': [{'type': k, 'count': v} for k, v in sorted(parsed_hand['tiles'])]
        }        # Convertir los melds al formato esperado por el frontend
        melds_by_player = []
        try:
            for i in range(4):
                player_melds_data = analyzer.parser.melds.get(i, {'tiles': []})
                melds_by_player.append(
                    [{'type': meld_type, 'count': count} for meld_type, count in player_melds_data['tiles']]
                )
        except Exception as e:
            print(f"Error procesando melds: {e}")
            # Fallback: crear estructura vacía
            melds_by_player = [[] for _ in range(4)]
        
        # Convertir los descartes al formato esperado por el frontend
        discards_by_player = []
        # itera de 0 a 3 para asegurar el orden de los jugadores
        for i in range(4):
            player_discards_data = analyzer.parser.discards[i]
            discards_by_player.append(
                [{'type': discard_type, 'count': count} for discard_type, count in player_discards_data['tiles']]
            )

        return {
            'index': matrix_index,
            'summary': summary,
            'metadata': analyzer.parser.metadata,
            'hand_composition': hand_composition,
            'melds_by_player': melds_by_player,
            'discards_by_player': discards_by_player
        }
    
    def get_comparison_analysis(self):
        """Obtiene análisis comparativo entre matrices"""
        if len(self.summaries) < 2:
            return None
        
        # Generar datos de comparación
        comparison_data = {
            'progression': [],
            'meld_changes': []
        }
        
        # Progresión temporal
        for i, summary in enumerate(self.summaries):
            comparison_data['progression'].append({
                'matrix': i + 1,                'pov_player': summary['pov_player'],
                'step_number': summary['step_number'],
                'wall_tiles': summary['wall_tiles'],
                'total_discards': sum(len(discards) for discards in summary['discards_detail'].values())
            })
        
        # Comparaciones de melds
        for i in range(len(self.summaries) - 1):
            current = self.summaries[i]
            next_matrix = self.summaries[i + 1]
            
            for player_id in range(4):
                current_melds = dict(current['melds_detail'].get(player_id, []))
                next_melds = dict(next_matrix['melds_detail'].get(player_id, []))

                if current_melds != next_melds:
                    newly_formed_melds = []
                    for tile_type, count in next_melds.items():
                        if count > current_melds.get(tile_type, 0):
                            newly_formed_melds.append({
                                'type': tile_type,
                                'count': count - current_melds.get(tile_type, 0)
                            })
                    
                    if newly_formed_melds:
                        comparison_data['meld_changes'].append({
                            'from_matrix': i + 1,
                            'to_matrix': i + 2,
                            'player': player_id,
                            'new_melds': newly_formed_melds
                        })
        
        return comparison_data

# Instancia global del dashboard
dashboard = MahjongDashboard()

@app.route('/')
def index():
    """Página principal del dashboard"""
    return render_template('index.html')

@app.route('/api/datasets')
def api_datasets():
    """API: Lista de datasets NPZ disponibles en la carpeta de datos."""
    try:
        files = [f for f in os.listdir(app.config['DATA_FOLDER']) 
                 if f.endswith('.npz')]
        return jsonify(sorted(files))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/matrices')
def api_matrices():
    """API: Lista de matrices disponibles para un dataset"""
    dataset_name = request.args.get('dataset')
    if not dataset_name:
        return jsonify({'error': 'Dataset no especificado'}), 400

    # Cargar datos si no es el actual o si no hay ninguno cargado
    if dashboard.matrix_file != dataset_name:
        if not dashboard.load_data(dataset_name):
            return jsonify({'error': f'No se pudo cargar el dataset {dataset_name}'}), 500

    matrices_info = []
    for i in range(len(dashboard.summaries)):
        summary = dashboard.summaries[i]
        matrices_info.append({
            'index': int(i),
            'matrix_number': int(i + 1),
            'pov_player': int(summary['pov_player']),
            'step_number': int(summary['step_number']),
            'wall_tiles': int(summary['wall_tiles']),
            'hand_size': int(summary['hand_tiles'])
        })
    
    return jsonify(matrices_info)

# Función auxiliar para convertir tipos de NumPy a nativos de Python

def _convert_np(obj):
    if isinstance(obj, dict):
        return {str(k): _convert_np(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_convert_np(v) for v in obj]
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj

@app.route('/api/matrix/<int:matrix_id>')
def api_matrix_detail(matrix_id):
    """API: Detalle de una matriz específica"""
    analysis = dashboard.get_matrix_analysis(matrix_id)
    if analysis is None:
        return jsonify({'error': 'Matriz no encontrada'}), 404
    
    # Convertir objetos de NumPy a tipos nativos para serialización JSON
    analysis_clean = _convert_np(analysis)
    return jsonify(analysis_clean)

@app.route('/api/heatmap/<int:matrix_id>')
def api_heatmap(matrix_id):
    """API: Imagen del heatmap de una matriz"""
    color = request.args.get('color', 'black')
    img_data = dashboard.generate_heatmap_image(matrix_id, color)
    
    if img_data is None:
        return jsonify({'error': 'Error generando heatmap'}), 500
    
    return jsonify({'image': img_data})

@app.route('/api/comparison')
def api_comparison():
    """API: Análisis comparativo entre matrices"""
    comparison = dashboard.get_comparison_analysis()
    if comparison is None:
        return jsonify({'error': 'No hay suficientes datos para comparación'}), 400
    
    comparison_clean = _convert_np(comparison)
    return jsonify(comparison_clean)

@app.route('/matrix/<int:matrix_id>')
def matrix_detail(matrix_id):
    """Página de detalle de una matriz"""
    if matrix_id >= len(dashboard.summaries):
        return "Matriz no encontrada", 404
    
    return render_template('matrix_detail.html', matrix_id=matrix_id)

# @app.route('/comparison')
# def comparison():
#     """Página de comparación entre matrices"""
#     return render_template('comparison.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
