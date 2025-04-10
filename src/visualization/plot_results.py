# src/visualization/plot_results.py

import pandas as pd
import matplotlib.pyplot as plt

def plot_match_score_distribution(df, output_file):
    bins = [0, 20, 40, 60, 80, 100]
    df['score_bin'] = pd.cut(df['match_score'], bins=bins, right=True)
    freq = df['score_bin'].value_counts(sort=False)
    
    plt.figure(figsize=(8, 5))
    freq.plot(kind='bar')
    plt.title("Distribución de Puntaje de Matching")
    plt.xlabel("Rango de Puntaje")
    plt.ylabel("Frecuencia")
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()
