"""
Visualization Module

Module để vẽ charts và graphs cho portfolio analysis.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, List, Dict
import warnings

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10


class PortfolioVisualizer:
    """
    Class để visualize portfolio analysis results
    """
    
    def __init__(self, style: str = 'seaborn'):
        """
        Khởi tạo visualizer
        
        Args:
            style: Matplotlib style
        """
        self.style = style
        if style in plt.style.available:
            plt.style.use(style)
    
    def plot_allocation(
        self,
        weights: pd.Series,
        title: str = "Portfolio Allocation",
        figsize: tuple = (10, 6),
        save_path: Optional[str] = None
    ):
        """
        Plot portfolio allocation (pie chart hoặc bar chart)
        
        Args:
            weights: Series portfolio weights
            title: Chart title
            figsize: Figure size
            save_path: Path để save figure
        """
        # Remove zero weights
        weights = weights[weights.abs() > 1e-6].sort_values(ascending=False)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        
        # Pie chart
        colors = sns.color_palette("husl", len(weights))
        ax1.pie(
            weights.abs(),
            labels=weights.index,
            autopct='%1.1f%%',
            startangle=90,
            colors=colors
        )
        ax1.set_title(f"{title} - Pie Chart")
        
        # Bar chart
        ax2.bar(range(len(weights)), weights.values, color=colors)
        ax2.set_xticks(range(len(weights)))
        ax2.set_xticklabels(weights.index, rotation=45, ha='right')
        ax2.set_ylabel('Weight')
        ax2.set_title(f"{title} - Bar Chart")
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def plot_performance(
        self,
        portfolio_values: pd.DataFrame,
        benchmark_values: Optional[pd.DataFrame] = None,
        title: str = "Portfolio Performance",
        figsize: tuple = (12, 8),
        save_path: Optional[str] = None
    ):
        """
        Plot portfolio performance vs benchmark
        
        Args:
            portfolio_values: DataFrame với 'value' column
            benchmark_values: DataFrame benchmark values (optional)
            title: Chart title
            figsize: Figure size
            save_path: Save path
        """
        fig, axes = plt.subplots(2, 1, figsize=figsize, sharex=True)
        
        # Normalize to 100
        portfolio_norm = (portfolio_values['value'] / portfolio_values['value'].iloc[0]) * 100
        
        # Plot cumulative value
        ax1 = axes[0]
        ax1.plot(portfolio_norm.index, portfolio_norm.values, 
                label='Portfolio', linewidth=2, color='blue')
        
        if benchmark_values is not None:
            benchmark_norm = (benchmark_values['value'] / benchmark_values['value'].iloc[0]) * 100
            ax1.plot(benchmark_norm.index, benchmark_norm.values,
                    label='Benchmark', linewidth=2, color='red', alpha=0.7)
        
        ax1.set_ylabel('Cumulative Value (Base 100)')
        ax1.set_title(f"{title} - Cumulative Returns")
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot drawdown
        ax2 = axes[1]
        running_max = portfolio_norm.cummax()
        drawdown = (portfolio_norm - running_max) / running_max * 100
        
        ax2.fill_between(drawdown.index, drawdown.values, 0, 
                         color='red', alpha=0.3, label='Drawdown')
        ax2.plot(drawdown.index, drawdown.values, color='red', linewidth=1)
        
        if benchmark_values is not None:
            bm_running_max = benchmark_norm.cummax()
            bm_drawdown = (benchmark_norm - bm_running_max) / bm_running_max * 100
            ax2.plot(bm_drawdown.index, bm_drawdown.values,
                    color='orange', linewidth=1, alpha=0.7, label='Benchmark DD')
        
        ax2.set_ylabel('Drawdown (%)')
        ax2.set_xlabel('Date')
        ax2.set_title('Drawdown Analysis')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def plot_returns_distribution(
        self,
        returns: pd.Series,
        title: str = "Returns Distribution",
        bins: int = 50,
        figsize: tuple = (12, 6),
        save_path: Optional[str] = None
    ):
        """
        Plot distribution of returns
        
        Args:
            returns: Series of returns
            title: Chart title
            bins: Number of histogram bins
            figsize: Figure size
            save_path: Save path
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        
        # Histogram
        ax1.hist(returns.dropna(), bins=bins, alpha=0.7, color='blue', edgecolor='black')
        ax1.axvline(returns.mean(), color='red', linestyle='--', 
                   label=f'Mean: {returns.mean():.4f}')
        ax1.axvline(returns.median(), color='green', linestyle='--',
                   label=f'Median: {returns.median():.4f}')
        ax1.set_xlabel('Returns')
        ax1.set_ylabel('Frequency')
        ax1.set_title(f"{title} - Histogram")
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Q-Q plot
        from scipy import stats
        stats.probplot(returns.dropna(), dist="norm", plot=ax2)
        ax2.set_title(f"{title} - Q-Q Plot")
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def plot_rolling_metrics(
        self,
        returns: pd.Series,
        window: int = 60,
        title: str = "Rolling Metrics",
        figsize: tuple = (12, 10),
        save_path: Optional[str] = None
    ):
        """
        Plot rolling metrics (mean, std, sharpe)
        
        Args:
            returns: Series of returns
            window: Rolling window size
            title: Chart title
            figsize: Figure size
            save_path: Save path
        """
        fig, axes = plt.subplots(3, 1, figsize=figsize, sharex=True)
        
        # Rolling mean
        rolling_mean = returns.rolling(window=window).mean()
        axes[0].plot(rolling_mean.index, rolling_mean.values, linewidth=2)
        axes[0].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        axes[0].set_ylabel('Rolling Mean')
        axes[0].set_title(f"{title} - Rolling Mean ({window} periods)")
        axes[0].grid(True, alpha=0.3)
        
        # Rolling std
        rolling_std = returns.rolling(window=window).std()
        axes[1].plot(rolling_std.index, rolling_std.values, 
                    linewidth=2, color='orange')
        axes[1].set_ylabel('Rolling Std')
        axes[1].set_title(f"Rolling Volatility ({window} periods)")
        axes[1].grid(True, alpha=0.3)
        
        # Rolling Sharpe
        rolling_sharpe = rolling_mean / rolling_std
        axes[2].plot(rolling_sharpe.index, rolling_sharpe.values,
                    linewidth=2, color='green')
        axes[2].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        axes[2].set_ylabel('Rolling Sharpe')
        axes[2].set_xlabel('Date')
        axes[2].set_title(f"Rolling Sharpe Ratio ({window} periods)")
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def plot_correlation_matrix(
        self,
        returns: pd.DataFrame,
        title: str = "Correlation Matrix",
        figsize: tuple = (10, 8),
        save_path: Optional[str] = None
    ):
        """
        Plot correlation matrix heatmap
        
        Args:
            returns: DataFrame of returns
            title: Chart title
            figsize: Figure size
            save_path: Save path
        """
        corr = returns.corr()
        
        plt.figure(figsize=figsize)
        sns.heatmap(
            corr,
            annot=True,
            fmt='.2f',
            cmap='coolwarm',
            center=0,
            square=True,
            linewidths=1,
            cbar_kws={"shrink": 0.8}
        )
        plt.title(title)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def plot_efficient_frontier(
        self,
        returns_list: List[float],
        risks_list: List[float],
        optimal_point: Optional[tuple] = None,
        title: str = "Efficient Frontier",
        figsize: tuple = (10, 6),
        save_path: Optional[str] = None
    ):
        """
        Plot efficient frontier
        
        Args:
            returns_list: List of expected returns
            risks_list: List of risks (std)
            optimal_point: Tuple (risk, return) của optimal portfolio
            title: Chart title
            figsize: Figure size
            save_path: Save path
        """
        plt.figure(figsize=figsize)
        
        # Plot frontier
        plt.scatter(risks_list, returns_list, c=np.array(returns_list)/np.array(risks_list),
                   cmap='viridis', marker='o', s=50, alpha=0.6)
        plt.colorbar(label='Sharpe Ratio')
        
        # Plot optimal point
        if optimal_point is not None:
            plt.scatter(optimal_point[0], optimal_point[1],
                       marker='*', s=500, c='red', edgecolors='black',
                       label='Optimal Portfolio', zorder=5)
        
        plt.xlabel('Risk (Standard Deviation)')
        plt.ylabel('Expected Return')
        plt.title(title)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()


if __name__ == "__main__":
    # Example usage
    viz = PortfolioVisualizer()
    
    # Create sample data
    weights = pd.Series({
        'VNM': 0.25,
        'VIC': 0.20,
        'VHM': 0.15,
        'VCB': 0.25,
        'HPG': 0.15
    })
    
    # Plot allocation
    viz.plot_allocation(weights, title="Sample Portfolio Allocation")
    
    # Create sample returns
    dates = pd.date_range('2021-01-01', '2024-12-31', freq='D')
    returns = pd.Series(np.random.randn(len(dates)) * 0.02, index=dates)
    
    # Plot returns distribution
    viz.plot_returns_distribution(returns, title="Sample Returns Distribution")
