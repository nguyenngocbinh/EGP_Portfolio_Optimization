"""
Unit tests for EGP Optimizer
"""

import pytest
import pandas as pd
import numpy as np
from src.models.egp_optimizer import EGPOptimizer


class TestEGPOptimizer:
    """Test cases for EGPOptimizer class"""
    
    @pytest.fixture
    def sample_parameters(self):
        """Create sample parameters for optimization"""
        symbols = ['STOCK_A', 'STOCK_B', 'STOCK_C', 'STOCK_D']
        
        expected_returns = pd.Series({
            'STOCK_A': 0.0003,  # 30 bps daily
            'STOCK_B': 0.0002,
            'STOCK_C': 0.0004,
            'STOCK_D': 0.0001
        })
        
        betas = pd.Series({
            'STOCK_A': 1.2,
            'STOCK_B': 0.8,
            'STOCK_C': 1.5,
            'STOCK_D': 0.6
        })
        
        residual_vars = pd.Series({
            'STOCK_A': 0.0001,
            'STOCK_B': 0.00015,
            'STOCK_C': 0.00012,
            'STOCK_D': 0.0002
        })
        
        market_var = 0.0004
        risk_free_rate = 0.00002  # ~5% annual / 252
        
        return expected_returns, betas, residual_vars, market_var, risk_free_rate
    
    def test_initialization(self, sample_parameters):
        """Test optimizer initialization"""
        exp_ret, betas, res_vars, mkt_var, rf = sample_parameters
        
        egp = EGPOptimizer(
            expected_returns=exp_ret,
            betas=betas,
            residual_vars=res_vars,
            market_var=mkt_var,
            risk_free_rate=rf
        )
        
        assert egp.n_stocks == 4
        assert len(egp.symbols) == 4
        assert egp.market_var == mkt_var
        assert egp.risk_free_rate == rf
    
    def test_invalid_input_types(self, sample_parameters):
        """Test that invalid inputs raise errors"""
        exp_ret, betas, res_vars, mkt_var, rf = sample_parameters
        
        # Test with non-Series input
        with pytest.raises(TypeError):
            EGPOptimizer(
                expected_returns=[0.1, 0.2],  # Should be Series
                betas=betas,
                residual_vars=res_vars,
                market_var=mkt_var,
                risk_free_rate=rf
            )
    
    def test_zero_variance_error(self, sample_parameters):
        """Test that zero residual variance raises error"""
        exp_ret, betas, res_vars, mkt_var, rf = sample_parameters
        
        # Set one residual variance to zero
        res_vars_bad = res_vars.copy()
        res_vars_bad['STOCK_A'] = 0
        
        with pytest.raises(ValueError, match="Non-positive residual variance"):
            EGPOptimizer(
                expected_returns=exp_ret,
                betas=betas,
                residual_vars=res_vars_bad,
                market_var=mkt_var,
                risk_free_rate=rf
            )
    
    def test_zero_market_variance_error(self, sample_parameters):
        """Test that zero market variance raises error"""
        exp_ret, betas, res_vars, mkt_var, rf = sample_parameters
        
        with pytest.raises(ValueError, match="Market variance must be positive"):
            EGPOptimizer(
                expected_returns=exp_ret,
                betas=betas,
                residual_vars=res_vars,
                market_var=0,  # Invalid
                risk_free_rate=rf
            )
    
    def test_calculate_C0(self, sample_parameters):
        """Test C0 calculation"""
        exp_ret, betas, res_vars, mkt_var, rf = sample_parameters
        
        egp = EGPOptimizer(
            expected_returns=exp_ret,
            betas=betas,
            residual_vars=res_vars,
            market_var=mkt_var,
            risk_free_rate=rf
        )
        
        C0 = egp.calculate_C0()
        
        # C0 should be a finite number
        assert isinstance(C0, (int, float))
        assert np.isfinite(C0)
        
        # C0 should be stored
        assert egp.C0 == C0
    
    def test_calculate_Z_values(self, sample_parameters):
        """Test Z values calculation"""
        exp_ret, betas, res_vars, mkt_var, rf = sample_parameters
        
        egp = EGPOptimizer(
            expected_returns=exp_ret,
            betas=betas,
            residual_vars=res_vars,
            market_var=mkt_var,
            risk_free_rate=rf
        )
        
        Z_values = egp.calculate_Z_values()
        
        # Should return a Series
        assert isinstance(Z_values, pd.Series)
        assert len(Z_values) == 4
        
        # All values should be finite
        assert all(np.isfinite(Z_values))
        
        # Z values should be stored
        assert egp.Z_values is not None
    
    def test_optimize_no_constraints(self, sample_parameters):
        """Test optimization without constraints"""
        exp_ret, betas, res_vars, mkt_var, rf = sample_parameters
        
        egp = EGPOptimizer(
            expected_returns=exp_ret,
            betas=betas,
            residual_vars=res_vars,
            market_var=mkt_var,
            risk_free_rate=rf
        )
        
        weights = egp.optimize(allow_short=True)
        
        # Weights should sum to approximately 1
        assert abs(weights.abs().sum() - 1.0) < 1e-6
        
        # All weights should be finite
        assert all(np.isfinite(weights))
    
    def test_optimize_no_short(self, sample_parameters):
        """Test optimization with no short selling"""
        exp_ret, betas, res_vars, mkt_var, rf = sample_parameters
        
        egp = EGPOptimizer(
            expected_returns=exp_ret,
            betas=betas,
            residual_vars=res_vars,
            market_var=mkt_var,
            risk_free_rate=rf
        )
        
        weights = egp.optimize(allow_short=False)
        
        # All weights should be non-negative
        assert all(weights >= -1e-10)  # Allow small numerical error
        
        # Weights should sum to 1
        assert abs(weights.sum() - 1.0) < 1e-6
    
    def test_optimize_with_max_weight(self, sample_parameters):
        """Test optimization with max weight constraint"""
        exp_ret, betas, res_vars, mkt_var, rf = sample_parameters
        
        egp = EGPOptimizer(
            expected_returns=exp_ret,
            betas=betas,
            residual_vars=res_vars,
            market_var=mkt_var,
            risk_free_rate=rf
        )
        
        max_weight = 0.30
        weights = egp.optimize(allow_short=False, max_weight=max_weight)
        
        # No weight should exceed max_weight (excluding NaN values)
        valid_weights = weights.dropna()
        assert all(valid_weights <= max_weight + 1e-6)  # Allow small numerical error
        
        # Weights should still sum to 1
        assert abs(weights.sum() - 1.0) < 1e-6
    
    def test_optimize_with_min_weight(self, sample_parameters):
        """Test optimization with min weight constraint"""
        exp_ret, betas, res_vars, mkt_var, rf = sample_parameters
        
        egp = EGPOptimizer(
            expected_returns=exp_ret,
            betas=betas,
            residual_vars=res_vars,
            market_var=mkt_var,
            risk_free_rate=rf
        )
        
        min_weight = 0.05
        weights = egp.optimize(allow_short=False, min_weight=min_weight)
        
        # Non-zero weights should meet minimum
        non_zero = weights[weights > 1e-6]
        if len(non_zero) > 0:
            assert all(non_zero >= min_weight - 1e-6)
    
    def test_get_portfolio_statistics(self, sample_parameters):
        """Test portfolio statistics calculation"""
        exp_ret, betas, res_vars, mkt_var, rf = sample_parameters
        
        egp = EGPOptimizer(
            expected_returns=exp_ret,
            betas=betas,
            residual_vars=res_vars,
            market_var=mkt_var,
            risk_free_rate=rf
        )
        
        weights = egp.optimize(allow_short=False)
        stats = egp.get_portfolio_statistics()
        
        # Check expected keys
        assert 'portfolio_return' in stats
        assert 'portfolio_variance' in stats
        assert 'portfolio_std' in stats
        assert 'sharpe_ratio' in stats
        assert 'n_stocks' in stats
        
        # Check values are valid
        assert stats['portfolio_variance'] >= 0
        assert stats['portfolio_std'] >= 0
        assert np.isfinite(stats['sharpe_ratio'])
    
    def test_get_portfolio_statistics_before_optimize(self, sample_parameters):
        """Test that getting stats before optimization raises error"""
        exp_ret, betas, res_vars, mkt_var, rf = sample_parameters
        
        egp = EGPOptimizer(
            expected_returns=exp_ret,
            betas=betas,
            residual_vars=res_vars,
            market_var=mkt_var,
            risk_free_rate=rf
        )
        
        with pytest.raises(ValueError):
            egp.get_portfolio_statistics()
    
    def test_get_top_holdings(self, sample_parameters):
        """Test top holdings retrieval"""
        exp_ret, betas, res_vars, mkt_var, rf = sample_parameters
        
        egp = EGPOptimizer(
            expected_returns=exp_ret,
            betas=betas,
            residual_vars=res_vars,
            market_var=mkt_var,
            risk_free_rate=rf
        )
        
        weights = egp.optimize(allow_short=False)
        top_holdings = egp.get_top_holdings(n=2)
        
        # Should return DataFrame
        assert isinstance(top_holdings, pd.DataFrame)
        assert len(top_holdings) <= 2
        
        # Should have expected columns
        assert 'weight' in top_holdings.columns
        assert 'expected_return' in top_holdings.columns
        assert 'beta' in top_holdings.columns
    
    def test_all_negative_Z_values(self):
        """Test handling when all Z values are negative"""
        # Create scenario where all stocks are unattractive
        symbols = ['STOCK_A', 'STOCK_B']
        
        expected_returns = pd.Series({
            'STOCK_A': 0.00001,  # Very low returns
            'STOCK_B': 0.00001
        })
        
        betas = pd.Series({'STOCK_A': 1.0, 'STOCK_B': 1.0})
        residual_vars = pd.Series({'STOCK_A': 0.0001, 'STOCK_B': 0.0001})
        market_var = 0.0004
        risk_free_rate = 0.0001  # High risk-free rate
        
        egp = EGPOptimizer(
            expected_returns=expected_returns,
            betas=betas,
            residual_vars=residual_vars,
            market_var=market_var,
            risk_free_rate=risk_free_rate
        )
        
        # Should handle gracefully with warning
        with pytest.warns(UserWarning):
            weights = egp.optimize(allow_short=False)
        
        # Should return equal weights as fallback
        assert abs(weights.sum() - 1.0) < 1e-6


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
