# matrix_comparator.py
"""
Comparaciones entre matrices de Mahjong
"""

import pandas as pd
from config import LABELS, SYMBOLS
from vector_parser import tiles_to_string

class MatrixComparator:
    """Comparador para análisis entre matrices de Mahjong"""
    
    def __init__(self, summaries_list):
        """
        Inicializa el comparador
        
        Args:
            summaries_list: Lista de resúmenes de matrices
        """
        self.summaries = summaries_list
    
    def print_basic_comparison(self):
        """Imprime comparación básica entre todas las matrices"""
        print(f"\n{'='*60}")
        print("COMPARACIÓN ENTRE MATRICES")
        print(f"{'='*60}")
        
        # Crear DataFrame para comparación
        basic_data = []
        for summary in self.summaries:
            basic_data.append({
                'round_wind': summary['round_wind'],
                'dealer': summary['dealer'],
                'pov_player': summary['pov_player'],
                'hand_tiles': summary['hand_tiles'],
                'step_number': summary['step_number'],
                'wall_tiles': summary['wall_tiles']
            })
        
        df = pd.DataFrame(basic_data)
        df.index = [f"Matriz {i+1}" for i in range(len(basic_data))]
        
        print(f"\n{SYMBOLS['TABLA']} Tabla comparativa:")
        print(df.to_string())
        
        self._print_basic_differences(df)
    
    def _print_basic_differences(self, df):
        """Imprime diferencias básicas identificadas"""
        print(f"\n{SYMBOLS['ANALISIS']} Diferencias principales:")
        
        # Analizar vientos únicos
        vientos_unicos = df['round_wind'].unique()
        if len(vientos_unicos) > 1:
            print(f"- Diferentes vientos de ronda: {vientos_unicos}")
        
        # Analizar dealers únicos
        dealers_unicos = df['dealer'].unique()
        if len(dealers_unicos) > 1:
            print(f"- Diferentes dealers: {dealers_unicos}")
        
        # Analizar variación en fichas de mano
        min_fichas = df['hand_tiles'].min()
        max_fichas = df['hand_tiles'].max()
        if min_fichas != max_fichas:
            print(f"- Fichas en mano varían de {min_fichas} a {max_fichas}")
        
        # Mostrar progresión de steps y muro
        steps = df['step_number'].tolist()
        wall_tiles = df['wall_tiles'].tolist()
        print(f"- Progresión de steps: {steps}")
        print(f"- Fichas restantes en muro: {wall_tiles}")
    
    def print_sequential_comparison(self):
        """Imprime comparación secuencial entre matrices consecutivas"""
        print(f"\n{'='*80}")
        print("COMPARACIÓN SECUENCIAL: CAMBIOS ENTRE MATRICES CONSECUTIVAS")
        print(f"{'='*80}")
        
        for i in range(len(self.summaries) - 1):
            current = self.summaries[i]
            next_matrix = self.summaries[i + 1]
            
            print(f"\n{SYMBOLS['CAMBIO']} CAMBIOS DE MATRIZ {i+1} → MATRIZ {i+2}")
            print("-" * 60)
            
            self._analyze_metadata_changes(current, next_matrix)
            self._analyze_hand_changes(current, next_matrix, i+1, i+2)
            self._analyze_discard_changes(current, next_matrix)
            self._analyze_turn_pattern(current, next_matrix, i+1, i+2)
            
            print("-" * 60)
    
    def _analyze_metadata_changes(self, current, next_matrix):
        """Analiza cambios en metadata"""
        print(f"{SYMBOLS['TABLA']} CAMBIOS EN METADATA:")
        
        # POV Player
        if current['pov_player'] != next_matrix['pov_player']:
            print(f"   {SYMBOLS['POV']} POV Player: {current['pov_player']} → {next_matrix['pov_player']}")
        
        # Step number
        step_diff = next_matrix['step_number'] - current['step_number']
        print(f"   {SYMBOLS['TIEMPO']} Step: {current['step_number']} → {next_matrix['step_number']} (Δ: {step_diff:+d})")        
        # Wall tiles
        wall_diff = next_matrix['wall_tiles'] - current['wall_tiles']
        print(f"   {SYMBOLS['MURO']} Fichas muro: {current['wall_tiles']} → {next_matrix['wall_tiles']} (Δ: {wall_diff:+d})")
    
    def _analyze_hand_changes(self, current, next_matrix, current_num, next_num):
        """Analiza cambios en la mano POV solo cuando el jugador es el mismo"""
        
        # Solo analizar si es el mismo jugador
        if current['pov_player'] != next_matrix['pov_player']:
            return
        
        print(f"\n{SYMBOLS['MANO']} CAMBIOS EN MANO POV:")
        print(f"   👤 Mismo POV (Jugador {current['pov_player']}): Analizando evolución de mano...")
        
        # Convertir manos a diccionarios para facilitar comparación
        current_hand = dict(current['hand_detail'])
        next_hand = dict(next_matrix['hand_detail'])
        
        # Encontrar todos los tipos únicos
        all_types = set(current_hand.keys()) | set(next_hand.keys())
        
        changes_found = False
        lost_tiles = []
        gained_tiles = []
        modified_tiles = []
        
        for tile_type in sorted(all_types):
            current_count = current_hand.get(tile_type, 0)
            next_count = next_hand.get(tile_type, 0)
            
            if current_count != next_count:
                changes_found = True
                diff = next_count - current_count
                
                if current_count > 0 and next_count == 0:
                    lost_tiles.append(f"T{tile_type}({current_count})")
                elif current_count == 0 and next_count > 0:
                    gained_tiles.append(f"T{tile_type}({next_count})")
                else:
                    modified_tiles.append(f"T{tile_type}: {current_count}→{next_count} (Δ{diff:+d})")
        
        if not changes_found:
            print(f"   {SYMBOLS['EXITO']} Sin cambios en la mano POV (mismo jugador)")
        else:
            if lost_tiles:
                print(f"   {SYMBOLS['PERDIDA']} Fichas perdidas: {', '.join(lost_tiles)}")
            if gained_tiles:
                print(f"   {SYMBOLS['GANANCIA']} Fichas ganadas: {', '.join(gained_tiles)}")
            if modified_tiles:
                print(f"   {SYMBOLS['MODIFICACION']} Fichas modificadas: {', '.join(modified_tiles)}")
    
    def _analyze_discard_changes(self, current, next_matrix):
        """Analiza cambios en descartes"""
        print(f"\n{SYMBOLS['DESCARTE']} CAMBIOS EN DESCARTES:")
        
        global_changes = False
        
        for player_id in range(4):
            # Convertir descartes a diccionarios
            current_discards = dict(current['discards_detail'][player_id])
            next_discards = dict(next_matrix['discards_detail'][player_id])
            
            # Encontrar cambios
            all_types = set(current_discards.keys()) | set(next_discards.keys())
            player_changes = []
            
            for tile_type in sorted(all_types):
                current_count = current_discards.get(tile_type, 0)
                next_count = next_discards.get(tile_type, 0)
                
                if current_count != next_count:
                    global_changes = True
                    diff = next_count - current_count
                    if diff > 0:
                        player_changes.append(f"T{tile_type}(+{diff})")
                    else:
                        player_changes.append(f"T{tile_type}({diff})")
            
            if player_changes:
                player_name = LABELS['JUGADORES'][player_id]
                print(f"   👤 {player_name}: {', '.join(player_changes)}")
        
        if not global_changes:
            print(f"   {SYMBOLS['EXITO']} Sin cambios en descartes")
    
    def _analyze_turn_pattern(self, current, next_matrix, current_num, next_num):
        """Analiza el patrón específico del turno"""
        print(f"\n{SYMBOLS['TURNO']} ANÁLISIS DEL TURNO:")
        
        # Identificar qué jugador tuvo el turno
        previous_pov = current['pov_player']
        
        # Verificar si ese jugador descartó algo
        current_discards = dict(current['discards_detail'][previous_pov])
        next_discards = dict(next_matrix['discards_detail'][previous_pov])
        
        new_discards = []
        for tile_type in next_discards:
            current_count = current_discards.get(tile_type, 0)
            next_count = next_discards.get(tile_type, 0)
            if next_count > current_count:
                diff = next_count - current_count
                new_discards.append(f"T{tile_type}(+{diff})")
        
        if new_discards:
            print(f"   {SYMBOLS['POV']} Jugador {previous_pov} descartó: {', '.join(new_discards)}")
        else:
            print(f"   {SYMBOLS['POV']} Jugador {previous_pov} no descartó en este turno")
        
        # Cambio de turno
        if current['pov_player'] != next_matrix['pov_player']:
            print(f"   {SYMBOLS['CAMBIO']} Turno pasó: Jugador {current['pov_player']} → Jugador {next_matrix['pov_player']}")
    def print_consolidated_summary(self):
        """Genera un resumen consolidado de todos los cambios"""
        print(f"\n{'='*80}")
        print("RESUMEN CONSOLIDADO DE CAMBIOS")
        print(f"{'='*80}")
        
        self._print_temporal_progression()
        self._print_identified_patterns()
        self._print_most_discarded_types()
    
    def _print_temporal_progression(self):
        """Imprime progresión temporal"""
        print(f"\n{SYMBOLS['PATRON']} PROGRESIÓN TEMPORAL:")
        print("Matriz | POV | Step  | Muro | Nuevos Descartes")
        print("-" * 50)
        
        for i, summary in enumerate(self.summaries):
            # Contar total de descartes
            total_discards = sum(len(discards) for discards in summary['discards_detail'].values())
            
            print(f"   {i+1:2d}  |  {summary['pov_player']}  | {summary['step_number']:4d} | {summary['wall_tiles']:2d}   | {total_discards:2d}")
    
    def _print_identified_patterns(self):
        """Imprime patrones identificados"""
        print(f"\n{SYMBOLS['ANALISIS']} PATRONES IDENTIFICADOS:")
        
        # Patrón de rotación POV
        povs = [summary['pov_player'] for summary in self.summaries]
        print(f"   {SYMBOLS['POV']} Rotación POV: {' → '.join(map(str, povs))}")
    
    def _print_most_discarded_types(self):
        """Imprime tipos más descartados"""
        print(f"\n{SYMBOLS['TABLA']} TIPOS MÁS DESCARTADOS:")
        
        discard_counter = {}
        for summary in self.summaries:
            for player_discards in summary['discards_detail'].values():
                for tile_type, count in player_discards:
                    # Convertir a int estándar para evitar overflow
                    tile_type = int(tile_type)
                    count = int(count)
                    discard_counter[tile_type] = discard_counter.get(tile_type, 0) + count
        
        if discard_counter:
            frequent_types = sorted(discard_counter.items(), key=lambda x: x[1], reverse=True)[:5]
            for tile_type, total in frequent_types:
                print(f"   Tipo {tile_type:2d}: {total} veces descartado")
        else:
            print("   Sin descartes registrados")
