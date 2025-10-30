"""
Data Loader Module

Module để tải dữ liệu giá cổ phiếu và chỉ số thị trường từ VNDirect
sử dụng vnstock3 library.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional, Union, Dict
import warnings

try:
    from vnstock3 import Vnstock
except ImportError:
    warnings.warn("vnstock3 not installed. Please install: pip install vnstock3")
    Vnstock = None


class VNDataLoader:
    """
    Class để tải và xử lý dữ liệu từ thị trường chứng khoán Việt Nam
    
    Attributes:
        stock: Vnstock instance để tương tác với API
        start_date: Ngày bắt đầu lấy dữ liệu
        end_date: Ngày kết thúc lấy dữ liệu
        frequency: Tần suất dữ liệu ('D', 'W', 'M')
    """
    
    def __init__(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        frequency: str = 'D'
    ):
        """
        Khởi tạo VNDataLoader
        
        Args:
            start_date: Ngày bắt đầu (format: 'YYYY-MM-DD'). 
                       Mặc định: 3 năm trước
            end_date: Ngày kết thúc (format: 'YYYY-MM-DD'). 
                     Mặc định: hôm nay
            frequency: Tần suất dữ liệu ('D', 'W', 'M')
                      D = Daily, W = Weekly, M = Monthly
        """
        if Vnstock is None:
            raise ImportError(
                "vnstock3 is required. Install it with: pip install vnstock3"
            )
        
        self.stock = Vnstock().stock(symbol='VN30', source='VCI')
        
        # Set default dates
        if end_date is None:
            self.end_date = datetime.now().strftime('%Y-%m-%d')
        else:
            self.end_date = end_date
            
        if start_date is None:
            # Default: 3 years ago
            start = datetime.now() - timedelta(days=3*365)
            self.start_date = start.strftime('%Y-%m-%d')
        else:
            self.start_date = start_date
            
        self.frequency = frequency.upper()
        
        if self.frequency not in ['D', 'W', 'M']:
            raise ValueError("Frequency must be 'D' (Daily), 'W' (Weekly), or 'M' (Monthly)")
    
    def get_stock_prices(
        self, 
        symbols: Union[str, List[str]],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Lấy dữ liệu giá đóng cửa điều chỉnh của các cổ phiếu
        
        Args:
            symbols: Mã cổ phiếu hoặc danh sách mã cổ phiếu
            start_date: Ngày bắt đầu (override default)
            end_date: Ngày kết thúc (override default)
            
        Returns:
            DataFrame với columns là symbols, index là date, values là adjusted close price
        """
        if isinstance(symbols, str):
            symbols = [symbols]
            
        start = start_date or self.start_date
        end = end_date or self.end_date
        
        prices_dict = {}
        failed_symbols = []
        
        for symbol in symbols:
            try:
                # Get stock data
                stock = Vnstock().stock(symbol=symbol, source='VCI')
                df = stock.quote.history(
                    start=start,
                    end=end,
                    interval='1D'
                )
                
                if df is not None and len(df) > 0:
                    # Use close price (adjusted if available)
                    if 'close' in df.columns:
                        prices_dict[symbol] = df['close']
                    else:
                        print(f"Warning: No 'close' column for {symbol}")
                        failed_symbols.append(symbol)
                else:
                    failed_symbols.append(symbol)
                    
            except Exception as e:
                print(f"Error loading {symbol}: {str(e)}")
                failed_symbols.append(symbol)
        
        if not prices_dict:
            raise ValueError("Could not load any stock data")
            
        if failed_symbols:
            print(f"Failed to load: {', '.join(failed_symbols)}")
        
        # Combine into DataFrame
        prices_df = pd.DataFrame(prices_dict)
        prices_df.index = pd.to_datetime(prices_df.index)
        prices_df = prices_df.sort_index()
        
        # Resample if needed
        if self.frequency == 'W':
            prices_df = prices_df.resample('W').last()
        elif self.frequency == 'M':
            prices_df = prices_df.resample('M').last()
        
        # Forward fill missing values
        prices_df = prices_df.fillna(method='ffill')
        
        return prices_df
    
    def get_market_index(
        self,
        index_symbol: str = 'VNINDEX',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.Series:
        """
        Lấy dữ liệu chỉ số thị trường
        
        Args:
            index_symbol: Mã chỉ số ('VNINDEX', 'VN30', 'HNX', etc.)
            start_date: Ngày bắt đầu (override default)
            end_date: Ngày kết thúc (override default)
            
        Returns:
            Series với index là date, values là index close price
        """
        start = start_date or self.start_date
        end = end_date or self.end_date
        
        try:
            # Get index data
            stock = Vnstock().stock(symbol=index_symbol, source='VCI')
            df = stock.quote.history(
                start=start,
                end=end,
                interval='1D'
            )
            
            if df is None or len(df) == 0:
                raise ValueError(f"No data returned for index {index_symbol}")
            
            # Use close price
            index_series = df['close']
            index_series.index = pd.to_datetime(index_series.index)
            index_series = index_series.sort_index()
            
            # Resample if needed
            if self.frequency == 'W':
                index_series = index_series.resample('W').last()
            elif self.frequency == 'M':
                index_series = index_series.resample('M').last()
            
            # Forward fill
            index_series = index_series.fillna(method='ffill')
            
            return index_series
            
        except Exception as e:
            raise ValueError(f"Error loading market index {index_symbol}: {str(e)}")
    
    def calculate_returns(
        self, 
        prices: Union[pd.DataFrame, pd.Series],
        method: str = 'simple'
    ) -> Union[pd.DataFrame, pd.Series]:
        """
        Tính lợi tức từ giá
        
        Args:
            prices: DataFrame hoặc Series chứa giá
            method: Phương pháp tính ('simple' hoặc 'log')
                   simple: R_t = (P_t - P_{t-1}) / P_{t-1}
                   log: R_t = ln(P_t / P_{t-1})
                   
        Returns:
            Returns DataFrame/Series (bỏ hàng đầu tiên)
        """
        if method == 'simple':
            returns = prices.pct_change()
        elif method == 'log':
            returns = np.log(prices / prices.shift(1))
        else:
            raise ValueError("Method must be 'simple' or 'log'")
        
        # Drop first row (NaN)
        returns = returns.dropna()
        
        return returns
    
    def get_data_bundle(
        self,
        stock_symbols: List[str],
        index_symbol: str = 'VNINDEX',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        return_method: str = 'simple'
    ) -> Dict[str, pd.DataFrame]:
        """
        Lấy bundle dữ liệu hoàn chỉnh cho phân tích
        
        Args:
            stock_symbols: Danh sách mã cổ phiếu
            index_symbol: Mã chỉ số thị trường
            start_date: Ngày bắt đầu
            end_date: Ngày kết thúc
            return_method: Phương pháp tính lợi tức
            
        Returns:
            Dict chứa:
                - 'stock_prices': DataFrame giá cổ phiếu
                - 'stock_returns': DataFrame lợi tức cổ phiếu
                - 'index_prices': Series giá chỉ số
                - 'index_returns': Series lợi tức chỉ số
        """
        print(f"Loading data from {start_date or self.start_date} to {end_date or self.end_date}")
        print(f"Frequency: {self.frequency}")
        
        # Get stock prices
        print(f"\nLoading {len(stock_symbols)} stocks...")
        stock_prices = self.get_stock_prices(
            stock_symbols, 
            start_date, 
            end_date
        )
        
        # Get market index
        print(f"Loading market index: {index_symbol}...")
        index_prices = self.get_market_index(
            index_symbol,
            start_date,
            end_date
        )
        
        # Align dates (intersection of dates)
        common_dates = stock_prices.index.intersection(index_prices.index)
        stock_prices = stock_prices.loc[common_dates]
        index_prices = index_prices.loc[common_dates]
        
        print(f"\nData loaded: {len(common_dates)} periods")
        print(f"Date range: {common_dates[0]} to {common_dates[-1]}")
        
        # Calculate returns
        stock_returns = self.calculate_returns(stock_prices, return_method)
        index_returns = self.calculate_returns(index_prices, return_method)
        
        # Align returns
        common_return_dates = stock_returns.index.intersection(index_returns.index)
        stock_returns = stock_returns.loc[common_return_dates]
        index_returns = index_returns.loc[common_return_dates]
        
        return {
            'stock_prices': stock_prices,
            'stock_returns': stock_returns,
            'index_prices': index_prices,
            'index_returns': index_returns,
            'symbols': list(stock_prices.columns),
            'index_symbol': index_symbol,
            'frequency': self.frequency,
            'start_date': str(common_dates[0].date()),
            'end_date': str(common_dates[-1].date())
        }


if __name__ == "__main__":
    # Example usage
    loader = VNDataLoader(
        start_date='2021-01-01',
        end_date='2024-12-31',
        frequency='D'
    )
    
    # Test with VN30 stocks
    test_symbols = ['VNM', 'VIC', 'VHM', 'VCB', 'HPG']
    
    data = loader.get_data_bundle(
        stock_symbols=test_symbols,
        index_symbol='VNINDEX'
    )
    
    print("\n=== Data Summary ===")
    print(f"Stocks: {data['symbols']}")
    print(f"Index: {data['index_symbol']}")
    print(f"Returns shape: {data['stock_returns'].shape}")
    print(f"\nFirst few returns:")
    print(data['stock_returns'].head())
