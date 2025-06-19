# vector_parser.py
"""
Utilidades para parsear vectores de estado de Mahjong
"""

import numpy as np
from config import INDICES, LABELS, SYMBOLS

class MahjongVectorParser:
    """Clase para parsear vectores de estado de Mahjong"""
    
    def __init__(self, vector):
        """
        Inicializa el parser con un vector de estado
        
        Args:
            vector: Array numpy de 510 elementos representando el estado
        """
        self.vector = vector
        self.metadata = self._parse_metadata()
        self.control = self._parse_control()
        self.dora = self._parse_dora()
        self.hand = self._parse_hand()
        self.melds = self._parse_melds()
        self.discards = self._parse_discards()
        self.pond = self._parse_pond()
    
    def _parse_metadata(self):
        """Parsea la sección de metadata"""
        return {
            'round_wind': self.vector[INDICES['ROUND_WIND']],
            'dealer': self.vector[INDICES['DEALER']],
            'pov_player': self.vector[INDICES['POV_PLAYER']],
            'honba_sticks': self.vector[INDICES['HONBA_STICKS']],
            'riichi_sticks': self.vector[INDICES['RIICHI_STICKS']],
            'wall_tiles': self.vector[INDICES['WALL_TILES']],
            'scores': [self.vector[INDICES['SCORES_START'] + i] for i in range(4)],
            'riichi_status': [
                self.vector[INDICES['RIICHI_STATUS_START'] + i] for i in range(3)
            ]
        }
    
    def _parse_control(self):
        """Parsea la sección de control técnico"""
        return {
            'round_number': self.vector[INDICES['ROUND_NUMBER']],
            'step_number': self.vector[INDICES['STEP_NUMBER']]
        }
    
    def _parse_dora(self):
        """Parsea la sección de indicadores de dora"""
        dora_section = self.vector[INDICES['DORA_START']:INDICES['DORA_END']+1]
        dora_indices = np.where(dora_section == 1)[0]
        return {
            'active_dora': dora_indices[0] if len(dora_indices) > 0 else None,
            'all_dora': dora_indices.tolist()
        }
    
    def _parse_hand(self):
        """Parsea la mano del POV player"""
        hand_section = self.vector[INDICES['HAND_START']:INDICES['HAND_END']+1]
        hand_tiles = [(i, count) for i, count in enumerate(hand_section) if count > 0]
        return {
            'tiles': hand_tiles,
            'total_tiles': np.sum(hand_section),
            'unique_types': len(hand_tiles)
        }
    
    def _parse_melds(self):
        """Parsea los melds de todos los jugadores"""
        melds = {}
        for player in range(4):
            start_idx = INDICES['MELDS_START'] + player * INDICES['MELDS_SIZE']
            end_idx = start_idx + INDICES['MELDS_SIZE']
            player_melds = self.vector[start_idx:end_idx]
            melds[player] = {
                'tiles': [(i, count) for i, count in enumerate(player_melds) if count > 0],
                'total': np.sum(player_melds)
            }
        return melds
    
    def _parse_discards(self):
        """Parsea los descartes de todos los jugadores"""
        discards = {}
        for player in range(4):
            start_idx = INDICES['DISCARDS_START'] + player * INDICES['DISCARDS_SIZE']
            end_idx = start_idx + INDICES['DISCARDS_SIZE']
            player_discards = self.vector[start_idx:end_idx]
            discards[player] = {
                'tiles': [(i, count) for i, count in enumerate(player_discards) if count > 0],
                'total': np.sum(player_discards)
            }
        return discards
    
    def _parse_pond(self):
        """Parsea el pond completo de todos los jugadores"""
        pond = {}
        for player in range(4):
            start_idx = INDICES['POND_START'] + player * INDICES['POND_SIZE']
            end_idx = start_idx + INDICES['POND_SIZE']
            player_pond = self.vector[start_idx:end_idx]
            pond[player] = {
                'tiles': [(i, count) for i, count in enumerate(player_pond) if count > 0],
                'total': np.sum(player_pond)
            }
        return pond
    
    def get_summary(self):
        """Retorna un resumen del estado parseado"""
        return {
            'round_wind': self.metadata['round_wind'],
            'dealer': self.metadata['dealer'],
            'pov_player': self.metadata['pov_player'],
            'step_number': self.control['step_number'],
            'wall_tiles': self.metadata['wall_tiles'],
            'hand_tiles': self.hand['total_tiles'],
            'hand_detail': self.hand['tiles'],
            'discards_detail': {i: data['tiles'] for i, data in self.discards.items()},
            'pond_detail': {i: data['tiles'] for i, data in self.pond.items()},
            'melds_detail': {i: data['tiles'] for i, data in self.melds.items()}
        }

def tiles_to_string(tiles_list, max_show=None):
    """
    Convierte una lista de (tipo, cantidad) a string legible
    
    Args:
        tiles_list: Lista de tuplas (tipo, cantidad)
        max_show: Máximo número de tipos a mostrar
    
    Returns:
        String formateado
    """
    if not tiles_list:
        return "Sin fichas"
    
    if max_show and len(tiles_list) > max_show:
        shown = tiles_list[:max_show]
        hidden = len(tiles_list) - max_show
        tiles_str = ", ".join([f"T{tipo}({cant})" for tipo, cant in shown])
        return f"{tiles_str} ... y {hidden} tipos más"
    else:
        return ", ".join([f"T{tipo}({cant})" for tipo, cant in tiles_list])
