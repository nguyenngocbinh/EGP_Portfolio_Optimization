# EGP Portfolio Optimization

Hệ thống tối ưu hóa danh mục đầu tư sử dụng thuật toán **Elton-Gruber-Padberg (EGP)** với **Single-Index Model** cho thị trường chứng khoán Việt Nam.

## 📖 Mô tả

Project này implement thuật toán EGP để tối ưu hóa danh mục đầu tư nhằm **maximize Sharpe ratio** dựa trên Single-Index Model. Đây là phương pháp hiệu quả để xây dựng portfolio tối ưu mà không cần tính toán ma trận hiệp phương sai đầy đủ.

### Ưu điểm của EGP
✅ **Hiệu quả tính toán**: Không cần ma trận hiệp phương sai N×N  
✅ **Closed-form solution**: Có công thức đóng, không cần QP solver  
✅ **Dễ implement**: Code đơn giản, dễ hiểu  
✅ **Ranking procedure**: Xếp hạng cổ phiếu theo tiềm năng  

### Công thức chính

**Single-Index Model:**
```
R_i = α_i + β_i * R_m + ε_i
```

**EGP Algorithm:**
```
C₀ = σ²_m * Σ[(R̄ᵢ - Rf) * βᵢ / σ²_εi] / [1 + σ²_m * Σ(β²ᵢ / σ²_εi)]

Z_i = (R̄ᵢ - Rf)/σ²_εi - (βᵢ/σ²_εi) * C₀

w_i = Z_i / Σ|Z_j|
```

## 🚀 Cài đặt

### Yêu cầu hệ thống
- Python >= 3.8
- pip hoặc conda

### Cài đặt dependencies

```bash
# Clone repository
git clone <repository-url>
cd EGP_Portfolio_Optimization

# Tạo virtual environment (khuyến nghị)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate  # Windows

# Cài đặt packages
pip install -r requirements.txt
```

### Cấu hình

1. Copy file `.env.example` thành `.env`:
```bash
cp .env.example .env
```

2. Chỉnh sửa `.env` với cấu hình của bạn:
```env
DEFAULT_MARKET_INDEX=VNINDEX
DEFAULT_RISK_FREE_RATE=0.05
DEFAULT_START_DATE=2021-01-01
DEFAULT_END_DATE=2024-12-31
```

## 📊 Sử dụng nhanh

### Example 1: Portfolio Optimization cơ bản

```python
from src.data.data_loader import VNDataLoader
from src.models.single_index_model import SingleIndexModel
from src.models.egp_optimizer import EGPOptimizer

# 1. Load dữ liệu
loader = VNDataLoader(start_date='2021-01-01', end_date='2024-12-31')
stocks = ['VNM', 'VIC', 'VHM', 'VCB', 'HPG', 'MSN', 'MWG', 'FPT']

data = loader.get_data_bundle(
    stock_symbols=stocks,
    index_symbol='VNINDEX'
)

# 2. Fit Single-Index Model
sim = SingleIndexModel(
    stock_returns=data['stock_returns'],
    market_returns=data['index_returns']
)
sim.fit()

# 3. Optimize portfolio với EGP
egp = EGPOptimizer(
    expected_returns=sim.get_expected_returns(),
    betas=sim.get_all_betas(),
    residual_vars=sim.get_all_residual_vars(),
    market_var=sim.market_var,
    risk_free_rate=0.05 / 252  # 5% năm
)

# Tối ưu hóa (không bán khống, max 30% mỗi mã)
weights = egp.optimize(allow_short=False, max_weight=0.30)

print("Portfolio Weights:")
print(weights.sort_values(ascending=False))

# Xem statistics
stats = egp.get_portfolio_statistics()
print(f"\nSharpe Ratio: {stats['sharpe_ratio']:.4f}")
print(f"Expected Return: {stats['portfolio_return']:.4f}")
print(f"Portfolio Std: {stats['portfolio_std']:.4f}")
```

### Example 2: Backtesting

```python
from src.analysis.backtesting import Backtester

backtester = Backtester(
    data=data,
    initial_capital=1_000_000_000,  # 1 tỷ VND
    rebalance_frequency='M',  # Monthly
    transaction_cost=0.0015
)

results = backtester.run(
    optimizer_params={
        'allow_short': False,
        'max_weight': 0.30
    }
)

print(f"Total Return: {results['total_return']:.2%}")
print(f"Annualized Return: {results['annualized_return']:.2%}")
print(f"Max Drawdown: {results['max_drawdown']:.2%}")
```

### Example 3: Visualization

```python
from src.visualization.plots import PortfolioVisualizer

viz = PortfolioVisualizer()

# Plot allocation
viz.plot_allocation(weights, title="EGP Portfolio Allocation")

# Plot performance
viz.plot_performance(
    portfolio_values=results['portfolio_values'],
    benchmark_values=results['benchmark_values']
)

# Plot efficient frontier
viz.plot_efficient_frontier(sim, egp)
```

## 📁 Cấu trúc Project

```
EGP_Portfolio_Optimization/
├── README.md                          # File này
├── requirements.txt                   # Dependencies
├── .env.example                       # Template cấu hình
│
├── docs/                              # Tài liệu
│   ├── mathematical_derivation.md    # Dẫn xuất toán học
│   ├── egp_algorithm.md              # Giải thích thuật toán
│   └── user_guide.md                 # Hướng dẫn sử dụng
│
├── src/                               # Source code
│   ├── data/                         # Data handling
│   │   ├── data_loader.py           # Load từ VNDirect
│   │   └── preprocessor.py          # Xử lý dữ liệu
│   │
│   ├── models/                       # Core models
│   │   ├── single_index_model.py    # Single-Index Model
│   │   ├── egp_optimizer.py         # EGP Algorithm
│   │   └── portfolio.py             # Portfolio management
│   │
│   ├── analysis/                     # Phân tích
│   │   ├── performance.py           # Performance metrics
│   │   └── backtesting.py           # Backtesting engine
│   │
│   └── visualization/                # Visualization
│       └── plots.py                 # Charts và graphs
│
├── examples/                          # Ví dụ
│   ├── 01_basic_optimization.py
│   ├── 02_with_constraints.py
│   ├── 03_backtesting.py
│   └── notebooks/                   # Jupyter tutorials
│       ├── tutorial_01_intro.ipynb
│       ├── tutorial_02_math.ipynb
│       └── tutorial_03_application.ipynb
│
├── tests/                             # Unit tests
│   ├── test_single_index_model.py
│   ├── test_egp_optimizer.py
│   └── test_backtesting.py
│
└── data/                              # Sample data
    └── sample_stocks.csv
```

## 🔬 Phương pháp luận

### Single-Index Model

Giả định rằng lợi tức của mỗi cổ phiếu được quyết định bởi:
- **Market factor** (β_i): Độ nhạy với thị trường
- **Idiosyncratic factor** (ε_i): Rủi ro riêng

```
R_i = α_i + β_i * R_m + ε_i

với:
- R_i: Return của stock i
- R_m: Return của market index
- β_i: Beta coefficient (market sensitivity)
- α_i: Alpha (excess return)
- ε_i: Residual (specific risk)
```

### EGP Algorithm

EGP sử dụng **ranking procedure** để tìm portfolio tối ưu:

1. **Tính C₀** (cutoff constant):
   - Phản ánh "tiêu chuẩn" để chọn cổ phiếu
   - Phụ thuộc vào toàn bộ universe

2. **Tính Z_i** cho mỗi stock:
   - Z_i > 0: Stock được chọn (long position)
   - Z_i < 0: Stock bị loại (hoặc short nếu cho phép)

3. **Normalize Z_i** thành weights

### Constraints

Project hỗ trợ các constraints:
- ❌ **No short selling**: Z_i >= 0
- 📊 **Max position**: w_i <= max_weight
- 📉 **Min position**: w_i >= min_weight (nếu > 0)

## 📈 Performance Metrics

Hệ thống tính các metrics sau:

| Metric | Mô tả |
|--------|-------|
| **Total Return** | Lợi nhuận tổng (%) |
| **Annualized Return** | Return trung bình hàng năm |
| **Volatility** | Độ biến động (annualized std) |
| **Sharpe Ratio** | Return/risk ratio |
| **Max Drawdown** | Sụt giảm tối đa từ peak |
| **Win Rate** | Tỷ lệ periods dương |

## 🧪 Testing

Chạy unit tests:

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test
pytest tests/test_egp_optimizer.py -v
```

## 📚 Tài liệu tham khảo

1. **Elton, E. J., Gruber, M. J., & Padberg, M. W.** (1976). Simple Criteria for Optimal Portfolio Selection. *The Journal of Finance*, 31(5), 1341-1357.

2. **Elton, E. J., Gruber, M. J., & Padberg, M. W.** (1978). Simple Criteria for Optimal Portfolio Selection: Tracing Out the Efficient Frontier. *The Journal of Finance*, 33(1), 296-302.

3. **Sharpe, W. F.** (1963). A Simplified Model for Portfolio Analysis. *Management Science*, 9(2), 277-293.

## ⚠️ Lưu ý quan trọng

1. **Dữ liệu lịch sử**: Kết quả dựa trên dữ liệu quá khứ, không đảm bảo hiệu suất tương lai

2. **Estimation error**: EGP nhạy với lỗi ước lượng của expected returns, betas

3. **Transaction costs**: Trong thực tế cần tính đến phí giao dịch, slippage

4. **Rebalancing**: Tần suất rebalance ảnh hưởng đến performance và costs

5. **Market assumptions**: Single-Index Model giả định market là nhân tố duy nhất

## 🤝 Đóng góp

Contributions are welcome! Please:
1. Fork repository
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Mở Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## 📧 Liên hệ

- **Email**: your.email@example.com
- **Issues**: [GitHub Issues](https://github.com/nguyenngocbinh/EGP_Portfolio_Optimization/issues)

## 🙏 Acknowledgments

- Elton, Gruber & Padberg for the original algorithm
- VNDirect for market data API
- vnstock3 library for data access

---

**Made with ❤️ for Vietnamese stock market**
