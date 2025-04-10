from pathlib import Path
import pandas as pd

def generar_estructura():
    """
    Genera el archivo 'estructura.xlsx' en la carpeta data/raw/ con la configuración
    de los campos que se utilizarán en el proceso de conciliación.
    """
    data = {
        "campo": ["referencia", "monto", "fecha"],
        "tipo": ["texto", "importe", "fecha"],
        "similar": ["si", "no", "no"],
        "depurar": ["si", "no", "no"],
        "factor": [None, 0.03, None],
        "ajuste_factor": [None, 0.01, None]
    }
    df_estructura = pd.DataFrame(data)
    
    # ROOT_DIR: Retrocede dos niveles desde scripts/
    ROOT_DIR = Path(__file__).resolve().parent.parent
    output_path = ROOT_DIR / "data" / "raw"
    output_path.mkdir(parents=True, exist_ok=True)
    output_file = output_path / "estructura.xlsx"
    
    df_estructura.to_excel(output_file, index=False)
    print(f"Archivo 'estructura.xlsx' generado en {output_file}")

if __name__ == "__main__":
    generar_estructura()