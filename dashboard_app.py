"""
Dashboard Web para Análisis de Matrices de Mahjong
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import json
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Backend no interactivo para web
import seaborn as sns
import numpy as np

# Importar nuestros módulos de análisis
from config import CONFIG, SYMBOLS
from matrix_analyzer import MatrixAnalyzer
from matrix_comparator import MatrixComparator
from maps import generate_mahjong_heatmap

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mahjong-dashboard-secret-key'

class MahjongDashboard:
    """Clase principal del dashboard"""
    def __init__(self):
        self.matrix = None
        self.analyzers = []
        self.summaries = []
        self.matrices_data = []  # Inicializar como lista vacía
        self.load_data()
    
    def load_data(self):
        """Carga los datos de las matrices"""
        try:
            self.matrix = np.load(CONFIG['archivo_matriz'])
            self.analyze_matrices()
        except Exception as e:
            print(f"Error cargando datos: {e}")
    
    def analyze_matrices(self):
        """Analiza todas las matrices"""
        self.analyzers = []
        self.summaries = []
        
        for i in range(self.matrix.shape[0]):
            vector = self.matrix[i]
            analyzer = MatrixAnalyzer(vector, i)
            self.analyzers.append(analyzer)
            self.summaries.append(analyzer.get_summary())
        
        # Almacenar las matrices reformateadas como en test.py
        self.matrices_data = []
        for i in range(self.matrix.shape[0]):
            single_row = self.matrix[i]  # Obtener fila individual (510 elementos)
            single_matrix = single_row.reshape(15, 34)  # Reformatear a matriz 2D de 15x34
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

            # Leer la imagen generada y devolverla
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
        hand_data = dict(analyzer.parser.hand)
        hand_composition = {
            'total_tiles': sum(hand_data.values()),
            'unique_types': len(hand_data),
            'tiles_detail': [{'type': k, 'count': v} for k, v in sorted(hand_data.items())]
        }
        
        # Convertir los descartes al formato esperado por el frontend
        discards_by_player = []
        for player_discards in analyzer.parser.discards:
            discards_by_player.append(
                [{'type': discard[0], 'count': discard[1]} for discard in player_discards]
            )

        return {
            'index': matrix_index,
            'summary': summary,
            'metadata': analyzer.parser.metadata,
            'hand_composition': hand_composition,
            'discards_by_player': discards_by_player
        }
    
    def get_comparison_analysis(self):
        """Obtiene análisis comparativo entre matrices"""
        if len(self.summaries) < 2:
            return None
        
        comparator = MatrixComparator(self.summaries)
        
        # Generar datos de comparación
        comparison_data = {
            'progression': [],
            'same_player_comparisons': [],
            'discard_patterns': {}
        }
        
        # Progresión temporal
        for i, summary in enumerate(self.summaries):
            comparison_data['progression'].append({
                'matrix': i + 1,                'pov_player': summary['pov_player'],
                'step_number': summary['step_number'],
                'wall_tiles': summary['wall_tiles'],
                'total_discards': sum(len(discards) for discards in summary['discards_detail'].values())
            })
        
        # Comparaciones del mismo jugador
        for i in range(len(self.summaries) - 1):
            current = self.summaries[i]
            next_matrix = self.summaries[i + 1]
            
            if current['pov_player'] == next_matrix['pov_player']:
                comparison_data['same_player_comparisons'].append({
                    'from_matrix': i + 1,
                    'to_matrix': i + 2,
                    'player': current['pov_player'],
                    'hand_changes': self._analyze_hand_changes_data(current, next_matrix)
                })
        
        return comparison_data
    
    def _analyze_hand_changes_data(self, current, next_matrix):
        """Analiza cambios de mano entre matrices para datos JSON"""
        current_hand = dict(current['hand_detail'])
        next_hand = dict(next_matrix['hand_detail'])
        
        all_types = set(current_hand.keys()) | set(next_hand.keys())
        
        changes = {
            'lost': [],
            'gained': [],
            'modified': []
        }
        
        for tile_type in sorted(all_types):
            current_count = current_hand.get(tile_type, 0)
            next_count = next_hand.get(tile_type, 0)
            
            if current_count != next_count:
                if current_count > 0 and next_count == 0:
                    changes['lost'].append({'type': tile_type, 'count': current_count})
                elif current_count == 0 and next_count > 0:
                    changes['gained'].append({'type': tile_type, 'count': next_count})
                else:
                    changes['modified'].append({
                        'type': tile_type, 
                        'from': current_count, 
                        'to': next_count,
                        'diff': next_count - current_count
                    })
        
        return changes

# Instancia global del dashboard
dashboard = MahjongDashboard()

@app.route('/')
def index():
    """Página principal del dashboard"""
    return render_template('index.html')

@app.route('/api/matrices')
def api_matrices():
    """API: Lista de matrices disponibles"""
    matrices_info = []
    
    for i in range(len(dashboard.summaries)):
        summary = dashboard.summaries[i]
        matrices_info.append({
            'index': int(i),
            'matrix_number': int(i + 1),
            'pov_player': int(summary['pov_player']),
            'step_number': int(summary['step_number']),
            'wall_tiles': int(summary['wall_tiles']),
            'hand_size': int(summary['hand_tiles'])  # Convertir a int nativo
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
    
    return jsonify(comparison)

@app.route('/matrix/<int:matrix_id>')
def matrix_detail(matrix_id):
    """Página de detalle de una matriz"""
    if matrix_id >= len(dashboard.summaries):
        return "Matriz no encontrada", 404
    
    return render_template('matrix_detail.html', matrix_id=matrix_id)

@app.route('/comparison')
def comparison():
    """Página de comparación entre matrices"""
    return render_template('comparison.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
