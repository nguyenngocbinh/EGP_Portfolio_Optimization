"""
Example 2: Portfolio Optimization with Constraints

Ví dụ về optimization với các ràng buộc khác nhau.
"""

import sys
sys.path.append('.')

from src.data.data_loader import VNDataLoader
from src.models.single_index_model import SingleIndexModel
from src.models.egp_optimizer import EGPOptimizer
from src.visualization.plots import PortfolioVisualizer
import pandas as pd
import numpy as np


def compare_strategies():
    """
    So sánh các chiến lược optimization khác nhau
    """
    
    print("=" * 70)
    print("EXAMPLE 2: PORTFOLIO OPTIMIZATION WITH DIFFERENT CONSTRAINTS")
    print("=" * 70)
    
    # Load data
    print("\n[1] Loading data...")
    loader = VNDataLoader(start_date='2021-01-01', end_date='2024-12-31')
    stocks = ['VNM', 'VIC', 'VHM', 'VCB', 'HPG', 'MSN', 'MWG', 'FPT', 'GAS', 'TCB']
    
    data = loader.get_data_bundle(stocks, index_symbol='VNINDEX')
    
    # Fit model
    print("\n[2] Fitting Single-Index Model...")
    sim = SingleIndexModel(data['stock_returns'], data['index_returns'])
    sim.fit()
    
    # Get parameters
    expected_returns = sim.get_expected_returns()
    betas = sim.get_all_betas()
    residual_vars = sim.get_all_residual_vars()
    market_var = sim.market_var
    risk_free_rate = 0.05 / 252
    
    # ========== STRATEGY DEFINITIONS ==========
    strategies = {
        'Equal Weight': {
            'type': 'equal',
            'weights': pd.Series(1.0/len(stocks), index=stocks)
        },
        'No Constraints': {
            'allow_short': False,
            'max_weight': None,
            'min_weight': None
        },
        'Max 30% per stock': {
            'allow_short': False,
            'max_weight': 0.30,
            'min_weight': None
        },
        'Max 25%, Min 5%': {
            'allow_short': False,
            'max_weight': 0.25,
            'min_weight': 0.05
        },
        'Concentrated (Max 50%)': {
            'allow_short': False,
            'max_weight': 0.50,
            'min_weight': None
        },
    }
    
    # ========== RUN STRATEGIES ==========
    print("\n[3] Running optimization strategies...\n")
    
    results = {}
    
    for name, params in strategies.items():
        print(f"Strategy: {name}")
        
        if params.get('type') == 'equal':
            # Equal weight strategy
            weights = params['weights']
        else:
            # EGP optimization
            egp = EGPOptimizer(
                expected_returns=expected_returns,
                betas=betas,
                residual_vars=residual_vars,
                market_var=market_var,
                risk_free_rate=risk_free_rate
            )
            
            weights = egp.optimize(**params)
            stats = egp.get_portfolio_statistics()
        
        # Calculate portfolio metrics for equal weight
        if params.get('type') == 'equal':
            port_return = (weights * expected_returns).sum()
            port_beta = (weights * betas).sum()
            systematic_var = (port_beta ** 2) * market_var
            idio_var = ((weights ** 2) * residual_vars).sum()
            port_var = systematic_var + idio_var
            port_std = np.sqrt(port_var)
            sharpe = (port_return - risk_free_rate) / port_std if port_std > 0 else 0
            
            stats = {
                'portfolio_return': port_return,
                'portfolio_std': port_std,
                'portfolio_beta': port_beta,
                'sharpe_ratio': sharpe,
                'n_stocks': (weights > 0).sum()
            }
        
        results[name] = {
            'weights': weights,
            'stats': stats
        }
        
        print(f"  Return (annual): {stats['portfolio_return']*252:.2%}")
        print(f"  Std (annual):    {stats['portfolio_std']*np.sqrt(252):.2%}")
        print(f"  Sharpe (annual): {stats['sharpe_ratio']*np.sqrt(252):.4f}")
        print(f"  Portfolio Beta:  {stats['portfolio_beta']:.4f}")
        print(f"  Num stocks:      {stats['n_stocks']}")
        print(f"  Top holding:     {weights.abs().max():.2%}")
        print()
    
    # ========== COMPARISON TABLE ==========
    print("\n[4] Strategy Comparison:")
    print("-" * 70)
    
    comparison = pd.DataFrame({
        name: {
            'Annual Return': res['stats']['portfolio_return'] * 252,
            'Annual Std': res['stats']['portfolio_std'] * np.sqrt(252),
            'Annual Sharpe': res['stats']['sharpe_ratio'] * np.sqrt(252),
            'Beta': res['stats']['portfolio_beta'],
            'N Stocks': res['stats']['n_stocks'],
            'Max Weight': res['weights'].abs().max()
        }
        for name, res in results.items()
    }).T
    
    print(comparison.round(4))
    
    # ========== VISUALIZE TOP STRATEGIES ==========
    print("\n[5] Visualizing strategies...")
    
    viz = PortfolioVisualizer()
    
    # Plot allocations of different strategies
    import matplotlib.pyplot as plt
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    
    for idx, (name, res) in enumerate(results.items()):
        if idx >= 6:
            break
        
        weights = res['weights']
        weights = weights[weights.abs() > 1e-6].sort_values(ascending=False)
        
        ax = axes[idx]
        colors = ['blue' if w > 0 else 'red' for w in weights.values]
        ax.bar(range(len(weights)), weights.values, color=colors)
        ax.set_xticks(range(len(weights)))
        ax.set_xticklabels(weights.index, rotation=45, ha='right')
        ax.set_ylabel('Weight')
        ax.set_title(name)
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('output/strategy_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("\n✓ Comparison complete!")
    print("=" * 70)
    
    return results


if __name__ == "__main__":
    results = compare_strategies()
