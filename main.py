# main.py

import logging
from pathlib import Path
import subprocess
import sys

from src.data.process_data import ConciliadorAvanzado
try:
    from src.visualization.plot_results import plot_match_score_distribution
except ImportError:
    plot_match_score_distribution = None

logging.basicConfig(level=logging.INFO)

def run_script(script_path):
    """Ejecuta un script de Python dado su path."""
    result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
    if result.returncode != 0:
        logging.error(f"Error ejecutando {script_path}:\n{result.stderr}")
    else:
        logging.info(result.stdout)

def main():
    # Generar la estructura
    logging.info("Generando la estructura...")
    run_script(str(Path("scripts") / "genera_estructura.py"))
    
    # Generar datos de ejemplo
    logging.info("Generando datos de ejemplo con Faker...")
    run_script(str(Path("scripts") / "generate_data.py"))
    
    # Ejecutar el proceso de conciliación
    logging.info("Iniciando el proceso de conciliación de datos...")
    conciliador = ConciliadorAvanzado()
    tabla1_final, tabla2_final = conciliador.conciliacion_iterativa()
    conciliador.generar_reporte(tabla1_final, tabla2_final)
    conciliador.validacion_cruzada(tabla1_final)
    
    # (Opcional) Generar visualización adicional
    if plot_match_score_distribution:
        output_plot = Path("reports") / "match_score_distribution.png"
        plot_match_score_distribution(tabla1_final, str(output_plot))
        logging.info(f"Plot generado en: {output_plot}")
    else:
        logging.info("Módulo de visualización no encontrado; omitiendo plot.")
    
    logging.info("Proceso completado. Revise los reportes en la carpeta 'reports'.")

if __name__ == "__main__":
    main()
