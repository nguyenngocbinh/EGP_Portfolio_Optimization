# Tests

## Tổng quan

Project sử dụng `pytest` cho unit testing với coverage tracking.

## Cấu trúc Tests

```
tests/
├── __init__.py              # Test initialization
├── conftest.py              # Pytest configuration & fixtures
├── test_single_index_model.py    # Tests cho Single-Index Model
├── test_egp_optimizer.py         # Tests cho EGP Optimizer
└── test_preprocessor.py          # Tests cho Data Preprocessor
```

## Chạy Tests

### Chạy tất cả tests

```bash
pytest tests/ -v
```

### Chạy với coverage

```bash
pytest tests/ --cov=src --cov-report=html --cov-report=term
```

### Chạy specific test file

```bash
pytest tests/test_egp_optimizer.py -v
```

### Chạy specific test case

```bash
pytest tests/test_egp_optimizer.py::TestEGPOptimizer::test_optimize_no_short -v
```

### Chạy với markers

```bash
# Chỉ unit tests
pytest tests/ -m unit

# Bỏ qua slow tests
pytest tests/ -m "not slow"
```

## Test Coverage

Để xem coverage report:

```bash
pytest tests/ --cov=src --cov-report=html
# Mở htmlcov/index.html trong browser
```

Target coverage: **>80%** cho production code

## CI/CD Integration

GitHub Actions tự động chạy tests khi:
- Push to `main` hoặc `develop` branch
- Pull request to `main` hoặc `develop`
- Manual trigger via workflow_dispatch

### Test Matrix

Tests chạy trên:
- Python 3.8
- Python 3.9
- Python 3.10
- Python 3.11

## Writing Tests

### Test Structure

```python
import pytest
from src.models.your_module import YourClass


class TestYourClass:
    """Test cases for YourClass"""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for tests"""
        return {"key": "value"}
    
    def test_initialization(self, sample_data):
        """Test object initialization"""
        obj = YourClass(sample_data)
        assert obj is not None
    
    def test_method(self, sample_data):
        """Test specific method"""
        obj = YourClass(sample_data)
        result = obj.method()
        assert result == expected_value
```

### Best Practices

1. **One assertion per test** (when possible)
2. **Use descriptive test names**: `test_what_condition_expected`
3. **Use fixtures** for reusable test data
4. **Test edge cases**: empty inputs, None, negative numbers
5. **Test error handling**: use `pytest.raises()`
6. **Mock external dependencies**: API calls, file I/O

### Example: Testing with Fixtures

```python
@pytest.fixture
def portfolio_data():
    """Reusable portfolio test data"""
    return {
        'symbols': ['VNM', 'VIC'],
        'weights': pd.Series({'VNM': 0.6, 'VIC': 0.4})
    }

def test_portfolio_creation(portfolio_data):
    portfolio = Portfolio(**portfolio_data)
    assert len(portfolio.symbols) == 2
```

### Example: Testing Exceptions

```python
def test_invalid_input_raises_error():
    with pytest.raises(ValueError, match="Invalid input"):
        YourClass(invalid_input)
```

### Example: Testing Warnings

```python
def test_warning_raised():
    with pytest.warns(UserWarning):
        function_that_warns()
```

## Continuous Integration

### GitHub Actions Workflow

File: `.github/workflows/tests.yml`

**Jobs:**
1. **test**: Run pytest with coverage on multiple Python versions
2. **lint**: Check code style with flake8 and black
3. **security**: Run bandit and safety checks

### Badges

Add to README.md:

```markdown
![Tests](https://github.com/your-username/EGP_Portfolio_Optimization/workflows/Python%20Tests/badge.svg)
![Coverage](https://codecov.io/gh/your-username/EGP_Portfolio_Optimization/branch/main/graph/badge.svg)
```

## Debugging Failed Tests

### Verbose output

```bash
pytest tests/ -vv
```

### Show print statements

```bash
pytest tests/ -s
```

### Stop at first failure

```bash
pytest tests/ -x
```

### Run last failed tests

```bash
pytest tests/ --lf
```

### Debug with pdb

```bash
pytest tests/ --pdb
```

## Test Data

Tests sử dụng synthetic data để tránh dependency vào external APIs:

- `sample_data`: Randomly generated stock/market returns
- `sample_parameters`: Pre-defined optimization parameters
- Seed: `np.random.seed(42)` cho reproducibility

## Mocking External Dependencies

Ví dụ mock vnstock3:

```python
from unittest.mock import Mock, patch

@patch('src.data.data_loader.Vnstock')
def test_data_loader(mock_vnstock):
    mock_stock = Mock()
    mock_stock.quote.history.return_value = pd.DataFrame(...)
    mock_vnstock.return_value.stock.return_value = mock_stock
    
    # Test your code
    loader = VNDataLoader()
    data = loader.get_stock_prices(['VNM'])
    
    assert len(data) > 0
```

## Performance Testing

Để test performance:

```python
import time

def test_optimization_speed():
    start = time.time()
    
    # Run optimization
    egp.optimize()
    
    duration = time.time() - start
    
    # Should complete in reasonable time
    assert duration < 1.0  # Less than 1 second
```

## Test Coverage Goals

| Module | Target Coverage |
|--------|-----------------|
| `single_index_model.py` | >90% |
| `egp_optimizer.py` | >90% |
| `portfolio.py` | >85% |
| `data_loader.py` | >75% (due to external API) |
| `preprocessor.py` | >85% |
| `backtesting.py` | >80% |
| `plots.py` | >60% (visualization) |

## Contributing Tests

Khi thêm feature mới:

1. Viết tests trước (TDD approach)
2. Ensure tests pass: `pytest tests/ -v`
3. Check coverage: `pytest tests/ --cov=src`
4. Update this README nếu cần

## Troubleshooting

### Import errors

```bash
# Add src to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest tests/
```

### Fixture not found

Check `conftest.py` contains fixture definition.

### Tests pass locally but fail in CI

- Check Python version compatibility
- Verify all dependencies in requirements.txt
- Check random seed consistency

---

**Maintained by:** EGP Project Team  
**Last updated:** October 2025
