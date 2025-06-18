# matrix_analyzer.py
"""
Análisis individual de matrices de Mahjong
"""

import numpy as np
from config import LABELS, SYMBOLS
from vector_parser import MahjongVectorParser, tiles_to_string

class MatrixAnalyzer:
    """Analizador para matrices individuales de Mahjong"""
    
    def __init__(self, vector, index):
        """
        Inicializa el analizador
        
        Args:
            vector: Vector de estado de Mahjong
            index: Índice de la matriz (para identificación)
        """
        self.parser = MahjongVectorParser(vector)
        self.index = index
    
    def print_full_analysis(self):
        """Imprime análisis completo de la matriz"""
        print(f"\n{'='*60}")
        print(f"ANÁLISIS DE LA MATRIZ {self.index + 1}")
        print(f"{'='*60}")
        
        self._print_metadata()
        self._print_control()
        self._print_dora()
        self._print_hand()
        self._print_discards()
        self._print_pond()
    
    def _print_metadata(self):
        """Imprime metadata del juego"""
        print(f"\n{SYMBOLS['SECCION']} SECCIÓN 1: {LABELS['SECCIONES'][1]}")
        print("-" * 40)
        
        meta = self.parser.metadata
        print(f"Round wind: {LABELS['VIENTOS'][meta['round_wind']]} ({meta['round_wind']})")
        print(f"Dealer (oya): Jugador {meta['dealer']}")
        print(f"POV player: Jugador {meta['pov_player']}")
        print(f"Honba sticks: {meta['honba_sticks']}")
        print(f"Riichi sticks: {meta['riichi_sticks']}")
        print(f"Fichas en muro: {meta['wall_tiles']}")
        
        print(f"\nPuntuaciones:")
        for i, score in enumerate(meta['scores']):
            print(f"  Jugador {i}: {score} puntos")
        
        print(f"\nEstado de Riichi:")
        riichi_labels = ["derecha", "frente", "izquierda"]
        for i, status in enumerate(meta['riichi_status']):
            print(f"  Jugador {riichi_labels[i]}: {'SÍ' if status else 'NO'}")
    
    def _print_control(self):
        """Imprime información de control técnico"""
        print(f"\n{SYMBOLS['SECCION']} SECCIÓN 2: {LABELS['SECCIONES'][2]}")
        print("-" * 40)
        
        control = self.parser.control
        print(f"Round number: {control['round_number']}")
        print(f"Step number: {control['step_number']}")
    
    def _print_dora(self):
        """Imprime información de dora"""
        print(f"\n{SYMBOLS['SECCION']} SECCIÓN 3: {LABELS['SECCIONES'][3]}")
        print("-" * 40)
        
        dora = self.parser.dora
        if dora['active_dora'] is not None:
            print(f"Indicador de dora en posición: {dora['active_dora']} (ficha tipo {dora['active_dora']})")
        else:
            print("No se encontró indicador de dora activo")
    
    def _print_hand(self):
        """Imprime información detallada de la mano"""
        print(f"\n{SYMBOLS['SECCION']} SECCIÓN 4: {LABELS['SECCIONES'][4]} (DETALLADO)")
        print("-" * 40)
        
        hand = self.parser.hand
        print(f"Total de fichas en mano: {hand['total_tiles']}")
        print(f"Tipos diferentes de fichas: {hand['unique_types']}")
        
        if hand['tiles']:
            print("Composición completa de la mano:")
            for tipo, cantidad in hand['tiles']:
                plural = "s" if cantidad > 1 else ""
                print(f"  Tipo {tipo:2d}: {cantidad} ficha{plural}")
        else:
            print("Sin fichas en mano")
    
    def _print_discards(self):
        """Imprime información detallada de descartes"""
        print(f"\n{SYMBOLS['SECCION']} SECCIÓN 6: {LABELS['SECCIONES'][6]} (DETALLADO)")
        print("-" * 40)
        
        for player_id, player_data in self.parser.discards.items():
            player_name = LABELS['JUGADORES'][player_id]
            print(f"\n{player_name}: {player_data['total']} fichas descartadas")
            
            if player_data['tiles']:
                for tipo, cantidad in player_data['tiles']:
                    plural = "s" if cantidad > 1 else ""
                    print(f"  Tipo {tipo:2d}: {cantidad} ficha{plural}")
            else:
                print("  Sin descartes")
    
    def _print_pond(self):
        """Imprime información del pond completo"""
        print(f"\n{SYMBOLS['SECCION']} SECCIÓN 7: {LABELS['SECCIONES'][7]}")
        print("-" * 40)
        
        for player_id, player_data in self.parser.pond.items():
            player_name = LABELS['JUGADORES'][player_id]
            print(f"{player_name}: {player_data['total']} fichas visibles en total")
    
    def get_summary(self):
        """Retorna resumen estructurado para comparaciones"""
        return self.parser.get_summary()
