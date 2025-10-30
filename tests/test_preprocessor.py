"""
Unit tests for Data Preprocessor
"""

import pytest
import pandas as pd
import numpy as np
from src.data.preprocessor import DataPreprocessor


class TestDataPreprocessor:
    """Test cases for DataPreprocessor class"""
    
    @pytest.fixture
    def sample_returns(self):
        """Create sample returns data with outliers"""
        np.random.seed(42)
        n_periods = 100
        
        returns = pd.DataFrame({
            'STOCK_A': np.random.randn(n_periods) * 0.02,
            'STOCK_B': np.random.randn(n_periods) * 0.02,
            'STOCK_C': np.random.randn(n_periods) * 0.02
        }, index=pd.date_range('2023-01-01', periods=n_periods, freq='D'))
        
        # Add some outliers
        returns.iloc[10, 0] = 0.15  # Large positive
        returns.iloc[20, 1] = -0.12  # Large negative
        
        return returns
    
    @pytest.fixture
    def sample_prices(self):
        """Create sample price data"""
        np.random.seed(42)
        n_periods = 100
        
        prices = pd.DataFrame({
            'STOCK_A': 100 * np.exp(np.cumsum(np.random.randn(n_periods) * 0.02)),
            'STOCK_B': 50 * np.exp(np.cumsum(np.random.randn(n_periods) * 0.02)),
            'STOCK_C': 200 * np.exp(np.cumsum(np.random.randn(n_periods) * 0.02))
        }, index=pd.date_range('2023-01-01', periods=n_periods, freq='D'))
        
        return prices
    
    def test_remove_outliers_zscore(self, sample_returns):
        """Test outlier removal using z-score method"""
        preprocessor = DataPreprocessor()
        
        cleaned = preprocessor.remove_outliers(
            sample_returns,
            method='zscore',
            threshold=3.0
        )
        
        # Should return DataFrame of same shape
        assert cleaned.shape == sample_returns.shape
        
        # Outliers should be replaced
        assert cleaned.iloc[10, 0] != sample_returns.iloc[10, 0]
        assert cleaned.iloc[20, 1] != sample_returns.iloc[20, 1]
        
        # No NaN values after cleaning
        assert not cleaned.isna().any().any()
    
    def test_remove_outliers_iqr(self, sample_returns):
        """Test outlier removal using IQR method"""
        preprocessor = DataPreprocessor()
        
        cleaned = preprocessor.remove_outliers(
            sample_returns,
            method='iqr',
            threshold=1.5
        )
        
        # Should return DataFrame of same shape
        assert cleaned.shape == sample_returns.shape
        
        # No NaN values
        assert not cleaned.isna().any().any()
    
    def test_remove_outliers_invalid_method(self, sample_returns):
        """Test that invalid method raises error"""
        preprocessor = DataPreprocessor()
        
        with pytest.raises(ValueError, match="Method must be"):
            preprocessor.remove_outliers(sample_returns, method='invalid')
    
    def test_check_data_quality(self, sample_returns):
        """Test data quality checking"""
        preprocessor = DataPreprocessor()
        
        # Add some missing values
        returns_with_na = sample_returns.copy()
        returns_with_na.iloc[5:10, 0] = np.nan
        
        quality = preprocessor.check_data_quality(returns_with_na)
        
        # Check expected keys
        assert 'total_rows' in quality
        assert 'columns' in quality
        assert 'missing_values' in quality
        assert 'zero_variance' in quality
        assert 'warnings' in quality
        
        # Should detect missing values
        assert quality['missing_values']['STOCK_A']['count'] > 0
    
    def test_check_data_quality_zero_variance(self):
        """Test detection of zero variance"""
        preprocessor = DataPreprocessor()
        
        # Create data with constant column
        data = pd.DataFrame({
            'STOCK_A': [1.0] * 100,  # Constant
            'STOCK_B': np.random.randn(100)
        })
        
        quality = preprocessor.check_data_quality(data)
        
        # Should detect zero variance
        assert 'STOCK_A' in quality['zero_variance']
        assert len(quality['warnings']) > 0
    
    def test_filter_liquid_stocks(self, sample_prices):
        """Test filtering of liquid stocks"""
        preprocessor = DataPreprocessor()
        
        # Add a penny stock
        prices_with_penny = sample_prices.copy()
        prices_with_penny['PENNY'] = 0.5  # Low price
        
        liquid_stocks = preprocessor.filter_liquid_stocks(
            prices_with_penny,
            min_price=1.0,
            min_trading_days=50
        )
        
        # Penny stock should be filtered out
        assert 'PENNY' not in liquid_stocks
        assert 'STOCK_A' in liquid_stocks
    
    def test_filter_liquid_stocks_insufficient_data(self, sample_prices):
        """Test filtering with insufficient trading days"""
        preprocessor = DataPreprocessor()
        
        # Add stock with lots of missing values
        prices_with_gaps = sample_prices.copy()
        prices_with_gaps['GAPPED'] = np.nan
        prices_with_gaps.iloc[:10, -1] = 100  # Only 10 valid values
        
        liquid_stocks = preprocessor.filter_liquid_stocks(
            prices_with_gaps,
            min_trading_days=50
        )
        
        # Gapped stock should be filtered
        assert 'GAPPED' not in liquid_stocks
    
    def test_align_data(self):
        """Test data alignment"""
        preprocessor = DataPreprocessor()
        
        # Create misaligned data
        dates1 = pd.date_range('2023-01-01', periods=100, freq='D')
        dates2 = pd.date_range('2023-01-05', periods=100, freq='D')
        
        stock_returns = pd.DataFrame({
            'STOCK_A': np.random.randn(100) * 0.02,
            'STOCK_B': np.random.randn(100) * 0.02
        }, index=dates1)
        
        index_returns = pd.Series(
            np.random.randn(100) * 0.02,
            index=dates2
        )
        
        aligned_stocks, aligned_index = preprocessor.align_data(
            stock_returns, index_returns
        )
        
        # Should have same index
        assert all(aligned_stocks.index == aligned_index.index)
        
        # Should be shorter than originals
        assert len(aligned_stocks) < len(stock_returns)
        assert len(aligned_index) < len(index_returns)
    
    def test_winsorize_returns(self, sample_returns):
        """Test winsorization"""
        preprocessor = DataPreprocessor()
        
        winsorized = preprocessor.winsorize_returns(
            sample_returns,
            lower_percentile=0.05,
            upper_percentile=0.95
        )
        
        # Shape should be preserved
        assert winsorized.shape == sample_returns.shape
        
        # Extreme values should be clipped
        for col in winsorized.columns:
            assert winsorized[col].max() <= sample_returns[col].quantile(0.95)
            assert winsorized[col].min() >= sample_returns[col].quantile(0.05)
    
    def test_normalize_returns_zscore(self, sample_returns):
        """Test z-score normalization"""
        preprocessor = DataPreprocessor()
        
        normalized = preprocessor.normalize_returns(
            sample_returns,
            method='zscore'
        )
        
        # Mean should be close to 0, std close to 1
        for col in normalized.columns:
            assert abs(normalized[col].mean()) < 1e-10
            assert abs(normalized[col].std() - 1.0) < 1e-10
    
    def test_normalize_returns_minmax(self, sample_returns):
        """Test min-max normalization"""
        preprocessor = DataPreprocessor()
        
        normalized = preprocessor.normalize_returns(
            sample_returns,
            method='minmax'
        )
        
        # Values should be in [0, 1]
        for col in normalized.columns:
            assert normalized[col].min() >= -1e-10
            assert normalized[col].max() <= 1.0 + 1e-10
    
    def test_normalize_returns_invalid_method(self, sample_returns):
        """Test that invalid normalization method raises error"""
        preprocessor = DataPreprocessor()
        
        with pytest.raises(ValueError, match="Method must be"):
            preprocessor.normalize_returns(sample_returns, method='invalid')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
