"""
Backtesting Module

Module để backtest chiến lược EGP portfolio optimization trên dữ liệu lịch sử.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from datetime import datetime
import warnings

from src.data.data_loader import VNDataLoader
from src.models.single_index_model import SingleIndexModel
from src.models.egp_optimizer import EGPOptimizer
from src.models.portfolio import Portfolio


class Backtester:
    """
    Backtest EGP portfolio strategy
    
    Attributes:
        data: Dict chứa stock/index returns và prices
        initial_capital: Vốn ban đầu
        rebalance_frequency: Tần suất rebalance ('M', 'Q', 'Y')
        transaction_cost: Phí giao dịch (%)
    """
    
    def __init__(
        self,
        data: Dict,
        initial_capital: float = 1_000_000_000,
        rebalance_frequency: str = 'M',
        transaction_cost: float = 0.0015,
        risk_free_rate: float = 0.05
    ):
        """
        Khởi tạo Backtester
        
        Args:
            data: Dict từ VNDataLoader.get_data_bundle()
            initial_capital: Vốn đầu tư ban đầu (VND)
            rebalance_frequency: 'M' (monthly), 'Q' (quarterly), 'Y' (yearly)
            transaction_cost: Transaction cost (% of trade value)
            risk_free_rate: Annualized risk-free rate
        """
        self.data = data
        self.stock_returns = data['stock_returns']
        self.index_returns = data['index_returns']
        self.stock_prices = data['stock_prices']
        self.index_prices = data['index_prices']
        
        self.initial_capital = initial_capital
        self.rebalance_frequency = rebalance_frequency
        self.transaction_cost = transaction_cost
        
        # Convert annual risk-free rate to period rate
        if data['frequency'] == 'D':
            self.risk_free_rate = risk_free_rate / 252
        elif data['frequency'] == 'W':
            self.risk_free_rate = risk_free_rate / 52
        elif data['frequency'] == 'M':
            self.risk_free_rate = risk_free_rate / 12
        else:
            self.risk_free_rate = risk_free_rate / 252
        
        # Results storage
        self.portfolio = None
        self.results = {}
        self.rebalance_history = []
        
    def _get_rebalance_dates(self) -> pd.DatetimeIndex:
        """
        Xác định các ngày rebalance
        
        Returns:
            DatetimeIndex của rebalance dates
        """
        dates = self.stock_returns.index
        
        if self.rebalance_frequency == 'M':
            # End of each month
            rebal_dates = dates.to_period('M').to_timestamp('M').unique()
        elif self.rebalance_frequency == 'Q':
            # End of each quarter
            rebal_dates = dates.to_period('Q').to_timestamp('Q').unique()
        elif self.rebalance_frequency == 'Y':
            # End of each year
            rebal_dates = dates.to_period('Y').to_timestamp('Y').unique()
        else:
            # Default to monthly
            rebal_dates = dates.to_period('M').to_timestamp('M').unique()
        
        # Keep only dates in our data range
        rebal_dates = [d for d in rebal_dates if d in dates]
        
        return pd.DatetimeIndex(rebal_dates)
    
    def _optimize_portfolio_at_date(
        self,
        date: datetime,
        lookback_periods: int = 252,
        optimizer_params: Optional[Dict] = None
    ) -> pd.Series:
        """
        Optimize portfolio tại một thời điểm cụ thể
        
        Args:
            date: Ngày optimize
            lookback_periods: Số periods lookback để estimate parameters
            optimizer_params: Parameters cho EGPOptimizer.optimize()
            
        Returns:
            Series weights
        """
        if optimizer_params is None:
            optimizer_params = {'allow_short': False, 'max_weight': 0.30}
        
        # Get historical data up to this date
        historical_returns = self.stock_returns.loc[:date].tail(lookback_periods)
        historical_index = self.index_returns.loc[:date].tail(lookback_periods)
        
        if len(historical_returns) < 30:
            warnings.warn(f"Insufficient data at {date}: {len(historical_returns)} periods")
            # Return equal weights
            n = len(self.stock_returns.columns)
            return pd.Series(1.0/n, index=self.stock_returns.columns)
        
        # Fit Single-Index Model
        sim = SingleIndexModel(
            stock_returns=historical_returns,
            market_returns=historical_index
        )
        sim.fit()
        
        # Optimize with EGP
        try:
            egp = EGPOptimizer(
                expected_returns=sim.get_expected_returns(),
                betas=sim.get_all_betas(),
                residual_vars=sim.get_all_residual_vars(),
                market_var=sim.market_var,
                risk_free_rate=self.risk_free_rate
            )
            
            weights = egp.optimize(**optimizer_params)
            
            return weights
            
        except Exception as e:
            warnings.warn(f"Optimization failed at {date}: {str(e)}")
            # Return equal weights
            n = len(self.stock_returns.columns)
            return pd.Series(1.0/n, index=self.stock_returns.columns)
    
    def run(
        self,
        lookback_periods: int = 252,
        optimizer_params: Optional[Dict] = None,
        benchmark: bool = True
    ) -> Dict:
        """
        Chạy backtest
        
        Args:
            lookback_periods: Số periods để estimate parameters
            optimizer_params: Parameters cho optimizer
            benchmark: Có tính benchmark (buy & hold market index) không
            
        Returns:
            Dict chứa kết quả backtest
        """
        print("=== Starting Backtest ===")
        print(f"Period: {self.stock_returns.index[0]} to {self.stock_returns.index[-1]}")
        print(f"Initial capital: {self.initial_capital:,.0f} VND")
        print(f"Rebalance frequency: {self.rebalance_frequency}")
        print(f"Transaction cost: {self.transaction_cost:.2%}\n")
        
        # Initialize portfolio
        self.portfolio = Portfolio(
            initial_capital=self.initial_capital,
            transaction_cost=self.transaction_cost
        )
        
        # Get rebalance dates
        rebalance_dates = self._get_rebalance_dates()
        print(f"Number of rebalances: {len(rebalance_dates)}\n")
        
        # Track daily portfolio value
        portfolio_values = []
        dates_list = []
        
        current_weights = None
        
        # Iterate through all dates
        for date in self.stock_returns.index:
            # Check if rebalance date
            if date in rebalance_dates:
                print(f"Rebalancing on {date.date()}...")
                
                # Optimize portfolio
                new_weights = self._optimize_portfolio_at_date(
                    date=date,
                    lookback_periods=lookback_periods,
                    optimizer_params=optimizer_params
                )
                
                # Rebalance
                prices_at_date = self.stock_prices.loc[date]
                rebal_info = self.portfolio.rebalance(
                    date=date,
                    target_weights=new_weights,
                    prices=prices_at_date
                )
                
                self.rebalance_history.append(rebal_info)
                current_weights = new_weights
                
                print(f"  Trades: {rebal_info['n_trades']}, Cost: {rebal_info['total_cost']:,.0f} VND")
            
            # Record portfolio state
            prices_at_date = self.stock_prices.loc[date]
            self.portfolio.record_state(date, prices_at_date)
            
            # Track value
            value = self.portfolio.get_portfolio_value(prices_at_date)
            portfolio_values.append(value)
            dates_list.append(date)
        
        print("\n=== Backtest Complete ===\n")
        
        # Create results DataFrame
        portfolio_df = pd.DataFrame({
            'date': dates_list,
            'value': portfolio_values
        }).set_index('date')
        
        portfolio_df['returns'] = portfolio_df['value'].pct_change()
        
        # Calculate metrics
        metrics = self._calculate_metrics(portfolio_df)
        
        # Benchmark (if requested)
        benchmark_df = None
        if benchmark:
            benchmark_df = self._calculate_benchmark()
            metrics['benchmark'] = self._calculate_metrics(benchmark_df)
        
        # Store results
        self.results = {
            'portfolio_values': portfolio_df,
            'benchmark_values': benchmark_df,
            'metrics': metrics,
            'rebalance_history': self.rebalance_history,
            'final_weights': current_weights
        }
        
        # Print summary
        self._print_summary()
        
        return self.results
    
    def _calculate_benchmark(self) -> pd.DataFrame:
        """
        Tính benchmark (buy & hold market index)
        
        Returns:
            DataFrame benchmark values
        """
        # Invest all capital in index
        initial_units = self.initial_capital / self.index_prices.iloc[0]
        
        benchmark_values = initial_units * self.index_prices
        benchmark_returns = self.index_returns
        
        benchmark_df = pd.DataFrame({
            'value': benchmark_values,
            'returns': benchmark_returns
        })
        
        return benchmark_df
    
    def _calculate_metrics(self, df: pd.DataFrame) -> Dict:
        """
        Tính performance metrics
        
        Args:
            df: DataFrame với columns 'value' và 'returns'
            
        Returns:
            Dict metrics
        """
        if len(df) < 2:
            return {}
        
        # Determine annualization factor
        if self.data['frequency'] == 'D':
            periods_per_year = 252
        elif self.data['frequency'] == 'W':
            periods_per_year = 52
        elif self.data['frequency'] == 'M':
            periods_per_year = 12
        else:
            periods_per_year = 252
        
        # Total return
        total_return = (df['value'].iloc[-1] - df['value'].iloc[0]) / df['value'].iloc[0]
        
        # Annualized return
        n_periods = len(df)
        years = n_periods / periods_per_year
        annualized_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0
        
        # Volatility
        returns = df['returns'].dropna()
        volatility = returns.std() * np.sqrt(periods_per_year)
        
        # Sharpe ratio
        mean_return = returns.mean() * periods_per_year
        sharpe = (mean_return - self.risk_free_rate * periods_per_year) / volatility if volatility > 0 else 0
        
        # Max drawdown
        cumulative = df['value'] / df['value'].iloc[0]
        running_max = cumulative.cummax()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Win rate
        win_rate = (returns > 0).sum() / len(returns) if len(returns) > 0 else 0
        
        return {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'final_value': df['value'].iloc[-1]
        }
    
    def _print_summary(self):
        """
        In ra summary của backtest
        """
        metrics = self.results['metrics']
        
        print("=== Portfolio Performance ===")
        print(f"Total Return:       {metrics['total_return']:>10.2%}")
        print(f"Annualized Return:  {metrics['annualized_return']:>10.2%}")
        print(f"Volatility:         {metrics['volatility']:>10.2%}")
        print(f"Sharpe Ratio:       {metrics['sharpe_ratio']:>10.4f}")
        print(f"Max Drawdown:       {metrics['max_drawdown']:>10.2%}")
        print(f"Win Rate:           {metrics['win_rate']:>10.2%}")
        print(f"Final Value:        {metrics['final_value']:>10,.0f} VND")
        
        if 'benchmark' in metrics:
            print("\n=== Benchmark Performance ===")
            bm = metrics['benchmark']
            print(f"Total Return:       {bm['total_return']:>10.2%}")
            print(f"Annualized Return:  {bm['annualized_return']:>10.2%}")
            print(f"Volatility:         {bm['volatility']:>10.2%}")
            print(f"Sharpe Ratio:       {bm['sharpe_ratio']:>10.4f}")
            print(f"Max Drawdown:       {bm['max_drawdown']:>10.2%}")
            
            print("\n=== Excess Performance ===")
            print(f"Excess Return:      {(metrics['total_return'] - bm['total_return']):>10.2%}")
            print(f"Excess Ann. Return: {(metrics['annualized_return'] - bm['annualized_return']):>10.2%}")


if __name__ == "__main__":
    # Example usage
    import sys
    sys.path.append('.')
    
    # Load data
    print("Loading data...")
    loader = VNDataLoader(start_date='2021-01-01', end_date='2024-12-31')
    stocks = ['VNM', 'VIC', 'VHM', 'VCB', 'HPG', 'MSN', 'MWG', 'FPT', 'GAS', 'TCB']
    
    data = loader.get_data_bundle(stocks, index_symbol='VNINDEX')
    
    # Run backtest
    backtester = Backtester(
        data=data,
        initial_capital=1_000_000_000,
        rebalance_frequency='M',
        transaction_cost=0.0015,
        risk_free_rate=0.05
    )
    
    results = backtester.run(
        lookback_periods=252,
        optimizer_params={'allow_short': False, 'max_weight': 0.30},
        benchmark=True
    )
