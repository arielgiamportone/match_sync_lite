import matplotlib.pyplot as plt
import pandas as pd
from typing import Optional
import logging

logger = logging.getLogger(__name__)

def plot_matching_distribution(
    matched_data: pd.DataFrame,
    figsize: tuple[int, int] = (10, 6),
    title: str = 'Distribution of Matched Transactions',
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plot the distribution of matched transactions.
    
    Args:
        matched_data: DataFrame containing matching results
        figsize: Tuple of figure dimensions (width, height)
        title: Plot title
        save_path: Optional path to save the plot
        
    Returns:
        matplotlib.Figure: The generated plot figure
        
    Raises:
        ValueError: If matched_data is empty or missing required columns
    """
    try:
        if matched_data.empty:
            raise ValueError("Input DataFrame is empty")
        
        if 'Conciliado' not in matched_data.columns:
            raise ValueError("DataFrame missing 'Conciliado' column")
            
        fig, ax = plt.subplots(figsize=figsize)
        matched_counts = matched_data['Conciliado'].value_counts()
        
        # Create bar plot with custom styling
        matched_counts.plot(
            kind='bar',
            ax=ax,
            color=['#2ecc71', '#e74c3c']
        )
        
        # Customize plot appearance
        ax.set_title(title, pad=20, fontsize=12)
        ax.set_xlabel('Match Status', fontsize=10)
        ax.set_ylabel('Count', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # Add value labels on top of bars
        for i, v in enumerate(matched_counts):
            ax.text(i, v, str(v), ha='center', va='bottom')
            
        plt.tight_layout()
        
        if save_path:
            try:
                fig.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"Plot saved successfully to {save_path}")
            except Exception as e:
                logger.error(f"Failed to save plot: {str(e)}")
        
        return fig
        
    except Exception as e:
        logger.error(f"Error generating plot: {str(e)}")
        raise