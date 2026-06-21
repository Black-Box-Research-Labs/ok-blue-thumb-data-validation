"""
visualize.py - Create validation visualizations

Expected output: data/outputs/validation_plot.png
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
import yaml

def load_config():
    """Load configuration"""
    with open('config/config.yaml', 'r') as f:
        return yaml.safe_load(f)

def create_validation_plot(matches_df, config):
    """
    Create scatter plot comparing volunteer vs. professional measurements
    
    Shows:
    - Scatter plot of matched pairs
    - Linear regression line
    - 1:1 reference line (perfect agreement)
    - Statistics box (N, R², slope)
    """
    
    vol_values = matches_df['Vol_Value'].values
    pro_values = matches_df['Pro_Value'].values
    
    # Calculate regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(pro_values, vol_values)
    r_squared = r_value ** 2
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Scatter plot
    ax.scatter(pro_values, vol_values, alpha=0.6, s=100, color='steelblue',
               edgecolors='navy', linewidth=1, label='Matched Pairs')
    
    # Regression line
    x_line = np.linspace(pro_values.min(), pro_values.max(), 100)
    y_line = slope * x_line + intercept
    ax.plot(x_line, y_line, 'r-', linewidth=2, 
            label=f'Linear Fit (R²={r_squared:.3f})')
    
    # 1:1 reference line
    max_val = max(pro_values.max(), vol_values.max())
    ax.plot([0, max_val], [0, max_val], 'k--', linewidth=1.5, alpha=0.5,
            label='1:1 Reference')
    
    # Labels and formatting
    ax.set_xlabel('Professional Chloride (mg/L)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Volunteer Chloride (mg/L)', fontsize=14, fontweight='bold')
    ax.set_title('Blue Thumb Virtual Triangulation Results\nVolunteer vs. Professional Chloride Measurements',
                 fontsize=16, fontweight='bold', pad=20)
    
    # Statistics text box
    p_text = f'p = {p_value:.1e}' if p_value >= 1e-4 else 'p < 0.0001'
    stats_text = (f'N = {len(matches_df)}\n'
                  f'R² = {r_squared:.3f}\n'
                  f'Slope = {slope:.3f}\n'
                  f'{p_text}')
    ax.text(0.05, 0.95, stats_text, transform=ax.transAxes,
            fontsize=12, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # Grid and legend
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='lower right', fontsize=11)
    
    # Set equal aspect
    ax.set_aspect('equal', adjustable='box')
    
    plt.tight_layout()
    
    # Save
    output_dir = Path(config['output_paths']['results'])
    output_path = output_dir / "validation_plot.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    
    print(f"\nVisualization saved: {output_path}")
    
    plt.close()

def main():
    """Create all visualizations"""
    
    config = load_config()
    
    # Load matched pairs
    results_dir = Path(config['output_paths']['results'])
    matches_df = pd.read_csv(results_dir / "matched_pairs.csv")
    
    # Create validation plot
    create_validation_plot(matches_df, config)
    
    print("\n✅ Visualization complete")

if __name__ == "__main__":
    main()
