"""
Example 3: Backtesting EGP Strategy

Ví dụ về backtest chiến lược EGP trên dữ liệu lịch sử.
"""

import sys
sys.path.append('.')

from src.data.data_loader import VNDataLoader
from src.analysis.backtesting import Backtester
from src.visualization.plots import PortfolioVisualizer
import matplotlib.pyplot as plt


def run_backtest_example():
    """
    Backtest EGP strategy với rebalancing
    """
    
    print("=" * 70)
    print("EXAMPLE 3: BACKTESTING EGP PORTFOLIO STRATEGY")
    print("=" * 70)
    
    # ========== 1. LOAD DATA ==========
    print("\n[1] Loading historical data...")
    
    loader = VNDataLoader(
        start_date='2020-01-01',
        end_date='2024-12-31',
        frequency='D'
    )
    
    # VN30 stocks
    stocks = [
        'VNM', 'VIC', 'VHM', 'VCB', 'HPG',
        'MSN', 'MWG', 'FPT', 'GAS', 'TCB',
        'VPB', 'PLX', 'VRE', 'VJC', 'MBB',
        'BID', 'CTG', 'ACB', 'SSI', 'HDB'
    ]
    
    data = loader.get_data_bundle(
        stock_symbols=stocks,
        index_symbol='VNINDEX'
    )
    
    print(f"✓ Loaded {len(data['symbols'])} stocks")
    print(f"✓ Period: {data['start_date']} to {data['end_date']}")
    
    # ========== 2. RUN BACKTEST ==========
    print("\n[2] Running backtest...")
    print("Configuration:")
    print("  - Initial capital: 1,000,000,000 VND")
    print("  - Rebalance frequency: Monthly")
    print("  - Transaction cost: 0.15%")
    print("  - Risk-free rate: 5% annual")
    print("  - Max weight per stock: 30%")
    print()
    
    backtester = Backtester(
        data=data,
        initial_capital=1_000_000_000,
        rebalance_frequency='M',  # Monthly
        transaction_cost=0.0015,
        risk_free_rate=0.05
    )
    
    results = backtester.run(
        lookback_periods=252,  # 1 year
        optimizer_params={
            'allow_short': False,
            'max_weight': 0.30
        },
        benchmark=True
    )
    
    # ========== 3. ANALYZE RESULTS ==========
    print("\n[3] Detailed Analysis:")
    
    portfolio_values = results['portfolio_values']
    benchmark_values = results['benchmark_values']
    metrics = results['metrics']
    
    # Monthly returns analysis
    print("\nMonthly Statistics:")
    monthly_returns = portfolio_values['returns'].resample('M').sum()
    print(f"  Average monthly return: {monthly_returns.mean():.2%}")
    print(f"  Best month:            {monthly_returns.max():.2%}")
    print(f"  Worst month:           {monthly_returns.min():.2%}")
    print(f"  Positive months:       {(monthly_returns > 0).sum()} / {len(monthly_returns)}")
    
    # Rebalancing stats
    rebalance_history = results['rebalance_history']
    total_cost = sum(r['total_cost'] for r in rebalance_history)
    avg_cost = total_cost / len(rebalance_history)
    
    print(f"\nRebalancing Statistics:")
    print(f"  Total rebalances:      {len(rebalance_history)}")
    print(f"  Total transaction cost: {total_cost:,.0f} VND")
    print(f"  Average cost per rebalance: {avg_cost:,.0f} VND")
    print(f"  Cost as % of initial capital: {total_cost/1_000_000_000:.2%}")
    
    # Final portfolio
    print(f"\nFinal Portfolio Allocation:")
    final_weights = results['final_weights']
    if final_weights is not None:
        top_5 = final_weights.sort_values(ascending=False).head(5)
        for symbol, weight in top_5.items():
            print(f"  {symbol}: {weight:.2%}")
    
    # ========== 4. VISUALIZATION ==========
    print("\n[4] Creating visualizations...")
    
    viz = PortfolioVisualizer()
    
    # Performance comparison
    viz.plot_performance(
        portfolio_values=portfolio_values,
        benchmark_values=benchmark_values,
        title="EGP Strategy vs Benchmark (VNINDEX)"
    )
    
    # Returns distribution
    viz.plot_returns_distribution(
        returns=portfolio_values['returns'],
        title="Portfolio Returns Distribution"
    )
    
    # Rolling metrics
    viz.plot_rolling_metrics(
        returns=portfolio_values['returns'],
        window=60,
        title="Rolling Performance Metrics"
    )
    
    # ========== 5. YEARLY BREAKDOWN ==========
    print("\n[5] Yearly Performance Breakdown:")
    print("-" * 70)
    
    portfolio_values['year'] = portfolio_values.index.year
    yearly_perf = []
    
    for year in sorted(portfolio_values['year'].unique()):
        year_data = portfolio_values[portfolio_values['year'] == year]
        year_returns = year_data['returns'].dropna()
        
        if len(year_returns) > 0:
            total_return = (1 + year_returns).prod() - 1
            volatility = year_returns.std() * np.sqrt(252)
            sharpe = year_returns.mean() / year_returns.std() * np.sqrt(252) if year_returns.std() > 0 else 0
            
            yearly_perf.append({
                'Year': year,
                'Return': total_return,
                'Volatility': volatility,
                'Sharpe': sharpe,
                'Best Day': year_returns.max(),
                'Worst Day': year_returns.min()
            })
    
    import pandas as pd
    yearly_df = pd.DataFrame(yearly_perf)
    print(yearly_df.round(4))
    
    print("\n✓ Backtest complete!")
    print("=" * 70)
    
    return results


if __name__ == "__main__":
    import numpy as np
    results = run_backtest_example()
