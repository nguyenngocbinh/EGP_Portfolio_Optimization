# Dẫn Xuất Toán Học - Thuật Toán EGP

## Tổng quan

Tài liệu này trình bày chi tiết các bước dẫn xuất toán học cho thuật toán **Elton-Gruber-Padberg (EGP)** áp dụng cho tối ưu hóa danh mục đầu tư với **Single-Index Model**.

---

## 1. Single-Index Model

### 1.1. Giả định cơ bản

Mô hình Single-Index giả định rằng lợi tức của mỗi cổ phiếu được quyết định bởi một nhân tố chung (market factor) và một nhân tố riêng (specific factor):

$$R_i = \alpha_i + \beta_i R_m + \varepsilon_i$$

Trong đó:
- $R_i$: Lợi tức của cổ phiếu $i$
- $R_m$: Lợi tức của thị trường (market index)
- $\alpha_i$: Alpha (excess return không giải thích được bởi market)
- $\beta_i$: Beta (độ nhạy với market)
- $\varepsilon_i$: Phần dư (specific risk)

### 1.2. Các giả định thống kê

1. **Kỳ vọng phần dư bằng 0:**
   $$E[\varepsilon_i] = 0 \quad \forall i$$

2. **Phần dư không tương quan với market:**
   $$\text{Cov}(\varepsilon_i, R_m) = 0 \quad \forall i$$

3. **Phần dư giữa các cổ phiếu không tương quan:**
   $$\text{Cov}(\varepsilon_i, \varepsilon_j) = 0 \quad \forall i \neq j$$

### 1.3. Kỳ vọng và phương sai

**Kỳ vọng lợi tức:**
$$\bar{R}_i = E[R_i] = \alpha_i + \beta_i E[R_m]$$

**Phương sai lợi tức:**
$$\sigma_i^2 = \text{Var}(R_i) = \beta_i^2 \sigma_m^2 + \sigma_{\varepsilon_i}^2$$

Trong đó:
- $\sigma_m^2 = \text{Var}(R_m)$: Phương sai của market
- $\sigma_{\varepsilon_i}^2 = \text{Var}(\varepsilon_i)$: Phương sai phần dư của stock $i$

**Hiệp phương sai giữa hai cổ phiếu:**
$$\sigma_{ij} = \text{Cov}(R_i, R_j) = \beta_i \beta_j \sigma_m^2$$

---

## 2. Bài toán tối ưu hóa danh mục

### 2.1. Mục tiêu: Maximize Sharpe Ratio

Chúng ta muốn tìm danh mục có **Sharpe ratio** cao nhất:

$$\max_{w_i} \quad \theta = \frac{E[R_p] - R_f}{\sigma_p}$$

Trong đó:
- $E[R_p] = \sum_{i=1}^N w_i \bar{R}_i$: Kỳ vọng lợi tức danh mục
- $R_f$: Lãi suất phi rủi ro
- $\sigma_p$: Độ lệch chuẩn của danh mục
- $w_i$: Tỷ trọng của cổ phiếu $i$

### 2.2. Ràng buộc

$$\sum_{i=1}^N w_i = 1$$

(Có thể thêm ràng buộc: $w_i \geq 0$ nếu không cho phép bán khống)

### 2.3. Phương sai danh mục với Single-Index Model

Theo Single-Index Model:

$$\sigma_p^2 = \beta_p^2 \sigma_m^2 + \sum_{i=1}^N w_i^2 \sigma_{\varepsilon_i}^2$$

Trong đó $\beta_p = \sum_{i=1}^N w_i \beta_i$ là beta của danh mục.

---

## 3. Dẫn xuất EGP Algorithm

### 3.1. Đổi biến

EGP đề xuất đổi biến từ $w_i$ sang $Z_i$ để đơn giản hóa:

$$Z_i = \frac{w_i}{\sigma_p^2}$$

Khi đó:
$$w_i = Z_i \sigma_p^2$$

### 3.2. Điều kiện tối ưu (First-Order Condition)

Lấy đạo hàm của Sharpe ratio theo $w_i$ và cho bằng 0, sau một số biến đổi đại số (xem Appendix của bài báo EGP), ta có:

$$(\bar{R}_i - R_f) \sigma_p^2 = w_i \left[\beta_i^2 \sigma_m^2 + \sigma_{\varepsilon_i}^2 + \beta_i \sigma_m^2 \sum_{j=1}^N w_j \beta_j\right]$$

Thay $w_i = Z_i \sigma_p^2$:

$$\bar{R}_i - R_f = Z_i \left[\beta_i^2 \sigma_m^2 + \sigma_{\varepsilon_i}^2 + \beta_i \sigma_m^2 \sum_{j=1}^N Z_j \beta_j \sigma_p^2\right]$$

Chia hai vế cho $\sigma_{\varepsilon_i}^2$:

$$\frac{\bar{R}_i - R_f}{\sigma_{\varepsilon_i}^2} = Z_i \left[\frac{\beta_i^2 \sigma_m^2}{\sigma_{\varepsilon_i}^2} + 1 + \frac{\beta_i \sigma_m^2}{\sigma_{\varepsilon_i}^2} \sum_{j=1}^N Z_j \beta_j \sigma_p^2\right]$$

### 3.3. Công thức EGP (2)

Sau khi sắp xếp lại, EGP thu được:

$$\boxed{Z_i = \frac{\bar{R}_i - R_f}{\sigma_{\varepsilon_i}^2} - \frac{\beta_i \sigma_m^2}{\sigma_{\varepsilon_i}^2} \sum_{j=1}^N Z_j \beta_j}$$

Đây là phương trình (2) trong bài báo EGP.

### 3.4. Giải cho $S = \sum_{j=1}^N Z_j \beta_j$

Nhân cả hai vế của phương trình trên với $\beta_i$ và cộng theo $i$:

$$\sum_{i=1}^N Z_i \beta_i = \sum_{i=1}^N \frac{(\bar{R}_i - R_f) \beta_i}{\sigma_{\varepsilon_i}^2} - \sigma_m^2 \left(\sum_{i=1}^N Z_i \beta_i\right) \left(\sum_{i=1}^N \frac{\beta_i^2}{\sigma_{\varepsilon_i}^2}\right)$$

Đặt $S = \sum_{j=1}^N Z_j \beta_j$, ta có:

$$S = A - \sigma_m^2 \cdot S \cdot B$$

Trong đó:
$$A = \sum_{i=1}^N \frac{(\bar{R}_i - R_f) \beta_i}{\sigma_{\varepsilon_i}^2}$$

$$B = \sum_{i=1}^N \frac{\beta_i^2}{\sigma_{\varepsilon_i}^2}$$

Giải cho $S$:

$$S + \sigma_m^2 S B = A$$
$$S(1 + \sigma_m^2 B) = A$$

$$\boxed{S = \frac{A}{1 + \sigma_m^2 B} = \frac{\displaystyle\sum_{i=1}^N \frac{(\bar{R}_i - R_f) \beta_i}{\sigma_{\varepsilon_i}^2}}{1 + \sigma_m^2 \displaystyle\sum_{i=1}^N \frac{\beta_i^2}{\sigma_{\varepsilon_i}^2}}}$$

Đây là phương trình (3) trong bài báo EGP.

### 3.5. Định nghĩa $C_0$

EGP định nghĩa hằng số **cutoff** $C_0$:

$$\boxed{C_0 = \sigma_m^2 \cdot S = \frac{\sigma_m^2 \displaystyle\sum_{i=1}^N \frac{(\bar{R}_i - R_f) \beta_i}{\sigma_{\varepsilon_i}^2}}{1 + \sigma_m^2 \displaystyle\sum_{i=1}^N \frac{\beta_i^2}{\sigma_{\varepsilon_i}^2}}}$$

### 3.6. Công thức cuối cùng cho $Z_i$

Thay $S$ bằng $C_0 / \sigma_m^2$ vào phương trình (2):

$$Z_i = \frac{\bar{R}_i - R_f}{\sigma_{\varepsilon_i}^2} - \frac{\beta_i \sigma_m^2}{\sigma_{\varepsilon_i}^2} \cdot \frac{C_0}{\sigma_m^2}$$

$$\boxed{Z_i = \frac{\bar{R}_i - R_f}{\sigma_{\varepsilon_i}^2} - \frac{\beta_i}{\sigma_{\varepsilon_i}^2} C_0}$$

Hoặc viết dưới dạng:

$$\boxed{Z_i = \frac{\beta_i}{\sigma_{\varepsilon_i}^2} \left[\frac{\bar{R}_i - R_f}{\beta_i} - C_0\right]}$$

---

## 4. Ý nghĩa của $C_0$ và $Z_i$

### 4.1. Cutoff Constant $C_0$

$C_0$ là **tiêu chuẩn chọn cổ phiếu**:
- Nếu $\frac{\bar{R}_i - R_f}{\beta_i} > C_0$: Cổ phiếu $i$ được chọn (long position)
- Nếu $\frac{\bar{R}_i - R_f}{\beta_i} < C_0$: Cổ phiếu $i$ bị loại (hoặc short nếu cho phép)

Số hạng $\frac{\bar{R}_i - R_f}{\beta_i}$ có thể hiểu là **excess return per unit of beta**.

### 4.2. Z Values

$Z_i$ thể hiện **mức độ đóng góp** của cổ phiếu $i$ vào danh mục tối ưu:
- $Z_i > 0$: Mua (long)
- $Z_i < 0$: Bán khống (short) nếu cho phép
- $Z_i = 0$: Không đầu tư

### 4.3. Chuyển đổi thành weights

Từ $Z_i$, ta tính weights:

$$w_i = \frac{Z_i}{\sum_{j=1}^N |Z_j|}$$

(Chuẩn hóa để $\sum w_i = 1$)

---

## 5. Thuật toán Implementation

### Bước 1: Ước lượng parameters từ dữ liệu

Cho mỗi cổ phiếu $i$, hồi quy OLS:

$$R_i^{(t)} = \alpha_i + \beta_i R_m^{(t)} + \varepsilon_i^{(t)}$$

Thu được:
- $\hat{\beta}_i$: Slope
- $\hat{\alpha}_i$: Intercept
- $\hat{\sigma}_{\varepsilon_i}^2 = \frac{1}{T-2} \sum_{t=1}^T (\varepsilon_i^{(t)})^2$

Tính:
- $\hat{\sigma}_m^2 = \text{Var}(R_m)$
- $\bar{R}_i = \hat{\alpha}_i + \hat{\beta}_i \bar{R}_m$ (hoặc dùng historical mean)

### Bước 2: Tính $C_0$

$$C_0 = \frac{\sigma_m^2 \sum_{i=1}^N \frac{(\bar{R}_i - R_f) \beta_i}{\sigma_{\varepsilon_i}^2}}{1 + \sigma_m^2 \sum_{i=1}^N \frac{\beta_i^2}{\sigma_{\varepsilon_i}^2}}$$

### Bước 3: Tính $Z_i$ cho mỗi cổ phiếu

$$Z_i = \frac{\bar{R}_i - R_f}{\sigma_{\varepsilon_i}^2} - \frac{\beta_i}{\sigma_{\varepsilon_i}^2} C_0$$

### Bước 4: Áp dụng constraints

- Nếu không bán khống: $Z_i \leftarrow \max(Z_i, 0)$
- Nếu có max/min weight: Điều chỉnh iteratively

### Bước 5: Chuẩn hóa thành weights

$$w_i = \frac{Z_i}{\sum_{j=1}^N |Z_j|}$$

---

## 6. Tính chất của giải pháp EGP

### 6.1. Optimal Portfolio Variance

$$\sigma_p^2 = \frac{C_0}{1 + C_0 B}$$

Trong đó $B = \sum_{i \in \text{selected}} \frac{\beta_i^2}{\sigma_{\varepsilon_i}^2}$

### 6.2. Expected Return

$$E[R_p] = R_f + C_0 \beta_p$$

Trong đó $\beta_p = \sum_i w_i \beta_i$

### 6.3. Sharpe Ratio

$$\theta = \frac{E[R_p] - R_f}{\sigma_p} = \sqrt{C_0(1 + C_0 B) - C_0^2 B}$$

---

## 7. Ưu điểm và hạn chế

### Ưu điểm
✅ Công thức đóng, không cần QP solver  
✅ Tính toán nhanh, $O(N)$ complexity  
✅ Không cần ma trận hiệp phương sai đầy đủ  
✅ Dễ implement và diễn giải  

### Hạn chế
❌ Dựa vào giả định Single-Index (một nhân tố)  
❌ Nhạy với lỗi ước lượng của $\bar{R}_i$  
❌ Với constraints phức tạp, cần điều chỉnh thêm  
❌ Không phải always globally optimal với upper bounds  

---

## 8. Tài liệu tham khảo

1. Elton, E. J., Gruber, M. J., & Padberg, M. W. (1976). "Simple Criteria for Optimal Portfolio Selection." *The Journal of Finance*, 31(5), 1341-1357.

2. Elton, E. J., Gruber, M. J., & Padberg, M. W. (1978). "Simple Criteria for Optimal Portfolio Selection: Tracing Out the Efficient Frontier." *The Journal of Finance*, 33(1), 296-302.

3. Sharpe, W. F. (1963). "A Simplified Model for Portfolio Analysis." *Management Science*, 9(2), 277-293.

---

*Document created for EGP Portfolio Optimization Project*
