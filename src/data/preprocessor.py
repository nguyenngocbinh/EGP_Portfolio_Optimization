"""
Data Preprocessor Module

Module để xử lý, làm sạch và chuẩn bị dữ liệu cho phân tích.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from scipy import stats


class DataPreprocessor:
    """
    Class để xử lý và làm sạch dữ liệu thị trường
    """
    
    @staticmethod
    def remove_outliers(
        returns: pd.DataFrame,
        method: str = 'zscore',
        threshold: float = 3.0
    ) -> pd.DataFrame:
        """
        Loại bỏ outliers từ dữ liệu returns
        
        Args:
            returns: DataFrame chứa returns
            method: Phương pháp detect outliers ('zscore', 'iqr')
            threshold: Ngưỡng cho method (z-score > threshold hoặc IQR multiplier)
            
        Returns:
            DataFrame đã loại bỏ outliers (thay = NaN, sau đó fillna)
        """
        cleaned = returns.copy()
        
        if method == 'zscore':
            # Z-score method
            z_scores = np.abs(stats.zscore(cleaned, nan_policy='omit'))
            cleaned[z_scores > threshold] = np.nan
            
        elif method == 'iqr':
            # IQR method
            Q1 = cleaned.quantile(0.25)
            Q3 = cleaned.quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - threshold * IQR
            upper_bound = Q3 + threshold * IQR
            
            for col in cleaned.columns:
                cleaned.loc[
                    (cleaned[col] < lower_bound[col]) | 
                    (cleaned[col] > upper_bound[col]),
                    col
                ] = np.nan
        else:
            raise ValueError("Method must be 'zscore' or 'iqr'")
        
        # Forward fill NaN values
        cleaned = cleaned.ffill().bfill()
        
        return cleaned
    
    @staticmethod
    def check_data_quality(
        data: pd.DataFrame,
        min_observations: int = 252  # ~1 year daily data
    ) -> Dict[str, any]:
        """
        Kiểm tra chất lượng dữ liệu
        
        Args:
            data: DataFrame cần kiểm tra
            min_observations: Số observation tối thiểu yêu cầu
            
        Returns:
            Dict chứa thông tin chất lượng dữ liệu
        """
        quality_report = {
            'total_rows': len(data),
            'columns': list(data.columns),
            'missing_values': {},
            'zero_variance': [],
            'sufficient_data': {},
            'warnings': []
        }
        
        for col in data.columns:
            # Check missing values
            missing_count = data[col].isna().sum()
            missing_pct = (missing_count / len(data)) * 100
            quality_report['missing_values'][col] = {
                'count': int(missing_count),
                'percentage': round(missing_pct, 2)
            }
            
            if missing_pct > 10:
                quality_report['warnings'].append(
                    f"{col}: {missing_pct:.1f}% missing values"
                )
            
            # Check variance
            if data[col].var() == 0:
                quality_report['zero_variance'].append(col)
                quality_report['warnings'].append(
                    f"{col}: Zero variance (constant values)"
                )
            
            # Check sufficient observations
            valid_obs = data[col].notna().sum()
            quality_report['sufficient_data'][col] = valid_obs >= min_observations
            
            if valid_obs < min_observations:
                quality_report['warnings'].append(
                    f"{col}: Only {valid_obs} observations (min: {min_observations})"
                )
        
        return quality_report
    
    @staticmethod
    def filter_liquid_stocks(
        prices: pd.DataFrame,
        min_price: float = 1.0,
        min_trading_days: int = 200,
        min_price_variance: float = 0.0001
    ) -> List[str]:
        """
        Lọc các cổ phiếu thanh khoản đủ điều kiện
        
        Args:
            prices: DataFrame giá cổ phiếu
            min_price: Giá tối thiểu (loại penny stocks)
            min_trading_days: Số ngày giao dịch tối thiểu
            min_price_variance: Variance tối thiểu của giá
            
        Returns:
            List các symbol đạt tiêu chuẩn
        """
        valid_stocks = []
        
        for col in prices.columns:
            # Check minimum price
            if prices[col].mean() < min_price:
                continue
            
            # Check trading days
            trading_days = prices[col].notna().sum()
            if trading_days < min_trading_days:
                continue
            
            # Check price variance
            if prices[col].var() < min_price_variance:
                continue
            
            valid_stocks.append(col)
        
        return valid_stocks
    
    @staticmethod
    def align_data(
        stock_returns: pd.DataFrame,
        index_returns: pd.Series
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Căn chỉnh dữ liệu stock returns và index returns
        
        Args:
            stock_returns: DataFrame returns của cổ phiếu
            index_returns: Series returns của chỉ số
            
        Returns:
            Tuple (aligned_stock_returns, aligned_index_returns)
        """
        # Find common dates
        common_dates = stock_returns.index.intersection(index_returns.index)
        
        # Align
        aligned_stocks = stock_returns.loc[common_dates]
        aligned_index = index_returns.loc[common_dates]
        
        # Drop any remaining NaN rows
        valid_dates = aligned_stocks.notna().all(axis=1) & aligned_index.notna()
        
        return aligned_stocks[valid_dates], aligned_index[valid_dates]
    
    @staticmethod
    def winsorize_returns(
        returns: pd.DataFrame,
        lower_percentile: float = 0.01,
        upper_percentile: float = 0.99
    ) -> pd.DataFrame:
        """
        Winsorize returns (cap extreme values)
        
        Args:
            returns: DataFrame returns
            lower_percentile: Percentile thấp nhất (0-1)
            upper_percentile: Percentile cao nhất (0-1)
            
        Returns:
            DataFrame đã winsorize
        """
        winsorized = returns.copy()
        
        for col in winsorized.columns:
            lower = winsorized[col].quantile(lower_percentile)
            upper = winsorized[col].quantile(upper_percentile)
            
            winsorized[col] = winsorized[col].clip(lower=lower, upper=upper)
        
        return winsorized
    
    @staticmethod
    def normalize_returns(
        returns: pd.DataFrame,
        method: str = 'zscore'
    ) -> pd.DataFrame:
        """
        Normalize returns
        
        Args:
            returns: DataFrame returns
            method: Phương pháp normalize ('zscore', 'minmax')
            
        Returns:
            DataFrame đã normalize
        """
        if method == 'zscore':
            # Z-score normalization
            normalized = (returns - returns.mean()) / returns.std()
        elif method == 'minmax':
            # Min-max normalization
            normalized = (returns - returns.min()) / (returns.max() - returns.min())
        else:
            raise ValueError("Method must be 'zscore' or 'minmax'")
        
        return normalized


if __name__ == "__main__":
    # Example usage
    import sys
    sys.path.append('.')
    from src.data.data_loader import VNDataLoader
    
    # Load data
    loader = VNDataLoader(start_date='2021-01-01', end_date='2024-12-31')
    test_symbols = ['VNM', 'VIC', 'VHM', 'VCB', 'HPG']
    data = loader.get_data_bundle(test_symbols)
    
    # Test preprocessor
    preprocessor = DataPreprocessor()
    
    # Check quality
    print("=== Data Quality Report ===")
    quality = preprocessor.check_data_quality(data['stock_returns'])
    print(f"Total rows: {quality['total_rows']}")
    print(f"Warnings: {len(quality['warnings'])}")
    for warning in quality['warnings']:
        print(f"  - {warning}")
    
    # Remove outliers
    print("\n=== Removing Outliers ===")
    cleaned = preprocessor.remove_outliers(data['stock_returns'], method='zscore', threshold=3)
    print(f"Original shape: {data['stock_returns'].shape}")
    print(f"Cleaned shape: {cleaned.shape}")
    
    # Filter liquid stocks
    print("\n=== Filtering Liquid Stocks ===")
    liquid = preprocessor.filter_liquid_stocks(data['stock_prices'])
    print(f"Liquid stocks: {liquid}")
