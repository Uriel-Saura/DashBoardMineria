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
        
        # Mapeo de números de fichas a nombres descriptivos
        self.tile_names = {
            # Man (Caracteres)
            0: "1-man", 1: "2-man", 2: "3-man", 3: "4-man", 4: "5-man", 
            5: "6-man", 6: "7-man", 7: "8-man", 8: "9-man",
            # Pin (Círculos) 
            9: "1-pin", 10: "2-pin", 11: "3-pin", 12: "4-pin", 13: "5-pin",
            14: "6-pin", 15: "7-pin", 16: "8-pin", 17: "9-pin",
            # Sou (Bambús)
            18: "1-sou", 19: "2-sou", 20: "3-sou", 21: "4-sou", 22: "5-sou",
            23: "6-sou", 24: "7-sou", 25: "8-sou", 26: "9-sou",
            # Vientos y Dragones
            27: "Este", 28: "Sur", 29: "Oeste", 30: "Norte",
            31: "Blanco", 32: "Verde", 33: "Rojo"
        }
    
    def _get_tile_name(self, tile_number):
        """Obtiene el nombre descriptivo de una ficha"""
        return self.tile_names.get(tile_number, f"T{tile_number}")
    
    def _is_sequence_possible(self, tile_list):
        """Verifica si un conjunto de fichas puede formar una secuencia (CHII)"""
        # Solo se pueden formar secuencias con fichas numeradas (man, pin, sou)
        # Vientos y dragones no pueden formar secuencias
        numeric_tiles = []
        for tile_type, count in tile_list:
            if tile_type < 27:  # Solo fichas numeradas (0-26)
                numeric_tiles.extend([tile_type] * count)
        
        if len(numeric_tiles) < 3:
            return False
            
        # Verificar si hay secuencias consecutivas del mismo palo
        numeric_tiles.sort()
        sequences = []
        
        i = 0
        while i < len(numeric_tiles) - 2:
            # Verificar secuencia de 3 fichas consecutivas del mismo palo
            if (numeric_tiles[i+1] == numeric_tiles[i] + 1 and 
                numeric_tiles[i+2] == numeric_tiles[i] + 2 and
                numeric_tiles[i] // 9 == numeric_tiles[i+1] // 9 == numeric_tiles[i+2] // 9):
                sequences.append((numeric_tiles[i], numeric_tiles[i+1], numeric_tiles[i+2]))
                i += 3
            else:
                i += 1
                
        return len(sequences) > 0

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
            matrix_data = self.matrices_data[matrix_index]            # Generar heatmap usando la función simplificada de maps.py
            output_path = f"./resources/mahjong_board_{matrix_index + 1}_{color}"
            generate_mahjong_heatmap(
                input_matrix=matrix_data,
                title="",  # Título eliminado
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
    
    def get_general_statistics(self):
        """Obtiene estadísticas generales de todas las matrices"""
        if not self.summaries:
            return None
        
        # Contadores para estadísticas
        discarded_tiles = {}
        pon_melds = {}
        chii_melds = {}
        kan_melds = {}
        total_games = len(self.summaries)
        
        try:            # Procesar cada matriz para recopilar estadísticas
            for matrix_idx, analyzer in enumerate(self.analyzers):                # Contar descartes por tipo de ficha
                try:
                    for player_id in range(4):
                        player_discards = analyzer.parser.discards[player_id]
                        for tile_type, count in player_discards['tiles']:
                            # Solo contar valores positivos
                            if count > 0:
                                tile_name = self._get_tile_name(tile_type)
                                # Convertir 'count' a int de Python para prevenir overflow
                                discarded_tiles[tile_name] = discarded_tiles.get(tile_name, 0) + int(count)
                except (KeyError, IndexError, TypeError) as e:
                    continue# Contar melds por tipo
                try:
                    for player_id in range(4):
                        player_melds_data = analyzer.parser.melds.get(player_id, {'tiles': []})
                          # Analizar todos los melds del jugador para clasificarlos correctamente
                        all_tiles = player_melds_data['tiles']
                        
                        for tile_type, count in all_tiles:
                            tile_name = self._get_tile_name(tile_type)
                            
                            if count == 4:
                                # KAN: 4 fichas iguales
                                meld_key = f"KAN de {tile_name}"
                                if meld_key not in kan_melds:
                                    kan_melds[meld_key] = {'count': 0, 'matrices': []}
                                kan_melds[meld_key]['count'] += 1
                                kan_melds[meld_key]['matrices'].append(matrix_idx + 1)
                            elif count == 3:
                                # PON: 3 fichas iguales
                                meld_key = f"PON de {tile_name}"
                                if meld_key not in pon_melds:
                                    pon_melds[meld_key] = {'count': 0, 'matrices': []}
                                pon_melds[meld_key]['count'] += 1
                                pon_melds[meld_key]['matrices'].append(matrix_idx + 1)
                            elif count == 1:
                                # Fichas individuales - podrían ser parte de CHII
                                meld_key = f"Ficha {tile_name} en meld"
                                if meld_key not in chii_melds:
                                    chii_melds[meld_key] = {'count': 0, 'matrices': []}
                                chii_melds[meld_key]['count'] += 1
                                chii_melds[meld_key]['matrices'].append(matrix_idx + 1)
                            elif count == 2:
                                # Par - no es un meld completo en Mahjong estándar, pero podría ser útil
                                meld_key = f"Par de {tile_name}"
                                if meld_key not in pon_melds:
                                    pon_melds[meld_key] = {'count': 0, 'matrices': []}
                                pon_melds[meld_key]['count'] += 1
                                pon_melds[meld_key]['matrices'].append(matrix_idx + 1)
                            else:                                # Cualquier otra cantidad inusual
                                meld_key = f"{count}x {tile_name}"
                                if meld_key not in pon_melds:
                                    pon_melds[meld_key] = {'count': 0, 'matrices': []}
                                pon_melds[meld_key]['count'] += 1
                                pon_melds[meld_key]['matrices'].append(matrix_idx + 1)
                except (KeyError, IndexError, TypeError) as e:
                    continue
            
            # Ordenar y obtener los más comunes
            most_discarded = sorted(discarded_tiles.items(), key=lambda x: x[1], reverse=True)[:10]
            most_common_pon = sorted(pon_melds.items(), key=lambda x: x[1]['count'], reverse=True)[:5]
            most_common_chii = sorted(chii_melds.items(), key=lambda x: x[1]['count'], reverse=True)[:5]
            most_common_kan = sorted(kan_melds.items(), key=lambda x: x[1]['count'], reverse=True)[:5]            # Calcular promedios
            total_discards = sum(discarded_tiles.values())
            total_melds = sum(data['count'] for data in pon_melds.values()) + sum(data['count'] for data in chii_melds.values()) + sum(data['count'] for data in kan_melds.values())
            
            # Asegurar que los valores sean válidos
            total_discards = max(0, total_discards)
            total_melds = max(0, total_melds)
            
            return {
                'total_games': total_games,
                'total_discards': total_discards,
                'total_melds': total_melds,
                'average_discards_per_game': round(total_discards / total_games, 2) if total_games > 0 else 0,
                'average_melds_per_game': round(total_melds / total_games, 2) if total_games > 0 else 0,
                'most_discarded_tiles': [{'tile': tile, 'count': count, 'percentage': round((count/total_discards)*100, 2) if total_discards > 0 else 0} for tile, count in most_discarded],
                'most_common_pon': [{'meld': meld, 'count': data['count'], 'matrices': data['matrices'][:5]} for meld, data in most_common_pon],
                'most_common_chii': [{'meld': meld, 'count': data['count'], 'matrices': data['matrices'][:5]} for meld, data in most_common_chii],
                'most_common_kan': [{'meld': meld, 'count': data['count'], 'matrices': data['matrices'][:5]} for meld, data in most_common_kan],
                'meld_distribution': {
                    'pon': sum(data['count'] for data in pon_melds.values()),
                    'chii': sum(data['count'] for data in chii_melds.values()),
                    'kan': sum(data['count'] for data in kan_melds.values())
                }
            }
        except Exception as e:
            print(f"Error calculando estadísticas generales: {e}")
            return {
                'total_games': total_games,
                'total_discards': 0,
                'total_melds': 0,
                'average_discards_per_game': 0,
                'average_melds_per_game': 0,
                'most_discarded_tiles': [],
                'most_common_pon': [],
                'most_common_chii': [],
                'most_common_kan': [],
                'meld_distribution': {'pon': 0, 'chii': 0, 'kan': 0}
            }
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

@app.route('/api/statistics')
def api_statistics():
    """API: Estadísticas generales del dataset actual"""
    if not dashboard.summaries:
        return jsonify({'error': 'No hay datos cargados'}), 400
    
    statistics = dashboard.get_general_statistics()
    if statistics is None:
        return jsonify({'error': 'Error calculando estadísticas'}), 500
    
    statistics_clean = _convert_np(statistics)
    return jsonify(statistics_clean)

@app.route('/statistics')
def statistics_page():
    """Página de estadísticas generales"""
    if not dashboard.summaries:
        return redirect(url_for('index'))
    
    return render_template('statistics.html')

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
