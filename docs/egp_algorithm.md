# Thuật Toán EGP - Hướng Dẫn Chi Tiết

## Giới thiệu

Thuật toán **Elton-Gruber-Padberg (EGP)** là phương pháp tối ưu hóa danh mục đầu tư để **maximize Sharpe ratio** sử dụng **Single-Index Model**. Đây là một trong những thuật toán kinh điển và hiệu quả nhất trong lý thuyết danh mục.

## Tại sao sử dụng EGP?

### Ưu điểm

1. **Hiệu quả tính toán**
   - Không cần tính ma trận hiệp phương sai đầy đủ (N×N)
   - Chỉ cần N regressions đơn giản (OLS)
   - Complexity: O(N) thay vì O(N²)

2. **Closed-form solution**
   - Có công thức đóng, không cần optimizer phức tạp
   - Không bị stuck ở local minimum
   - Tính toán deterministic và reproducible

3. **Dễ hiểu và implement**
   - Logic rõ ràng: xếp hạng cổ phiếu theo tiềm năng
   - Code đơn giản, ít bugs
   - Dễ debug và maintain

4. **Khả năng mở rộng**
   - Dễ thêm constraints (no short, max weight)
   - Có thể customize cho nhu cầu cụ thể
   - Phù hợp cho production systems

## Workflow tổng quan

```
[Dữ liệu giá]
      ↓
[1. Single-Index Model]
      ↓
[Ước lượng: β, α, σ²_ε, σ²_m]
      ↓
[2. Tính C₀ (cutoff constant)]
      ↓
[3. Tính Z_i cho mỗi stock]
      ↓
[4. Áp dụng constraints]
      ↓
[5. Normalize thành weights]
      ↓
[Portfolio tối ưu]
```

## Chi tiết từng bước

### Bước 1: Single-Index Model

**Mục đích:** Phân tách return thành market component và specific component.

**Model:**
```
R_i = α_i + β_i * R_m + ε_i
```

**Implementation:**
- Với mỗi cổ phiếu i, chạy OLS regression:
  ```
  Y = stock_returns[i]
  X = market_returns
  β_i = slope
  α_i = intercept
  ```

- Tính residual variance:
  ```
  residuals = Y - (α_i + β_i * X)
  σ²_εi = variance(residuals)
  ```

- Tính market variance:
  ```
  σ²_m = variance(market_returns)
  ```

**Output:**
- `betas`: Series of β_i values
- `alphas`: Series of α_i values
- `residual_vars`: Series of σ²_εi values
- `market_var`: Scalar σ²_m

### Bước 2: Tính Expected Returns

**Options:**

**Option A: Historical Mean (đơn giản)**
```python
expected_returns = stock_returns.mean()
```

**Option B: CAPM-based (theo lý thuyết)**
```python
expected_returns = alpha + beta * market_mean
```

**Option C: Forward-looking (advanced)**
```python
# Sử dụng analyst forecasts, ML models, etc.
```

### Bước 3: Tính C₀ (Cutoff Constant)

**Công thức:**

```
C₀ = (σ²_m * A) / (1 + σ²_m * B)
```

Trong đó:
```
A = Σ [(R̄ᵢ - Rf) * βᵢ / σ²_εi]
B = Σ [β²ᵢ / σ²_εi]
```

**Code:**
```python
excess_returns = expected_returns - risk_free_rate

# Tính A
A = sum((excess_returns * betas) / residual_vars)

# Tính B
B = sum((betas ** 2) / residual_vars)

# Tính C₀
C0 = (market_var * A) / (1 + market_var * B)
```

**Ý nghĩa:**
- C₀ là threshold để chọn cổ phiếu
- Phụ thuộc vào toàn bộ universe, không phải từng cổ phiếu riêng lẻ
- Cao hơn = tiêu chuẩn chọn lọc nghiêm ngặt hơn

### Bước 4: Tính Z_i Values

**Công thức:**

```
Z_i = (R̄ᵢ - Rf)/σ²_εi - (βᵢ/σ²_εi) * C₀
```

Hoặc viết lại:
```
Z_i = (βᵢ/σ²_εi) * [(R̄ᵢ - Rf)/βᵢ - C₀]
```

**Code:**
```python
Z_values = (excess_returns / residual_vars) - \
           (betas / residual_vars) * C0
```

**Ý nghĩa:**
- Z_i > 0: Stock được chọn (long position)
- Z_i < 0: Stock bị loại (hoặc short nếu cho phép)
- Magnitude của Z_i: mức độ quan trọng trong portfolio

**Ranking interpretation:**
```
Excess Return per Beta: (R̄ᵢ - Rf)/βᵢ
So sánh với C₀:
  - Nếu > C₀: Stock "đáng giá" → chọn
  - Nếu < C₀: Stock "không đáng giá" → loại
```

### Bước 5: Áp dụng Constraints

**Constraint 1: No Short Selling**
```python
if not allow_short:
    Z_values = Z_values.clip(lower=0)
```

**Constraint 2: Max Weight per Stock**
```python
# Iterative adjustment
while any violations:
    # Cap stocks exceeding max_weight
    Z_values[Z_values > max_weight * total_Z] = max_weight * total_Z
    
    # Redistribute excess to other stocks
    excess = calculate_excess()
    Z_values[unconstrained] += redistribute(excess)
```

**Constraint 3: Min Weight**
```python
# Similar iterative approach
# Ensure non-zero holdings meet minimum
```

### Bước 6: Normalize thành Weights

**Công thức:**
```
w_i = Z_i / Σ|Z_j|
```

**Code:**
```python
weights = Z_values / Z_values.abs().sum()
```

**Validation:**
```python
assert abs(weights.sum() - 1.0) < 1e-6  # Sum to 1
assert all(weights >= 0) if not allow_short  # Non-negative
assert all(weights <= max_weight) if max_weight  # Max constraint
```

## Portfolio Statistics

### Expected Return

```
E[R_p] = Σ wᵢ * R̄ᵢ
```

### Portfolio Variance

Sử dụng Single-Index Model:
```
σ²_p = β²_p * σ²_m + Σ w²ᵢ * σ²_εi

trong đó: β_p = Σ wᵢ * βᵢ
```

### Sharpe Ratio

```
Sharpe = (E[R_p] - Rf) / σ_p
```

## Practical Considerations

### 1. Estimation Window

**Trade-off:**
- Shorter window (6 months - 1 year): More responsive, less stable
- Longer window (3-5 years): More stable, less responsive

**Recommendation:**
- Daily data: 252-756 observations (1-3 years)
- Weekly data: 156-260 observations (3-5 years)
- Monthly data: 36-60 observations (3-5 years)

### 2. Risk-Free Rate

**Options:**
- Chính phủ bond yields (VN: TPCP 1 năm ~4-6%)
- Bank deposit rates
- For simplicity: 0 (interpret as excess returns)

**Frequency adjustment:**
```python
if frequency == 'D':
    rf_period = annual_rf / 252
elif frequency == 'W':
    rf_period = annual_rf / 52
elif frequency == 'M':
    rf_period = annual_rf / 12
```

### 3. Outlier Handling

**Problem:** Extreme returns can distort estimates

**Solutions:**
- Winsorize returns (cap at 1st/99th percentile)
- Remove outliers (z-score > 3)
- Robust regression methods

### 4. Rebalancing

**Frequency options:**
- Monthly: Balance cost vs adaptation
- Quarterly: Lower costs, less responsive
- Annually: Very low costs, slow to adapt

**Transaction costs:**
```python
cost = abs(trade_value) * cost_rate
typical_rate = 0.15% - 0.30% per trade
```

**Rebalancing threshold:**
- Only rebalance if drift > threshold (e.g., 5%)
- Reduces unnecessary trading

## Common Issues & Solutions

### Issue 1: All Z values negative

**Cause:** Expected returns too low, or C₀ too high

**Solutions:**
- Check risk-free rate (might be too high)
- Review expected returns estimation
- Consider using equal weights as fallback

### Issue 2: Extreme concentration

**Cause:** One stock dominates Z values

**Solutions:**
- Apply max_weight constraint
- Review outliers in expected returns
- Consider diversification penalty

### Issue 3: Unstable weights over time

**Cause:** Noisy parameter estimates

**Solutions:**
- Increase estimation window
- Use shrinkage methods for expected returns
- Smooth rebalancing (gradual adjustment)

### Issue 4: Low Sharpe ratio

**Cause:** Model limitations, estimation error

**Solutions:**
- Multi-factor models (beyond Single-Index)
- Regularization/shrinkage
- Robust optimization methods

## Example Workflow

```python
# 1. Load data
loader = VNDataLoader(start_date='2021-01-01', end_date='2024-12-31')
data = loader.get_data_bundle(stocks, index_symbol='VNINDEX')

# 2. Fit Single-Index Model
sim = SingleIndexModel(data['stock_returns'], data['index_returns'])
sim.fit()

# 3. Get parameters
expected_returns = sim.get_expected_returns()
betas = sim.get_all_betas()
residual_vars = sim.get_all_residual_vars()
market_var = sim.market_var

# 4. Optimize
egp = EGPOptimizer(
    expected_returns=expected_returns,
    betas=betas,
    residual_vars=residual_vars,
    market_var=market_var,
    risk_free_rate=0.05/252
)

weights = egp.optimize(allow_short=False, max_weight=0.30)

# 5. Analyze
stats = egp.get_portfolio_statistics()
print(f"Sharpe Ratio: {stats['sharpe_ratio']:.4f}")
print(f"Expected Return: {stats['portfolio_return']*252:.2%}")
```

## References

1. Elton, E. J., Gruber, M. J., & Padberg, M. W. (1976). "Simple Criteria for Optimal Portfolio Selection."

2. Elton, E. J., Gruber, M. J., & Padberg, M. W. (1978). "Simple Criteria for Optimal Portfolio Selection: Tracing Out the Efficient Frontier."

---

*EGP Portfolio Optimization - Algorithm Guide*
