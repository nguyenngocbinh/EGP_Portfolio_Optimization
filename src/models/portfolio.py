"""
Portfolio Module

Class quản lý danh mục đầu tư, tracking performance, rebalancing.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, List
from datetime import datetime


class Portfolio:
    """
    Portfolio management class
    
    Quản lý danh mục đầu tư, tính toán performance metrics,
    thực hiện rebalancing.
    """
    
    def __init__(
        self,
        initial_capital: float = 1_000_000_000,  # 1 billion VND
        transaction_cost: float = 0.0015  # 0.15%
    ):
        """
        Khởi tạo Portfolio
        
        Args:
            initial_capital: Vốn ban đầu (VND)
            transaction_cost: Phí giao dịch (% of transaction value)
        """
        self.initial_capital = initial_capital
        self.transaction_cost = transaction_cost
        
        # Portfolio state
        self.cash = initial_capital
        self.holdings = {}  # {symbol: quantity}
        self.weights = {}  # {symbol: weight}
        
        # History tracking
        self.history = []
        self.rebalance_dates = []
        
    def rebalance(
        self,
        date: datetime,
        target_weights: pd.Series,
        prices: pd.Series
    ) -> Dict:
        """
        Rebalance portfolio đến target weights
        
        Args:
            date: Ngày rebalance
            target_weights: Target weights (Series with symbol index)
            prices: Giá hiện tại của các stocks (Series with symbol index)
            
        Returns:
            Dict chứa thông tin rebalance (trades, costs, etc.)
        """
        # Calculate current portfolio value
        portfolio_value = self.get_portfolio_value(prices)
        
        # Calculate target quantities
        target_quantities = {}
        for symbol in target_weights.index:
            if symbol not in prices.index or pd.isna(prices[symbol]):
                continue
            
            target_value = target_weights[symbol] * portfolio_value
            target_quantities[symbol] = int(target_value / prices[symbol])
        
        # Calculate trades needed
        trades = {}
        total_cost = 0
        
        for symbol, target_qty in target_quantities.items():
            current_qty = self.holdings.get(symbol, 0)
            trade_qty = target_qty - current_qty
            
            if trade_qty != 0:
                trade_value = abs(trade_qty) * prices[symbol]
                cost = trade_value * self.transaction_cost
                
                trades[symbol] = {
                    'quantity': trade_qty,
                    'price': prices[symbol],
                    'value': trade_qty * prices[symbol],
                    'cost': cost
                }
                
                total_cost += cost
                
                # Update holdings
                self.holdings[symbol] = target_qty
        
        # Adjust cash
        cash_flow = sum(t['value'] for t in trades.values())
        self.cash -= (cash_flow + total_cost)
        
        # Update weights
        self.weights = target_weights.to_dict()
        
        # Record rebalance
        self.rebalance_dates.append(date)
        
        return {
            'date': date,
            'trades': trades,
            'total_cost': total_cost,
            'portfolio_value': portfolio_value,
            'n_trades': len(trades)
        }
    
    def get_portfolio_value(self, prices: pd.Series) -> float:
        """
        Tính tổng giá trị danh mục
        
        Args:
            prices: Giá hiện tại của stocks
            
        Returns:
            Total portfolio value
        """
        holdings_value = 0
        for symbol, quantity in self.holdings.items():
            if symbol in prices.index and not pd.isna(prices[symbol]):
                holdings_value += quantity * prices[symbol]
        
        return self.cash + holdings_value
    
    def get_returns(self, current_value: float) -> float:
        """
        Tính return so với vốn ban đầu
        
        Args:
            current_value: Giá trị hiện tại
            
        Returns:
            Return (%)
        """
        return (current_value - self.initial_capital) / self.initial_capital
    
    def record_state(
        self,
        date: datetime,
        prices: pd.Series
    ):
        """
        Ghi lại trạng thái portfolio
        
        Args:
            date: Ngày ghi nhận
            prices: Giá của stocks
        """
        value = self.get_portfolio_value(prices)
        returns = self.get_returns(value)
        
        self.history.append({
            'date': date,
            'value': value,
            'cash': self.cash,
            'returns': returns,
            'holdings': self.holdings.copy()
        })
    
    def get_history_df(self) -> pd.DataFrame:
        """
        Lấy lịch sử portfolio dưới dạng DataFrame
        
        Returns:
            DataFrame với columns: date, value, cash, returns
        """
        if not self.history:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.history)
        df = df.set_index('date')
        return df[['value', 'cash', 'returns']]
    
    def calculate_metrics(self, prices_df: pd.DataFrame, frequency: str = 'D') -> Dict:
        """
        Tính các performance metrics
        
        Args:
            prices_df: DataFrame giá lịch sử
            frequency: Frequency của data ('D', 'W', 'M')
            
        Returns:
            Dict chứa metrics
        """
        history_df = self.get_history_df()
        
        if len(history_df) < 2:
            return {}
        
        # Annualization factor
        if frequency == 'D':
            periods_per_year = 252
        elif frequency == 'W':
            periods_per_year = 52
        elif frequency == 'M':
            periods_per_year = 12
        else:
            periods_per_year = 252
        
        # Calculate returns series
        returns_series = history_df['returns'].pct_change().dropna()
        
        # Total return
        total_return = history_df['returns'].iloc[-1]
        
        # Annualized return
        n_periods = len(history_df)
        years = n_periods / periods_per_year
        annualized_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0
        
        # Volatility
        volatility = returns_series.std() * np.sqrt(periods_per_year)
        
        # Sharpe ratio (assuming risk-free rate = 0)
        sharpe = annualized_return / volatility if volatility > 0 else 0
        
        # Max drawdown
        cumulative = (1 + history_df['returns'])
        running_max = cumulative.cummax()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Win rate
        win_rate = (returns_series > 0).sum() / len(returns_series) if len(returns_series) > 0 else 0
        
        return {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'n_periods': n_periods,
            'n_rebalances': len(self.rebalance_dates)
        }


if __name__ == "__main__":
    # Example usage
    portfolio = Portfolio(initial_capital=1_000_000_000)
    
    # Simulate some data
    test_weights = pd.Series({'VNM': 0.3, 'VIC': 0.3, 'VCB': 0.4})
    test_prices = pd.Series({'VNM': 80000, 'VIC': 45000, 'VCB': 90000})
    
    # Rebalance
    rebal_info = portfolio.rebalance(
        date=datetime(2024, 1, 1),
        target_weights=test_weights,
        prices=test_prices
    )
    
    print("=== Rebalance Info ===")
    print(f"Total cost: {rebal_info['total_cost']:,.0f} VND")
    print(f"Number of trades: {rebal_info['n_trades']}")
    
    # Record state
    portfolio.record_state(datetime(2024, 1, 1), test_prices)
    
    print("\n=== Portfolio Value ===")
    print(f"{portfolio.get_portfolio_value(test_prices):,.0f} VND")
