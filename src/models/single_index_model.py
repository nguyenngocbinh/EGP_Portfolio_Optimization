"""
Single-Index Model Module

Implement Single-Index Model để ước lượng:
- Beta (β_i): hệ số hồi quy với market index
- Alpha (α_i): phần return không giải thích được bởi market
- Residual Variance (σ²_εi): variance của phần dư
- Market Variance (σ²_m): variance của market index

Model: R_i = α_i + β_i * R_m + ε_i
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
from scipy import stats
import warnings


class SingleIndexModel:
    """
    Single-Index Model để phân tích quan hệ giữa cổ phiếu và thị trường
    
    Attributes:
        stock_returns: DataFrame returns của các cổ phiếu
        market_returns: Series returns của chỉ số thị trường
        results: Dict chứa kết quả ước lượng cho mỗi cổ phiếu
    """
    
    def __init__(
        self,
        stock_returns: pd.DataFrame,
        market_returns: pd.Series
    ):
        """
        Khởi tạo Single-Index Model
        
        Args:
            stock_returns: DataFrame với columns là symbols, returns của cổ phiếu
            market_returns: Series returns của market index
        """
        # Validate input
        if not isinstance(stock_returns, pd.DataFrame):
            raise TypeError("stock_returns must be a pandas DataFrame")
        
        if not isinstance(market_returns, pd.Series):
            raise TypeError("market_returns must be a pandas Series")
        
        # Align data
        common_dates = stock_returns.index.intersection(market_returns.index)
        
        if len(common_dates) < 30:
            warnings.warn(
                f"Only {len(common_dates)} common dates. "
                "Results may be unreliable with < 30 observations."
            )
        
        self.stock_returns = stock_returns.loc[common_dates].copy()
        self.market_returns = market_returns.loc[common_dates].copy()
        
        # Drop any NaN
        valid_idx = self.market_returns.notna()
        self.stock_returns = self.stock_returns[valid_idx]
        self.market_returns = self.market_returns[valid_idx]
        
        self.symbols = list(self.stock_returns.columns)
        self.results = {}
        
        # Market statistics
        self.market_var = None
        self.market_mean = None
    
    def fit(self) -> Dict[str, Dict[str, float]]:
        """
        Fit Single-Index Model cho tất cả cổ phiếu
        
        Sử dụng OLS regression: R_i = α_i + β_i * R_m + ε_i
        
        Returns:
            Dict với key là symbol, value là dict chứa:
                - alpha: Intercept
                - beta: Slope (market sensitivity)
                - residual_var: Variance của phần dư (σ²_εi)
                - r_squared: R² của regression
                - std_error_beta: Standard error của beta
                - t_stat_beta: t-statistic của beta
                - p_value_beta: p-value của beta
        """
        # Calculate market statistics
        self.market_mean = self.market_returns.mean()
        self.market_var = self.market_returns.var()
        
        print(f"Fitting Single-Index Model for {len(self.symbols)} stocks...")
        print(f"Market variance: {self.market_var:.6f}")
        print(f"Market mean return: {self.market_mean:.6f}\n")
        
        for symbol in self.symbols:
            # Get stock returns
            y = self.stock_returns[symbol].values
            x = self.market_returns.values
            
            # Remove any NaN pairs
            mask = ~(np.isnan(y) | np.isnan(x))
            y = y[mask]
            x = x[mask]
            
            if len(y) < 10:
                warnings.warn(f"Skipping {symbol}: insufficient data ({len(y)} obs)")
                continue
            
            # OLS regression using scipy
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            
            # Calculate residuals
            y_pred = intercept + slope * x
            residuals = y - y_pred
            
            # Residual variance (unbiased estimator)
            n = len(y)
            residual_var = np.sum(residuals ** 2) / (n - 2)  # n-2 for OLS with 2 params
            
            # Standard error of beta
            # SE(β) = sqrt(σ²_ε / Σ(x_i - x̄)²)
            x_mean = np.mean(x)
            sum_sq_x = np.sum((x - x_mean) ** 2)
            std_error_beta = np.sqrt(residual_var / sum_sq_x)
            
            # t-statistic for beta
            t_stat_beta = slope / std_error_beta if std_error_beta > 0 else 0
            
            # Store results
            self.results[symbol] = {
                'alpha': intercept,
                'beta': slope,
                'residual_var': residual_var,
                'r_squared': r_value ** 2,
                'std_error_beta': std_error_beta,
                't_stat_beta': t_stat_beta,
                'p_value_beta': p_value,
                'n_observations': n
            }
        
        print(f"Successfully fitted {len(self.results)} stocks")
        return self.results
    
    def get_parameters(self, symbol: str) -> Dict[str, float]:
        """
        Lấy parameters của một cổ phiếu cụ thể
        
        Args:
            symbol: Mã cổ phiếu
            
        Returns:
            Dict chứa parameters
        """
        if symbol not in self.results:
            raise ValueError(f"Symbol {symbol} not found in results. Run fit() first.")
        
        return self.results[symbol]
    
    def get_all_betas(self) -> pd.Series:
        """
        Lấy beta của tất cả cổ phiếu
        
        Returns:
            Series với index là symbols, values là beta
        """
        if not self.results:
            raise ValueError("No results available. Run fit() first.")
        
        betas = {symbol: params['beta'] for symbol, params in self.results.items()}
        return pd.Series(betas)
    
    def get_all_alphas(self) -> pd.Series:
        """
        Lấy alpha của tất cả cổ phiếu
        
        Returns:
            Series với index là symbols, values là alpha
        """
        if not self.results:
            raise ValueError("No results available. Run fit() first.")
        
        alphas = {symbol: params['alpha'] for symbol, params in self.results.items()}
        return pd.Series(alphas)
    
    def get_all_residual_vars(self) -> pd.Series:
        """
        Lấy residual variance của tất cả cổ phiếu
        
        Returns:
            Series với index là symbols, values là σ²_εi
        """
        if not self.results:
            raise ValueError("No results available. Run fit() first.")
        
        res_vars = {
            symbol: params['residual_var'] 
            for symbol, params in self.results.items()
        }
        return pd.Series(res_vars)
    
    def get_expected_returns(self, risk_free_rate: float = 0.0) -> pd.Series:
        """
        Tính expected return cho mỗi cổ phiếu
        
        E[R_i] = α_i + β_i * E[R_m]
        
        Args:
            risk_free_rate: Lãi suất phi rủi ro (annualized)
                          Nếu = 0, sử dụng historical mean của market
            
        Returns:
            Series expected returns
        """
        if not self.results:
            raise ValueError("No results available. Run fit() first.")
        
        # Use historical market mean if risk_free_rate not provided
        market_premium = self.market_mean
        
        expected_returns = {}
        for symbol, params in self.results.items():
            # E[R_i] = α_i + β_i * E[R_m]
            expected_returns[symbol] = params['alpha'] + params['beta'] * market_premium
        
        return pd.Series(expected_returns)
    
    def get_total_variance(self) -> pd.Series:
        """
        Tính total variance cho mỗi cổ phiếu
        
        Var(R_i) = β_i² * σ²_m + σ²_εi
        
        Returns:
            Series total variances
        """
        if not self.results:
            raise ValueError("No results available. Run fit() first.")
        
        if self.market_var is None:
            raise ValueError("Market variance not calculated. Run fit() first.")
        
        total_vars = {}
        for symbol, params in self.results.items():
            # Var(R_i) = β² * Var(R_m) + Var(ε_i)
            systematic_var = (params['beta'] ** 2) * self.market_var
            total_vars[symbol] = systematic_var + params['residual_var']
        
        return pd.Series(total_vars)
    
    def summary(self, sort_by: str = 'beta') -> pd.DataFrame:
        """
        Tạo summary DataFrame của tất cả cổ phiếu
        
        Args:
            sort_by: Column để sort ('beta', 'alpha', 'r_squared')
            
        Returns:
            DataFrame summary
        """
        if not self.results:
            raise ValueError("No results available. Run fit() first.")
        
        summary_data = []
        for symbol, params in self.results.items():
            summary_data.append({
                'symbol': symbol,
                'alpha': params['alpha'],
                'beta': params['beta'],
                'residual_var': params['residual_var'],
                'r_squared': params['r_squared'],
                'std_error_beta': params['std_error_beta'],
                't_stat_beta': params['t_stat_beta'],
                'p_value_beta': params['p_value_beta'],
                'n_obs': params['n_observations']
            })
        
        df = pd.DataFrame(summary_data)
        df = df.set_index('symbol')
        
        if sort_by in df.columns:
            df = df.sort_values(by=sort_by, ascending=False)
        
        return df


if __name__ == "__main__":
    # Example usage
    import sys
    sys.path.append('.')
    from src.data.data_loader import VNDataLoader
    
    # Load data
    print("=== Loading Data ===")
    loader = VNDataLoader(start_date='2021-01-01', end_date='2024-12-31')
    test_symbols = ['VNM', 'VIC', 'VHM', 'VCB', 'HPG', 'MSN', 'MWG', 'FPT']
    
    data = loader.get_data_bundle(test_symbols, index_symbol='VNINDEX')
    
    # Fit Single-Index Model
    print("\n=== Fitting Single-Index Model ===")
    sim = SingleIndexModel(
        stock_returns=data['stock_returns'],
        market_returns=data['index_returns']
    )
    
    results = sim.fit()
    
    # Show summary
    print("\n=== Model Summary ===")
    summary = sim.summary(sort_by='beta')
    print(summary.round(4))
    
    # Expected returns
    print("\n=== Expected Returns ===")
    exp_returns = sim.get_expected_returns()
    print(exp_returns.round(6))
    
    # Total variance
    print("\n=== Total Variance ===")
    total_var = sim.get_total_variance()
    print(total_var.round(6))
