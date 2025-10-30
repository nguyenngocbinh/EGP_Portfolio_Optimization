"""
Unit tests for Single-Index Model
"""

import pytest
import pandas as pd
import numpy as np
from src.models.single_index_model import SingleIndexModel


class TestSingleIndexModel:
    """Test cases for SingleIndexModel class"""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample stock and market returns data"""
        np.random.seed(42)
        n_periods = 252  # 1 year of daily data
        
        # Generate market returns
        market_returns = pd.Series(
            np.random.randn(n_periods) * 0.02,
            index=pd.date_range('2023-01-01', periods=n_periods, freq='D'),
            name='market'
        )
        
        # Generate stock returns (correlated with market)
        stock_returns = pd.DataFrame()
        for i, symbol in enumerate(['STOCK_A', 'STOCK_B', 'STOCK_C']):
            beta = 0.8 + i * 0.2  # Different betas
            alpha = 0.0001
            residual = np.random.randn(n_periods) * 0.01
            
            stock_returns[symbol] = alpha + beta * market_returns + residual
        
        stock_returns.index = market_returns.index
        
        return stock_returns, market_returns
    
    def test_initialization(self, sample_data):
        """Test model initialization"""
        stock_returns, market_returns = sample_data
        
        sim = SingleIndexModel(stock_returns, market_returns)
        
        assert sim.symbols == ['STOCK_A', 'STOCK_B', 'STOCK_C']
        assert len(sim.stock_returns) == len(market_returns)
        assert sim.results == {}
    
    def test_invalid_input_types(self):
        """Test that invalid input types raise errors"""
        with pytest.raises(TypeError):
            SingleIndexModel("not a dataframe", pd.Series([1, 2, 3]))
        
        with pytest.raises(TypeError):
            SingleIndexModel(pd.DataFrame({'A': [1, 2, 3]}), "not a series")
    
    def test_fit_model(self, sample_data):
        """Test model fitting"""
        stock_returns, market_returns = sample_data
        
        sim = SingleIndexModel(stock_returns, market_returns)
        results = sim.fit()
        
        # Check that all stocks were fitted
        assert len(results) == 3
        assert 'STOCK_A' in results
        assert 'STOCK_B' in results
        assert 'STOCK_C' in results
        
        # Check that results contain expected keys
        for symbol, params in results.items():
            assert 'alpha' in params
            assert 'beta' in params
            assert 'residual_var' in params
            assert 'r_squared' in params
            assert 'n_observations' in params
    
    def test_beta_estimates(self, sample_data):
        """Test that beta estimates are reasonable"""
        stock_returns, market_returns = sample_data
        
        sim = SingleIndexModel(stock_returns, market_returns)
        sim.fit()
        
        betas = sim.get_all_betas()
        
        # Betas should be roughly in expected range (we generated with 0.8, 1.0, 1.2)
        assert all(betas > 0.5)
        assert all(betas < 1.5)
        assert betas['STOCK_A'] < betas['STOCK_C']  # STOCK_C has higher beta
    
    def test_market_variance(self, sample_data):
        """Test market variance calculation"""
        stock_returns, market_returns = sample_data
        
        sim = SingleIndexModel(stock_returns, market_returns)
        sim.fit()
        
        # Market variance should be positive
        assert sim.market_var > 0
        
        # Should be close to variance of market returns
        expected_var = market_returns.var()
        assert abs(sim.market_var - expected_var) < 1e-10
    
    def test_get_parameters(self, sample_data):
        """Test getting parameters for specific stock"""
        stock_returns, market_returns = sample_data
        
        sim = SingleIndexModel(stock_returns, market_returns)
        sim.fit()
        
        params_a = sim.get_parameters('STOCK_A')
        
        assert 'beta' in params_a
        assert 'alpha' in params_a
        assert isinstance(params_a['beta'], (int, float))
    
    def test_get_parameters_not_fitted(self, sample_data):
        """Test that getting parameters before fitting raises error"""
        stock_returns, market_returns = sample_data
        
        sim = SingleIndexModel(stock_returns, market_returns)
        
        with pytest.raises(ValueError):
            sim.get_parameters('STOCK_A')
    
    def test_expected_returns(self, sample_data):
        """Test expected returns calculation"""
        stock_returns, market_returns = sample_data
        
        sim = SingleIndexModel(stock_returns, market_returns)
        sim.fit()
        
        exp_returns = sim.get_expected_returns()
        
        # Should return a Series
        assert isinstance(exp_returns, pd.Series)
        assert len(exp_returns) == 3
        
        # All values should be finite
        assert all(np.isfinite(exp_returns))
    
    def test_total_variance(self, sample_data):
        """Test total variance calculation"""
        stock_returns, market_returns = sample_data
        
        sim = SingleIndexModel(stock_returns, market_returns)
        sim.fit()
        
        total_vars = sim.get_total_variance()
        
        # All variances should be positive
        assert all(total_vars > 0)
        
        # Total variance should be beta^2 * market_var + residual_var
        for symbol in sim.symbols:
            params = sim.results[symbol]
            expected = params['beta']**2 * sim.market_var + params['residual_var']
            assert abs(total_vars[symbol] - expected) < 1e-10
    
    def test_summary(self, sample_data):
        """Test summary DataFrame generation"""
        stock_returns, market_returns = sample_data
        
        sim = SingleIndexModel(stock_returns, market_returns)
        sim.fit()
        
        summary = sim.summary(sort_by='beta')
        
        # Should return DataFrame
        assert isinstance(summary, pd.DataFrame)
        assert len(summary) == 3
        
        # Should be sorted by beta
        betas = summary['beta'].values
        assert all(betas[i] >= betas[i+1] for i in range(len(betas)-1))
    
    def test_insufficient_data_warning(self):
        """Test warning with insufficient data"""
        # Create very small dataset
        stock_returns = pd.DataFrame({
            'STOCK_A': [0.01, 0.02, -0.01]
        }, index=pd.date_range('2023-01-01', periods=3, freq='D'))
        
        market_returns = pd.Series(
            [0.01, -0.01, 0.005],
            index=stock_returns.index
        )
        
        with pytest.warns(UserWarning):
            sim = SingleIndexModel(stock_returns, market_returns)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
