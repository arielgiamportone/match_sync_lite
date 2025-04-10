import pytest
import pandas as pd
import os
import tempfile

@pytest.fixture
def sample_data():
    """Fixture to provide sample test data"""
    sales_data = {
        'Método': ['Tarjeta', 'Transferencia'],
        'Cliente': ['John Doe', 'Jane Smith'],
        'ID': [1, 1],
        'Venta': ['VEN-8883-SEj', 'VEN-8890-mia'],
        'Pago': ['PAGO-NOI-4881', 'PAGO-ASv-5294'],
        'Fecha': ['2025-04-04', '2025-03-17'],
        'Monto': [3404.81, 3768.95],
        'Región': ['Centro', 'Norte']
    }
    
    deposits_data = {
        'ID': [1, 1],
        'Referencia': ['PAGO-NOI-4881', 'PAGO-ASv-5294'],
        'Porcentaje': [100.0, 100.0],
        'Conciliado': [True, True],
        'Código': ['PAGO-NOI-4881', 'PAGO-ASv-5294'],
        'Tipo': ['PAGO', 'PAGO'],
        'Sufijo': ['NOI', 'ASv']
    }
    
    return {
        'sales': pd.DataFrame(sales_data),
        'deposits': pd.DataFrame(deposits_data)
    }

@pytest.fixture
def temp_data_dir():
    """Fixture to provide temporary directory for test data"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir