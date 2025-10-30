# User Guide - EGP Portfolio Optimization

## Hướng dẫn sử dụng cho người dùng

Tài liệu này hướng dẫn cách sử dụng hệ thống EGP Portfolio Optimization cho mục đích thực tế.

---

## Mục lục

1. [Cài đặt](#1-cài-đặt)
2. [Cấu hình](#2-cấu-hình)
3. [Quy trình cơ bản](#3-quy-trình-cơ-bản)
4. [Use Cases](#4-use-cases)
5. [Best Practices](#5-best-practices)
6. [Troubleshooting](#6-troubleshooting)

---

## 1. Cài đặt

### Bước 1: Clone repository

```bash
git clone <repository-url>
cd EGP_Portfolio_Optimization
```

### Bước 2: Tạo virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Bước 3: Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### Bước 4: Verify installation

```bash
python -c "import vnstock3; print('vnstock3 OK')"
python -c "import pandas; print('pandas OK')"
python -c "import numpy; print('numpy OK')"
```

---

## 2. Cấu hình

### File .env

Copy `.env.example` thành `.env` và chỉnh sửa:

```env
# Market Configuration
DEFAULT_MARKET_INDEX=VNINDEX
DEFAULT_RISK_FREE_RATE=0.05  # 5% annual

# Data Configuration
DEFAULT_START_DATE=2021-01-01
DEFAULT_END_DATE=2024-12-31
DEFAULT_FREQUENCY=D  # D=Daily, W=Weekly, M=Monthly

# Portfolio Constraints
ALLOW_SHORT_SELLING=False
MAX_POSITION_SIZE=0.30  # 30% max per stock
MIN_POSITION_SIZE=0.01  # 1% min if invested

# Backtesting
INITIAL_CAPITAL=1000000000  # 1 tỷ VND
REBALANCE_FREQUENCY=M  # M=Monthly, Q=Quarterly
TRANSACTION_COST=0.0015  # 0.15%
```

---

## 3. Quy trình cơ bản

### Bước 1: Chuẩn bị danh sách cổ phiếu

Tạo file `my_stocks.txt`:
```
VNM
VIC
VHM
VCB
HPG
MSN
MWG
FPT
```

Hoặc trong Python:
```python
stocks = ['VNM', 'VIC', 'VHM', 'VCB', 'HPG', 'MSN', 'MWG', 'FPT']
```

### Bước 2: Load dữ liệu

```python
from src.data.data_loader import VNDataLoader

loader = VNDataLoader(
    start_date='2021-01-01',
    end_date='2024-12-31',
    frequency='D'
)

data = loader.get_data_bundle(
    stock_symbols=stocks,
    index_symbol='VNINDEX'
)
```

### Bước 3: Fit model và optimize

```python
from src.models.single_index_model import SingleIndexModel
from src.models.egp_optimizer import EGPOptimizer

# Fit Single-Index Model
sim = SingleIndexModel(data['stock_returns'], data['index_returns'])
sim.fit()

# Optimize portfolio
egp = EGPOptimizer(
    expected_returns=sim.get_expected_returns(),
    betas=sim.get_all_betas(),
    residual_vars=sim.get_all_residual_vars(),
    market_var=sim.market_var,
    risk_free_rate=0.05/252
)

weights = egp.optimize(allow_short=False, max_weight=0.30)
```

### Bước 4: Xem kết quả

```python
# Portfolio weights
print("Portfolio Allocation:")
print(weights.sort_values(ascending=False))

# Statistics
stats = egp.get_portfolio_statistics()
print(f"\nExpected Return (annual): {stats['portfolio_return']*252:.2%}")
print(f"Volatility (annual): {stats['portfolio_std']*np.sqrt(252):.2%}")
print(f"Sharpe Ratio: {stats['sharpe_ratio']*np.sqrt(252):.4f}")
```

### Bước 5: Visualize

```python
from src.visualization.plots import PortfolioVisualizer

viz = PortfolioVisualizer()
viz.plot_allocation(weights, title="My Portfolio")
```

---

## 4. Use Cases

### Use Case 1: Monthly Portfolio Rebalancing

**Mục tiêu:** Tự động rebalance portfolio hàng tháng

```python
from src.analysis.backtesting import Backtester

# Setup backtester
backtester = Backtester(
    data=data,
    initial_capital=1_000_000_000,
    rebalance_frequency='M',
    transaction_cost=0.0015,
    risk_free_rate=0.05
)

# Run backtest
results = backtester.run(
    lookback_periods=252,  # Use 1 year of data
    optimizer_params={'allow_short': False, 'max_weight': 0.30},
    benchmark=True
)

# View results
print(f"Total Return: {results['metrics']['total_return']:.2%}")
print(f"Sharpe Ratio: {results['metrics']['sharpe_ratio']:.4f}")
```

### Use Case 2: Compare Different Strategies

```python
strategies = {
    'Aggressive (Max 50%)': {'max_weight': 0.50},
    'Balanced (Max 30%)': {'max_weight': 0.30},
    'Conservative (Max 20%)': {'max_weight': 0.20}
}

for name, params in strategies.items():
    egp = EGPOptimizer(...)
    weights = egp.optimize(allow_short=False, **params)
    stats = egp.get_portfolio_statistics()
    
    print(f"\n{name}")
    print(f"  Sharpe: {stats['sharpe_ratio']*np.sqrt(252):.4f}")
    print(f"  Stocks: {stats['n_stocks']}")
```

### Use Case 3: Sector-based Portfolio

```python
# Define sectors
tech_stocks = ['FPT', 'VGI', 'CMG']
banking_stocks = ['VCB', 'BID', 'CTG', 'TCB']
consumer_stocks = ['VNM', 'MSN', 'MWG']

# Optimize for each sector
sectors = {
    'Tech': tech_stocks,
    'Banking': banking_stocks,
    'Consumer': consumer_stocks
}

sector_portfolios = {}
for sector_name, sector_stocks in sectors.items():
    # Load data for this sector
    sector_data = loader.get_data_bundle(sector_stocks)
    
    # Optimize
    sim = SingleIndexModel(sector_data['stock_returns'], sector_data['index_returns'])
    sim.fit()
    
    egp = EGPOptimizer(...)
    weights = egp.optimize(...)
    
    sector_portfolios[sector_name] = weights
```

### Use Case 4: Risk-based Allocation

```python
# Low risk: focus on low beta stocks
low_beta_stocks = sim.get_all_betas().nsmallest(10).index

# High beta: aggressive growth
high_beta_stocks = sim.get_all_betas().nlargest(10).index

# Optimize each
# ...
```

---

## 5. Best Practices

### 5.1. Data Quality

✅ **Kiểm tra dữ liệu trước khi optimize**

```python
from src.data.preprocessor import DataPreprocessor

preprocessor = DataPreprocessor()

# Check quality
quality = preprocessor.check_data_quality(data['stock_returns'])
print(f"Warnings: {quality['warnings']}")

# Clean outliers
cleaned_returns = preprocessor.remove_outliers(
    data['stock_returns'],
    method='zscore',
    threshold=3
)
```

✅ **Filter liquid stocks**

```python
liquid_stocks = preprocessor.filter_liquid_stocks(
    data['stock_prices'],
    min_price=1000,  # VND
    min_trading_days=200
)
```

### 5.2. Parameter Selection

✅ **Estimation window**

- Minimum: 30 observations
- Recommended: 252 observations (1 year daily data)
- Maximum: 1260 observations (5 years)

✅ **Risk-free rate**

Nguồn tham khảo:
- TPCP 1 năm: ~4-6% (2024)
- Lãi suất tiết kiệm: ~5-7%
- Conservative: 5%

✅ **Rebalancing frequency**

| Frequency | Pros | Cons |
|-----------|------|------|
| Monthly | Responsive | High costs |
| Quarterly | Balanced | Moderate costs |
| Semi-annual | Low costs | Slow to adapt |

### 5.3. Constraints

✅ **Max weight guidelines**

| Strategy | Max Weight | Min Weight |
|----------|-----------|-----------|
| Conservative | 15-20% | 3-5% |
| Balanced | 25-30% | 1-3% |
| Aggressive | 40-50% | 0% |

✅ **Diversification**

- Minimum 5 stocks
- Recommended: 10-20 stocks
- Too many (>30): diminishing benefits

### 5.4. Monitoring

✅ **Theo dõi metrics**

```python
# Calculate rolling Sharpe
rolling_sharpe = portfolio_returns.rolling(60).mean() / \
                 portfolio_returns.rolling(60).std() * np.sqrt(252)

# Alert if Sharpe drops below threshold
if rolling_sharpe.iloc[-1] < 0.5:
    print("WARNING: Low Sharpe ratio detected!")
```

✅ **Rebalance triggers**

```python
# Check drift from target
current_weights = calculate_current_weights(portfolio, prices)
drift = abs(current_weights - target_weights).sum()

if drift > 0.10:  # 10% total drift
    print("Rebalancing needed!")
    rebalance(portfolio, target_weights)
```

---

## 6. Troubleshooting

### Problem 1: "No data returned for stock XXX"

**Causes:**
- Stock delisted
- Data unavailable in vnstock3
- Network issues

**Solutions:**
```python
# Skip failed stocks
try:
    data = loader.get_data_bundle(stocks)
except Exception as e:
    print(f"Error: {e}")
    # Remove failed stocks and retry
```

### Problem 2: "All Z values are zero"

**Causes:**
- Expected returns too low
- C₀ too high
- Risk-free rate too high

**Solutions:**
```python
# Check parameters
print(f"C0: {egp.C0}")
print(f"Expected returns:\n{expected_returns}")
print(f"Risk-free rate: {risk_free_rate}")

# Try lower risk-free rate
egp = EGPOptimizer(..., risk_free_rate=0.0)
```

### Problem 3: Extreme concentration

**Cause:** One stock dominates

**Solution:**
```python
# Apply strict max weight
weights = egp.optimize(allow_short=False, max_weight=0.20)

# Or manually cap
weights = weights.clip(upper=0.20)
weights = weights / weights.sum()
```

### Problem 4: Poor backtesting performance

**Causes:**
- Overfitting
- Look-ahead bias
- High transaction costs

**Solutions:**
```python
# Increase lookback period
backtester.run(lookback_periods=756)  # 3 years

# Reduce rebalance frequency
backtester = Backtester(..., rebalance_frequency='Q')

# Account for realistic costs
backtester = Backtester(..., transaction_cost=0.003)  # 0.3%
```

---

## Appendix: Quick Reference

### Import cheatsheet

```python
# Data
from src.data.data_loader import VNDataLoader
from src.data.preprocessor import DataPreprocessor

# Models
from src.models.single_index_model import SingleIndexModel
from src.models.egp_optimizer import EGPOptimizer
from src.models.portfolio import Portfolio

# Analysis
from src.analysis.backtesting import Backtester

# Visualization
from src.visualization.plots import PortfolioVisualizer
```

### Common parameters

```python
# VNDataLoader
loader = VNDataLoader(
    start_date='2021-01-01',
    end_date='2024-12-31',
    frequency='D'  # 'D', 'W', 'M'
)

# EGPOptimizer
egp = EGPOptimizer(
    expected_returns=...,
    betas=...,
    residual_vars=...,
    market_var=...,
    risk_free_rate=0.05/252
)

weights = egp.optimize(
    allow_short=False,
    max_weight=0.30,
    min_weight=0.01
)

# Backtester
backtester = Backtester(
    data=...,
    initial_capital=1_000_000_000,
    rebalance_frequency='M',
    transaction_cost=0.0015,
    risk_free_rate=0.05
)
```

---

*User Guide - EGP Portfolio Optimization v1.0*
