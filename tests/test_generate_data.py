import pytest
from match_sync_lite.scripts.generate_data import generate_sales_data, generate_deposits_data

def test_sales_data_generation():
    """Test sales data generation"""
    sales_data = generate_sales_data(n_records=10)
    assert len(sales_data) == 10
    required_columns = ['Método', 'Cliente', 'ID', 'Venta', 'Pago', 'Fecha', 'Monto', 'Región']
    assert all(col in sales_data.columns for col in required_columns)

def test_deposits_data_generation():
    """Test deposits data generation"""
    deposits_data = generate_deposits_data(n_records=10)
    assert len(deposits_data) == 10
    required_columns = ['ID', 'Referencia', 'Porcentaje', 'Conciliado', 'Código', 'Tipo', 'Sufijo']
    assert all(col in deposits_data.columns for col in required_columns)

def test_data_consistency():
    """Test consistency between generated sales and deposits"""
    sales_data = generate_sales_data(n_records=5)
    deposits_data = generate_deposits_data(sales_data)
    
    assert len(sales_data) == len(deposits_data)
    assert all(sale_id in deposits_data['ID'].values for sale_id in sales_data['ID'])