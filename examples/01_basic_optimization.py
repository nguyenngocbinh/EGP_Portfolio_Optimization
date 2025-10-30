"""
Example 1: Basic EGP Portfolio Optimization

Ví dụ cơ bản về cách sử dụng EGP để tối ưu hóa portfolio.
"""

import sys
sys.path.append('.')

from src.data.data_loader import VNDataLoader
from src.models.single_index_model import SingleIndexModel
from src.models.egp_optimizer import EGPOptimizer
from src.visualization.plots import PortfolioVisualizer


def main():
    """
    Main function - Basic portfolio optimization example
    """
    
    print("=" * 60)
    print("EXAMPLE 1: BASIC EGP PORTFOLIO OPTIMIZATION")
    print("=" * 60)
    
    # ========== 1. LOAD DATA ==========
    print("\n[1] Loading data from VNDirect...")
    
    loader = VNDataLoader(
        start_date='2021-01-01',
        end_date='2024-12-31',
        frequency='D'  # Daily data
    )
    
    # Danh sách cổ phiếu (VN30 stocks)
    stock_symbols = [
        'VNM', 'VIC', 'VHM', 'VCB', 'HPG',
        'MSN', 'MWG', 'FPT', 'GAS', 'TCB',
        'VPB', 'PLX', 'VRE', 'VJC', 'MBB'
    ]
    
    data = loader.get_data_bundle(
        stock_symbols=stock_symbols,
        index_symbol='VNINDEX',
        return_method='simple'
    )
    
    print(f"✓ Loaded {len(data['symbols'])} stocks")
    print(f"✓ Period: {data['start_date']} to {data['end_date']}")
    print(f"✓ Number of observations: {len(data['stock_returns'])}")
    
    # ========== 2. FIT SINGLE-INDEX MODEL ==========
    print("\n[2] Fitting Single-Index Model...")
    
    sim = SingleIndexModel(
        stock_returns=data['stock_returns'],
        market_returns=data['index_returns']
    )
    
    results = sim.fit()
    
    print(f"✓ Successfully fitted {len(results)} stocks")
    print(f"✓ Market variance: {sim.market_var:.6f}")
    
    # Show model summary
    print("\nModel Summary (Top 5 by Beta):")
    summary = sim.summary(sort_by='beta')
    print(summary.head()[['beta', 'alpha', 'r_squared']].round(4))
    
    # ========== 3. OPTIMIZE PORTFOLIO WITH EGP ==========
    print("\n[3] Running EGP Optimization...")
    
    # Get parameters
    expected_returns = sim.get_expected_returns()
    betas = sim.get_all_betas()
    residual_vars = sim.get_all_residual_vars()
    
    # Initialize optimizer
    egp = EGPOptimizer(
        expected_returns=expected_returns,
        betas=betas,
        residual_vars=residual_vars,
        market_var=sim.market_var,
        risk_free_rate=0.05 / 252  # 5% annual -> daily
    )
    
    # Optimize portfolio
    # No short selling, max 30% per stock
    weights = egp.optimize(
        allow_short=False,
        max_weight=0.30,
        min_weight=0.01
    )
    
    print("\n✓ Optimization complete!")
    
    # Show weights
    print("\nPortfolio Weights:")
    print(weights.sort_values(ascending=False).round(4))
    
    # ========== 4. PORTFOLIO STATISTICS ==========
    print("\n[4] Portfolio Statistics:")
    
    stats = egp.get_portfolio_statistics()
    
    print(f"  Expected Return (daily):  {stats['portfolio_return']:.6f}")
    print(f"  Expected Return (annual): {stats['portfolio_return']*252:.4%}")
    print(f"  Portfolio Std (daily):    {stats['portfolio_std']:.6f}")
    print(f"  Portfolio Std (annual):   {stats['portfolio_std']*np.sqrt(252):.4%}")
    print(f"  Portfolio Beta:           {stats['portfolio_beta']:.4f}")
    print(f"  Sharpe Ratio (daily):     {stats['sharpe_ratio']:.4f}")
    print(f"  Sharpe Ratio (annual):    {stats['sharpe_ratio']*np.sqrt(252):.4f}")
    print(f"  Number of stocks:         {stats['n_stocks']}")
    print(f"  C₀ (cutoff constant):     {stats['C0']:.6f}")
    
    # ========== 5. TOP HOLDINGS ==========
    print("\n[5] Top 5 Holdings:")
    
    top_holdings = egp.get_top_holdings(n=5)
    print(top_holdings.round(4))
    
    # ========== 6. VISUALIZATION ==========
    print("\n[6] Creating visualizations...")
    
    viz = PortfolioVisualizer()
    
    # Plot allocation
    viz.plot_allocation(
        weights,
        title="EGP Optimal Portfolio Allocation"
    )
    
    print("\n✓ All done!")
    print("=" * 60)


if __name__ == "__main__":
    import numpy as np
    main()
