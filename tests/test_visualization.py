import pytest
import matplotlib.pyplot as plt
import os
from match_sync_lite.src.visualization.plot_results import plot_matching_distribution

def test_plot_generation(sample_data):
    """Test if plots are generated correctly"""
    matched_data = sample_data['sales'].merge(sample_data['deposits'], on='ID')
    
    # Test plot creation
    fig = plot_matching_distribution(matched_data)
    assert isinstance(fig, plt.Figure)
    plt.close(fig)

def test_plot_saving(temp_data_dir, sample_data):
    """Test if plots can be saved correctly"""
    matched_data = sample_data['sales'].merge(sample_data['deposits'], on='ID')
    output_path = f"{temp_data_dir}/test_plot.png"
    
    fig = plot_matching_distribution(matched_data)
    fig.savefig(output_path)
    assert os.path.exists(output_path)
    plt.close(fig)