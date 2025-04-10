import pytest
import pandas as pd
from match_sync_lite.src.data.process_data import process_data, match_transactions

def test_data_loading(sample_data):
    """Test if data is loaded correctly"""
    sales_df = sample_data['sales']
    deposits_df = sample_data['deposits']
    
    assert not sales_df.empty
    assert not deposits_df.empty
    assert 'Monto' in sales_df.columns
    assert 'Referencia' in deposits_df.columns

def test_matching_logic(sample_data):
    """Test if matching logic works correctly"""
    sales_df = sample_data['sales']
    deposits_df = sample_data['deposits']
    
    # Test exact matches
    matched_df = match_transactions(sales_df, deposits_df)
    assert len(matched_df) > 0
    assert 'Conciliado' in matched_df.columns
    assert matched_df['Conciliado'].all()

def test_process_data_integration(temp_data_dir, sample_data):
    """Test the complete data processing pipeline"""
    sales_path = f"{temp_data_dir}/tabla1.xlsx"
    deposits_path = f"{temp_data_dir}/tabla2.xlsx"
    
    # Save sample data to temporary files
    sample_data['sales'].to_excel(sales_path, index=False)
    sample_data['deposits'].to_excel(deposits_path, index=False)
    
    result = process_data(sales_path, deposits_path)
    assert result is not None
    assert isinstance(result, pd.DataFrame)