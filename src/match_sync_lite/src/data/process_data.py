import pandas as pd

def process_data(sales_path, deposits_path):
    """Process sales and deposits data"""
    sales_df = pd.read_excel(sales_path)
    deposits_df = pd.read_excel(deposits_path)
    return match_transactions(sales_df, deposits_df)

def match_transactions(sales_df, deposits_df):
    """Match transactions between sales and deposits"""
    matched_df = sales_df.merge(
        deposits_df,
        on=['ID'],
        how='left'
    )
    matched_df['Conciliado'] = matched_df['Referencia'].notna()
    return matched_df