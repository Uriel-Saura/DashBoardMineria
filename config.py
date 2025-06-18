# config.py
"""
Configuración y constantes para el análisis de vectores de Mahjong
"""

# Configuración de análisis
CONFIG = {
    'num_matrices_analizar': 100,
    'archivo_matriz': 'modified_matrix.npy',
    'mostrar_debug': True,
    'max_tipos_mostrar': 10
}

# Constantes del vector de Mahjong
INDICES = {
    'METADATA_START': 0,
    'METADATA_END': 13,
    'ROUND_WIND': 0,
    'DEALER': 1,
    'POV_PLAYER': 2,
    'HONBA_STICKS': 3,
    'RIICHI_STICKS': 4,
    'WALL_TILES': 5,
    'SCORES_START': 6,
    'SCORES_END': 9,
    'RIICHI_STATUS_START': 11,
    'RIICHI_STATUS_END': 13,
    
    'PADDING_START': 14,
    'PADDING_END': 31,
    'ROUND_NUMBER': 32,
    'STEP_NUMBER': 33,
    
    'DORA_START': 34,
    'DORA_END': 67,
    
    'HAND_START': 68,
    'HAND_END': 101,
    
    'MELDS_START': 102,
    'MELDS_END': 237,
    'MELDS_SIZE': 34,
    
    'DISCARDS_START': 238,
    'DISCARDS_END': 373,
    'DISCARDS_SIZE': 34,
    
    'POND_START': 374,
    'POND_END': 509,
    'POND_SIZE': 34
}

# Nombres y etiquetas
LABELS = {
    'VIENTOS': ["Este", "Sur", "Oeste", "Norte"],
    'JUGADORES': ["POV player", "Derecha", "Frente", "Izquierda"],
    'SECCIONES': {
        1: "Metadata general del juego",
        2: "Control técnico", 
        3: "Indicador de Dora",
        4: "Mano del POV player",
        5: "Melds por jugador",
        6: "Descartes por jugador",
        7: "Pond completo"
    }
}

# Símbolos para output
SYMBOLS = {
    'SECCION': '🔹',
    'POV': '🎯',
    'MANO': '🃏',
    'DESCARTE': '🗑️',
    'CAMBIO': '🔄',
    'TIEMPO': '⏱️',
    'MURO': '🧱',
    'PERDIDA': '➖',
    'GANANCIA': '➕',
    'MODIFICACION': '🔄',
    'TURNO': '🎲',
    'ANALISIS': '🔍',
    'EXITO': '✅',
    'ALERTA': '⚠️',
    'TABLA': '📊',
    'PATRON': '📈',
    'RESUMEN': '📋'
}
