"""
EGP Optimizer Module

Implement thuật toán Elton-Gruber-Padberg để tối ưu hóa portfolio
dựa trên Single-Index Model.

Thuật toán:
1. Tính C₀ = σ²_m * S / (1 + σ²_m * B)
   với S = Σ[(R̄ᵢ - Rf) * βᵢ / σ²_εi]
   và  B = Σ[β²ᵢ / σ²_εi]

2. Tính Zᵢ = (R̄ᵢ - Rf)/σ²_εi - (βᵢ/σ²_εi) * C₀

3. Normalize Zᵢ thành weights wᵢ

Tham khảo: Elton, Gruber & Padberg (1976, 1978)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import warnings


class EGPOptimizer:
    """
    EGP Portfolio Optimizer
    
    Tối ưu hóa danh mục để maximize Sharpe ratio sử dụng
    Single-Index Model và ranking procedure.
    
    Attributes:
        expected_returns: Expected returns của mỗi cổ phiếu (R̄ᵢ)
        betas: Beta coefficients (βᵢ)
        residual_vars: Residual variances (σ²_εi)
        market_var: Market variance (σ²_m)
        risk_free_rate: Risk-free rate (Rf)
    """
    
    def __init__(
        self,
        expected_returns: pd.Series,
        betas: pd.Series,
        residual_vars: pd.Series,
        market_var: float,
        risk_free_rate: float = 0.0
    ):
        """
        Khởi tạo EGP Optimizer
        
        Args:
            expected_returns: Series expected returns (R̄ᵢ)
            betas: Series beta coefficients (βᵢ)
            residual_vars: Series residual variances (σ²_εi)
            market_var: Market variance (σ²_m)
            risk_free_rate: Risk-free rate (Rf), default = 0
        """
        # Validate inputs
        if not all(isinstance(x, pd.Series) for x in [expected_returns, betas, residual_vars]):
            raise TypeError("expected_returns, betas, residual_vars must be pandas Series")
        
        # Align all series
        common_symbols = expected_returns.index.intersection(betas.index).intersection(residual_vars.index)
        
        if len(common_symbols) == 0:
            raise ValueError("No common symbols found in inputs")
        
        self.expected_returns = expected_returns.loc[common_symbols].copy()
        self.betas = betas.loc[common_symbols].copy()
        self.residual_vars = residual_vars.loc[common_symbols].copy()
        
        self.market_var = market_var
        self.risk_free_rate = risk_free_rate
        
        self.symbols = list(common_symbols)
        self.n_stocks = len(self.symbols)
        
        # Results
        self.C0 = None
        self.Z_values = None
        self.weights = None
        
        # Validate non-zero variance
        if (self.residual_vars <= 0).any():
            bad_symbols = self.residual_vars[self.residual_vars <= 0].index.tolist()
            raise ValueError(f"Non-positive residual variance for: {bad_symbols}")
        
        if self.market_var <= 0:
            raise ValueError("Market variance must be positive")
    
    def calculate_C0(self) -> float:
        """
        Tính hằng số C₀ theo công thức EGP
        
        C₀ = σ²_m * S / (1 + σ²_m * B)
        
        với:
        S = Σ[(R̄ᵢ - Rf) * βᵢ / σ²_εi]
        B = Σ[β²ᵢ / σ²_εi]
        
        Returns:
            Giá trị C₀
        """
        # Calculate excess returns
        excess_returns = self.expected_returns - self.risk_free_rate
        
        # Calculate S = Σ[(R̄ᵢ - Rf) * βᵢ / σ²_εi]
        S = np.sum((excess_returns * self.betas) / self.residual_vars)
        
        # Calculate B = Σ[β²ᵢ / σ²_εi]
        B = np.sum((self.betas ** 2) / self.residual_vars)
        
        # Calculate C₀
        denominator = 1 + self.market_var * B
        
        if denominator == 0:
            raise ValueError("Denominator is zero in C0 calculation")
        
        C0 = (self.market_var * S) / denominator
        
        self.C0 = C0
        return C0
    
    def calculate_Z_values(self) -> pd.Series:
        """
        Tính Z_i cho mỗi cổ phiếu
        
        Z_i = (R̄ᵢ - Rf)/σ²_εi - (βᵢ/σ²_εi) * C₀
        
        hoặc viết lại:
        Z_i = (βᵢ/σ²_εi) * [(R̄ᵢ - Rf)/βᵢ - C₀]
        
        Returns:
            Series Z values cho mỗi symbol
        """
        if self.C0 is None:
            self.calculate_C0()
        
        # Calculate excess returns
        excess_returns = self.expected_returns - self.risk_free_rate
        
        # Z_i = (R̄ᵢ - Rf)/σ²_εi - (βᵢ/σ²_εi) * C₀
        Z_values = (excess_returns / self.residual_vars) - \
                   (self.betas / self.residual_vars) * self.C0
        
        self.Z_values = Z_values
        return Z_values
    
    def optimize(
        self,
        allow_short: bool = False,
        max_weight: Optional[float] = None,
        min_weight: Optional[float] = None
    ) -> pd.Series:
        """
        Tối ưu hóa portfolio và tính weights
        
        Args:
            allow_short: Cho phép bán khống (Z_i < 0)
            max_weight: Tỷ trọng tối đa cho mỗi cổ phiếu (0-1)
            min_weight: Tỷ trọng tối thiểu cho mỗi cổ phiếu (0-1)
            
        Returns:
            Series weights (normalized to sum = 1)
        """
        # Calculate Z values
        Z_values = self.calculate_Z_values()
        
        # Apply constraints
        if not allow_short:
            # Only keep positive Z values
            Z_values = Z_values.clip(lower=0)
        
        # Check if we have any non-zero weights
        if Z_values.abs().sum() == 0:
            warnings.warn(
                "All Z values are zero. Returning equal weights."
            )
            weights = pd.Series(1.0 / self.n_stocks, index=self.symbols)
            self.weights = weights
            return weights
        
        # Normalize to get weights (proportional allocation)
        # w_i = Z_i / Σ|Z_j|
        total_abs_z = Z_values.abs().sum()
        weights = Z_values / total_abs_z
        
        # Apply weight constraints
        if max_weight is not None or min_weight is not None:
            weights = self._apply_weight_constraints(
                weights, 
                max_weight, 
                min_weight,
                allow_short
            )
        
        # Final normalization
        weights = weights / weights.abs().sum()
        
        self.weights = weights
        return weights
    
    def _apply_weight_constraints(
        self,
        weights: pd.Series,
        max_weight: Optional[float],
        min_weight: Optional[float],
        allow_short: bool
    ) -> pd.Series:
        """
        Áp dụng ràng buộc về tỷ trọng
        
        Iterative approach: clip weights vượt bound, 
        phân bổ lại phần dư cho các stock còn lại
        
        Args:
            weights: Initial weights
            max_weight: Maximum weight per stock
            min_weight: Minimum weight per stock
            allow_short: Allow negative weights
            
        Returns:
            Adjusted weights
        """
        adjusted_weights = weights.copy()
        max_iterations = 100
        
        for iteration in range(max_iterations):
            modified = False
            
            # Apply max constraint
            if max_weight is not None:
                over_max = adjusted_weights > max_weight
                if over_max.any():
                    excess = (adjusted_weights[over_max] - max_weight).sum()
                    adjusted_weights[over_max] = max_weight
                    
                    # Redistribute excess to unconstrained stocks
                    free_stocks = ~over_max & (adjusted_weights < max_weight)
                    if free_stocks.any():
                        adjusted_weights[free_stocks] += \
                            excess * (adjusted_weights[free_stocks] / adjusted_weights[free_stocks].sum())
                    
                    modified = True
            
            # Apply min constraint
            if min_weight is not None and not allow_short:
                under_min = (adjusted_weights > 0) & (adjusted_weights < min_weight)
                if under_min.any():
                    deficit = (min_weight - adjusted_weights[under_min]).sum()
                    adjusted_weights[under_min] = min_weight
                    
                    # Remove deficit from larger positions
                    free_stocks = ~under_min & (adjusted_weights > min_weight)
                    if free_stocks.any():
                        adjusted_weights[free_stocks] -= \
                            deficit * (adjusted_weights[free_stocks] / adjusted_weights[free_stocks].sum())
                    
                    modified = True
            
            if not modified:
                break
        
        return adjusted_weights
    
    def get_portfolio_statistics(self) -> Dict[str, float]:
        """
        Tính các chỉ số thống kê của portfolio tối ưu
        
        Returns:
            Dict chứa:
                - portfolio_return: Expected return của portfolio
                - portfolio_variance: Variance của portfolio
                - portfolio_std: Standard deviation của portfolio
                - sharpe_ratio: Sharpe ratio
                - n_stocks: Số cổ phiếu có weight > 0
        """
        if self.weights is None:
            raise ValueError("Weights not calculated. Run optimize() first.")
        
        # Portfolio expected return
        portfolio_return = (self.weights * self.expected_returns).sum()
        
        # Portfolio variance using Single-Index Model
        # Var(Rp) = βp² * σ²_m + Σ(w²ᵢ * σ²_εi)
        portfolio_beta = (self.weights * self.betas).sum()
        systematic_var = (portfolio_beta ** 2) * self.market_var
        
        idiosyncratic_var = ((self.weights ** 2) * self.residual_vars).sum()
        
        portfolio_variance = systematic_var + idiosyncratic_var
        portfolio_std = np.sqrt(portfolio_variance)
        
        # Sharpe ratio
        excess_return = portfolio_return - self.risk_free_rate
        sharpe_ratio = excess_return / portfolio_std if portfolio_std > 0 else 0
        
        # Number of stocks with non-zero weight
        n_stocks_invested = (self.weights.abs() > 1e-6).sum()
        
        return {
            'portfolio_return': portfolio_return,
            'portfolio_variance': portfolio_variance,
            'portfolio_std': portfolio_std,
            'portfolio_beta': portfolio_beta,
            'sharpe_ratio': sharpe_ratio,
            'n_stocks': n_stocks_invested,
            'C0': self.C0
        }
    
    def get_top_holdings(self, n: int = 10) -> pd.DataFrame:
        """
        Lấy top N holdings theo tỷ trọng
        
        Args:
            n: Số lượng holdings muốn xem
            
        Returns:
            DataFrame với symbol, weight, expected_return, beta
        """
        if self.weights is None:
            raise ValueError("Weights not calculated. Run optimize() first.")
        
        # Sort by absolute weight
        sorted_weights = self.weights.abs().sort_values(ascending=False)
        top_symbols = sorted_weights.head(n).index
        
        holdings = pd.DataFrame({
            'weight': self.weights[top_symbols],
            'expected_return': self.expected_returns[top_symbols],
            'beta': self.betas[top_symbols],
            'residual_var': self.residual_vars[top_symbols],
            'Z_value': self.Z_values[top_symbols] if self.Z_values is not None else np.nan
        })
        
        return holdings


if __name__ == "__main__":
    # Example usage
    import sys
    sys.path.append('.')
    from src.data.data_loader import VNDataLoader
    from src.models.single_index_model import SingleIndexModel
    
    # Load data
    print("=== Loading Data ===")
    loader = VNDataLoader(start_date='2021-01-01', end_date='2024-12-31')
    test_symbols = ['VNM', 'VIC', 'VHM', 'VCB', 'HPG', 'MSN', 'MWG', 'FPT', 'GAS', 'TCB']
    
    data = loader.get_data_bundle(test_symbols, index_symbol='VNINDEX')
    
    # Fit Single-Index Model
    print("\n=== Fitting Single-Index Model ===")
    sim = SingleIndexModel(
        stock_returns=data['stock_returns'],
        market_returns=data['index_returns']
    )
    sim.fit()
    
    # Get parameters for EGP
    expected_returns = sim.get_expected_returns()
    betas = sim.get_all_betas()
    residual_vars = sim.get_all_residual_vars()
    market_var = sim.market_var
    
    # Run EGP Optimization
    print("\n=== Running EGP Optimization ===")
    egp = EGPOptimizer(
        expected_returns=expected_returns,
        betas=betas,
        residual_vars=residual_vars,
        market_var=market_var,
        risk_free_rate=0.05 / 252  # 5% annual, convert to daily
    )
    
    # Optimize (no short selling, max 30% per stock)
    weights = egp.optimize(allow_short=False, max_weight=0.30)
    
    print("\n=== Portfolio Weights ===")
    print(weights.sort_values(ascending=False).round(4))
    
    # Portfolio statistics
    print("\n=== Portfolio Statistics ===")
    stats = egp.get_portfolio_statistics()
    for key, value in stats.items():
        print(f"{key}: {value:.6f}")
    
    # Top holdings
    print("\n=== Top Holdings ===")
    top_holdings = egp.get_top_holdings(n=5)
    print(top_holdings.round(4))
