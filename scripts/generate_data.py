# scripts/generate_data.py

from faker import Faker
import pandas as pd
import random
from datetime import timedelta
from pathlib import Path

fake = Faker('es_MX')

def generate_retail_data(registros: int = 500):
    """
    Genera datos de ventas y depósitos para el escenario "MatchSync Lite" en la industria retail.
    - tabla1.xlsx contendrá datos de ventas.
    - tabla2.xlsx contendrá datos de depósitos.
    """
    # Generar datos de ventas (tabla1)
    ventas = []
    for _ in range(registros):
        fecha = fake.date_between(start_date='-30d', end_date='today')
        ventas.append({
            'id': fake.unique.bothify('VEN-####-???'),
            'referencia': fake.bothify('PAGO-???-####'),
            'fecha': fecha,
            'monto': round(random.uniform(100, 5000), 2),
            'sucursal': random.choice(['Norte', 'Sur', 'Centro']),
            'metodo_pago': random.choice(['Tarjeta', 'Efectivo', 'Transferencia']),
            'cliente': fake.name(),
            'segregable': 1,   # Suponemos que inicialmente es segregable 1 vez
            'subid': "1"
        })
    
    # Generar datos de depósitos (tabla2)
    depositos = []
    for venta in ventas:
        if random.random() < 0.8:
            depositos.append({
                'id': fake.unique.bothify('DEP-####-???'),
                'referencia': venta['referencia'],
                'fecha': venta['fecha'] + timedelta(days=random.randint(0,2)),
                'monto': round(venta['monto'] * (1 + random.uniform(-0.03, 0.03)), 2),
                'sucursal': venta['sucursal'].upper() if random.random() < 0.3 else venta['sucursal'],
                'comision': round(venta['monto'] * 0.02, 2)
            })
        else:
            depositos.append({
                'id': fake.unique.bothify('DEP-####-???'),
                'referencia': fake.bothify('PAGO-???-####'),
                'fecha': fake.date_between(start_date='-30d', end_date='today'),
                'monto': round(random.uniform(100, 5000), 2),
                'sucursal': random.choice(['NORTE', 'SUR', 'CENTRO', 'Oriente']),
                'comision': round(random.uniform(10, 100), 2)
            })
    
    # Guardar datos en data/raw/
    ROOT_DIR = Path(__file__).resolve().parent.parent
    output_path = ROOT_DIR / "data" / "raw"
    output_path.mkdir(parents=True, exist_ok=True)
    tabla1_file = output_path / "tabla1.xlsx"
    tabla2_file = output_path / "tabla2.xlsx"
    
    pd.DataFrame(ventas).to_excel(tabla1_file, index=False)
    pd.DataFrame(depositos).to_excel(tabla2_file, index=False)
    print(f"Datos generados y guardados en {output_path}")

if __name__ == "__main__":
    generate_retail_data()