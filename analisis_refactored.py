# analisis_refactored.py
"""
Análisis principal de matrices de Mahjong - Versión refactorizada
"""

import numpy as np
from config import CONFIG, SYMBOLS
from matrix_analyzer import MatrixAnalyzer
from matrix_comparator import MatrixComparator

class MahjongAnalysisManager:
    """Gestor principal para el análisis de matrices de Mahjong"""
    
    def __init__(self, matrix_file=None, num_analyze=None):
        """
        Inicializa el gestor de análisis
        
        Args:
            matrix_file: Archivo de matriz a cargar (por defecto usa CONFIG)
            num_analyze: Número de matrices a analizar (por defecto usa CONFIG)
        """
        self.matrix_file = matrix_file or CONFIG['archivo_matriz']
        self.num_analyze = num_analyze or CONFIG['num_matrices_analizar']
        self.matrix = None
        self.analyzers = []
        self.summaries = []
    
    def load_matrix(self):
        """Carga la matriz desde archivo"""
        try:
            self.matrix = np.load(self.matrix_file)
            print(f"Matriz cargada con dimensiones: {self.matrix.shape}")
            print(f"Cada fila tiene {self.matrix.shape[1]} elementos (15x34 reformateados)")
            return True
        except FileNotFoundError:
            print(f"❌ Error: No se encontró '{self.matrix_file}'")
            print("Ejecuta primero 'python heatmap.py' para generar la matriz.")
            return False
        except Exception as e:
            print(f"❌ Error durante la carga: {e}")
            return False
    
    def analyze_individual_matrices(self):
        """Analiza matrices individuales"""
        if self.matrix is None:
            print("❌ No hay matriz cargada")
            return False
        
        num_to_analyze = min(self.num_analyze, self.matrix.shape[0])
        print(f"\nAnalizando {num_to_analyze} matrices individuales...")
        
        self.analyzers = []
        self.summaries = []
        
        for i in range(num_to_analyze):
            vector = self.matrix[i]
            analyzer = MatrixAnalyzer(vector, i)
            
            # Análisis detallado (opcional)
            if CONFIG['mostrar_debug']:
                analyzer.print_full_analysis()
            
            # Guardar analizador y resumen
            self.analyzers.append(analyzer)
            self.summaries.append(analyzer.get_summary())
        
        return True
    
    def run_comparisons(self):
        """Ejecuta las comparaciones entre matrices"""
        if not self.summaries:
            print("❌ No hay resúmenes para comparar")
            return False
        
        comparator = MatrixComparator(self.summaries)
        
        # Comparación básica
        comparator.print_basic_comparison()
        
        # Comparación secuencial (incluyendo análisis de manos del mismo jugador)
        comparator.print_sequential_comparison()
        
        # Resumen consolidado
        comparator.print_consolidated_summary()
        
        return True
    
    def print_executive_summary(self):
        """Imprime resumen ejecutivo"""
        print(f"\n{'='*60}")
        print("RESUMEN EJECUTIVO")
        print(f"{'='*60}")
        print(f"Se analizaron {len(self.summaries)} estados de juego de mahjong.")
        print(f"Cada estado contiene información completa sobre:")
        print("- Metadata del juego (viento, dealer, scores)")
        print("- Mano del jugador en turno")
        print("- Melds y descartes de todos los jugadores")
        print("- Estado del pond y fichas visibles")
        print(f"Los datos muestran la evolución temporal de una partida.")
    
    def run_full_analysis(self):
        """Ejecuta análisis completo"""
        print("🎯 Iniciando análisis completo de matrices de Mahjong")
        print("=" * 60)
        
        # Cargar matriz
        if not self.load_matrix():
            return False
        
        # Analizar matrices individuales
        if not self.analyze_individual_matrices():
            return False
        
        # Ejecutar comparaciones
        if not self.run_comparisons():
            return False
        
        # Resumen ejecutivo
        self.print_executive_summary()
        
        print(f"\n{SYMBOLS['EXITO']} Análisis completado exitosamente!")
        return True

def main():
    """Función principal"""
    # Crear y ejecutar el gestor de análisis
    manager = MahjongAnalysisManager()
    
    try:
        manager.run_full_analysis()
    except KeyboardInterrupt:
        print(f"\n⚠️ Análisis interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante el análisis: {e}")

if __name__ == "__main__":
    main()
