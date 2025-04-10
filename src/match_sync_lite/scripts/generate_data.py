from faker import Faker
import pandas as pd
import random
from datetime import timedelta

fake = Faker('es_MX')

def generate_sales_data(n_records=10):
    """Generate sample sales data"""
    sales_data = {
        'Método': [random.choice(['Tarjeta', 'Efectivo', 'Transferencia']) for _ in range(n_records)],
        'Cliente': [fake.name() for _ in range(n_records)],
        'ID': list(range(1, n_records + 1)),
        'Venta': [fake.unique.bothify('VEN-####-???') for _ in range(n_records)],
        'Pago': [fake.bothify('PAGO-???-####') for _ in range(n_records)],
        'Fecha': [fake.date_between(start_date='-30d', end_date='today') for _ in range(n_records)],
        'Monto': [round(random.uniform(100, 5000), 2) for _ in range(n_records)],
        'Región': [random.choice(['Norte', 'Sur', 'Centro']) for _ in range(n_records)]
    }
    return pd.DataFrame(sales_data)

def generate_deposits_data(sales_data=None, n_records=10):
    """Generate sample deposits data"""
    if sales_data is None:
        sales_data = generate_sales_data(n_records)
    
    deposits_data = {
        'ID': sales_data['ID'].tolist(),
        'Referencia': sales_data['Pago'].tolist(),
        'Porcentaje': [100.0] * len(sales_data),
        'Conciliado': [True] * len(sales_data),
        'Código': sales_data['Pago'].tolist(),
        'Tipo': ['PAGO'] * len(sales_data),
        'Sufijo': [ref.split('-')[1] for ref in sales_data['Pago']]
    }
    return pd.DataFrame(deposits_data)