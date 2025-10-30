---
applyTo: '**/*'
---
Instruction chung cho tất cả các dự án - Cung cấp nguyên tắc và quy tắc cơ bản mà AI phải tuân theo trong mọi tình huống làm việc với code và dự án.

# Quy tắc và Nguyên tắc chung cho Tất cả Dự án

## 1. **Ngôn ngữ và Giao tiếp**:
   - **Ngôn ngữ phản hồi**: Tất cả phản hồi, giải thích, tài liệu phải được viết bằng **tiếng Việt**.
   - **Ngôn ngữ code**: Tên variables, functions, classes, comments trong code phải sử dụng **tiếng Anh**.
   - **Tính nhất quán**: Luôn duy trì tính nhất quán trong cách đặt tên và viết code trong cùng một dự án.

## 2. **Nguyên tắc Thiết kế Code**:

### **SOLID Principles**:
   - **S**ingle Responsibility: Mỗi class/function chỉ có một trách nhiệm duy nhất
   - **O**pen/Closed: Mở cho extension, đóng cho modification
   - **L**iskov Substitution: Subclasses phải có thể thay thế base classes
   - **I**nterface Segregation: Tách biệt interfaces thành các phần nhỏ cụ thể
   - **D**ependency Inversion: Phụ thuộc vào abstractions, không phải concrete implementations

### **Clean Code Principles**:
   - **Readability**: Code phải dễ đọc và hiểu
   - **Simplicity**: Giữ code đơn giản, tránh over-engineering
   - **DRY** (Don't Repeat Yourself): Tránh duplicate code
   - **KISS** (Keep It Simple, Stupid): Giữ mọi thứ đơn giản
   - **YAGNI** (You Aren't Gonna Need It): Không implement tính năng chưa cần thiết

## 3. **Cấu trúc và Tổ chức Dự án**:

### **Folder Structure Standards**:
```
project_name/
├── README.md                     # Mô tả tổng quan dự án (tiếng Việt)
├── .gitignore                   # Git ignore patterns
├── .env.example                 # Environment variables template  
├── requirements.txt             # Dependencies (Python)
├── package.json                 # Dependencies (Node.js)
├── Dockerfile                   # Container definition
├── docker-compose.yml           # Multi-container setup
├── Makefile                     # Automation commands
│
├── docs/                        # Documentation
│   ├── README.md               # Hướng dẫn chi tiết
│   ├── api/                    # API documentation
│   ├── deployment/             # Deployment guides
│   └── architecture/           # Architecture diagrams
│
├── src/                         # Source code chính
│   ├── config/                 # Configuration
│   ├── utils/                  # Utility functions
│   ├── models/                 # Data models/ML models
│   ├── services/               # Business logic
│   └── api/                    # API layer
│
├── tests/                       # Test files
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── fixtures/               # Test data
│
├── scripts/                     # Automation scripts
├── config/                      # Configuration files
└── .github/                     # GitHub workflows và instructions
    ├── workflows/              # CI/CD pipelines
    └── instructions/           # AI coding instructions
```

### **File Naming Conventions**:
- **Tất cả files/folders**: Sử dụng `snake_case` hoặc `kebab-case`
- **Tránh**: Spaces, ký tự đặc biệt, ký tự Unicode
- **Consistent**: Duy trì một style trong cùng dự án

## 4. **Documentation Standards**:

### **README.md Template**:
```markdown
# Tên Dự Án

## Mô tả
Mô tả ngắn gọn về dự án và mục đích sử dụng.

## Yêu cầu Hệ thống
- [Danh sách requirements]

## Cài đặt
```bash
# Các bước cài đặt
```

## Sử dụng
```bash
# Ví dụ sử dụng
```

## Cấu trúc Dự án
- Giải thích cấu trúc folder chính

## Đóng góp
- Hướng dẫn cho contributors

## License
- Thông tin license
```

### **Code Documentation**:
- **Inline comments**: Giải thích logic phức tạp bằng tiếng Việt
- **Function/Class documentation**: Sử dụng docstrings với format phù hợp
- **API documentation**: Tự động generate từ code annotations

## 5. **Version Control Best Practices**:

### **Git Commit Messages**:
```
[type]: mô tả thay đổi bằng tiếng Việt

Types:
- feat: thêm tính năng mới
- fix: sửa bug
- docs: cập nhật documentation
- style: thay đổi formatting
- refactor: refactor code
- test: thêm/sửa tests
- chore: cập nhật build tools, dependencies
```

### **Branch Naming**:
```
feature/ten-tinh-nang-moi
bugfix/sua-loi-xac-dinh
hotfix/sua-loi-khan-cap
release/v1.0.0
```

### **Git Ignore Patterns**:
```gitignore
# Dependencies
node_modules/
venv/
__pycache__/

# Environment files
.env
.env.local

# Build outputs
dist/
build/
*.egg-info/

# IDE files
.vscode/
.idea/
*.swp

# OS files
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Temporary files
*.tmp
*.temp
```

## 6. **Security Standards**:

### **Bảo mật Cơ bản**:
- **Không commit**: Passwords, API keys, sensitive data
- **Environment variables**: Sử dụng .env files cho config
- **Input validation**: Validate tất cả user inputs
- **SQL injection**: Sử dụng parameterized queries
- **XSS protection**: Sanitize HTML outputs
- **HTTPS**: Luôn sử dụng HTTPS trong production

### **Secrets Management**:
```bash
# .env.example template
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database
DB_USER=your_username
DB_PASSWORD=your_password_here
API_KEY=your_api_key_here
```

## 7. **Error Handling và Logging**:

### **Error Handling Principles**:
- **Fail fast**: Phát hiện lỗi sớm nhất có thể
- **Graceful degradation**: Xử lý lỗi một cách nhẹ nhàng
- **User-friendly messages**: Thông báo lỗi dễ hiểu cho user
- **Developer-friendly logs**: Chi tiết cho debugging

### **Logging Standards**:
```
[TIMESTAMP] [LEVEL] [MODULE] - Message in Vietnamese
2024-08-01 10:30:15 INFO UserService - Người dùng đăng nhập thành công: user123
2024-08-01 10:30:16 ERROR PaymentService - Lỗi khi xử lý thanh toán: Invalid card number
```

## 8. **Testing Strategy**:

### **Testing Pyramid**:
- **Unit Tests**: 70% - Test individual functions/methods
- **Integration Tests**: 20% - Test component interactions  
- **E2E Tests**: 10% - Test complete user workflows

### **Test Naming**:
```
test_[function_name]_[scenario]_[expected_result]
test_calculate_total_with_valid_input_returns_correct_sum
test_user_login_with_invalid_password_throws_error
```

## 9. **Performance và Optimization**:

### **Performance Guidelines**:
- **Database**: Index các columns thường query
- **Caching**: Implement caching cho data không thay đổi thường xuyên
- **Lazy Loading**: Load data chỉ khi cần thiết
- **Compression**: Sử dụng compression cho static assets
- **CDN**: Sử dụng CDN cho static files

### **Code Optimization**:
- **Profiling**: Measure trước khi optimize
- **Bottlenecks**: Xác định và fix performance bottlenecks
- **Memory**: Quản lý memory efficiently
- **Algorithms**: Chọn algorithms phù hợp với use case

## 10. **Deployment và DevOps**:

### **Container Standards**:
```dockerfile
# Multi-stage builds
FROM node:16-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:16-alpine AS runtime
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
```

### **Environment Management**:
- **Development**: Local development với hot reload
- **Staging**: Môi trường giống production để test
- **Production**: Môi trường live với monitoring đầy đủ

## 11. **Code Review Standards**:

### **Review Checklist**:
- [ ] Code tuân thủ naming conventions
- [ ] Logic rõ ràng và dễ hiểu
- [ ] Error handling đầy đủ
- [ ] Tests coverage đạt yêu cầu
- [ ] Documentation cập nhật
- [ ] Security considerations được xem xét
- [ ] Performance impact được đánh giá

### **Review Comments**:
- Sử dụng tiếng Việt khi comment
- Constructive feedback
- Explain "why" không chỉ "what"
- Suggest alternatives khi possible

## 12. **Monitoring và Analytics**:

### **Application Monitoring**:
- **Health Checks**: Endpoint /health cho container orchestration
- **Metrics**: CPU, Memory, Disk usage
- **Logs**: Centralized logging với structured logs
- **Alerts**: Thiết lập alerts cho critical issues

### **Business Metrics**:
- **User Analytics**: Track user behavior
- **Performance Metrics**: Response time, throughput
- **Error Rates**: Track và analyze error patterns
- **Business KPIs**: Metrics specific cho business domain

## 13. **Team Collaboration**:

### **Communication Standards**:
- **Daily Standups**: Status updates và blockers
- **Code Reviews**: Mandatory cho mọi changes
- **Documentation**: Keep docs up-to-date
- **Knowledge Sharing**: Regular tech talks và workshops

### **Development Workflow**:
1. **Planning**: Define requirements rõ ràng
2. **Design**: Architecture và API design
3. **Implementation**: Code theo standards
4. **Testing**: Comprehensive testing
5. **Review**: Code review và feedback
6. **Deploy**: Staged deployment với monitoring
7. **Monitor**: Track performance và issues

## 14. **Maintenance và Technical Debt**:

### **Technical Debt Management**:
- **Regular Refactoring**: Schedule time cho refactoring
- **Dependency Updates**: Keep dependencies up-to-date
- **Code Quality**: Regular code quality assessments
- **Documentation**: Keep documentation current

### **Legacy Code**:
- **Gradual Migration**: Migrate legacy code từng phần
- **Testing**: Add tests trước khi refactor
- **Documentation**: Document legacy behavior
- **Risk Assessment**: Evaluate risks trước khi thay đổi

---

## **Lưu ý quan trọng**:
- Các quy tắc này là **foundation** cho tất cả dự án
- Specific instructions (Python, SQL, etc.) sẽ **extend** và **override** các quy tắc này khi cần
- **Consistency** là key - luôn áp dụng nhất quán trong cùng một dự án
- **Team agreement** quan trọng hơn perfect adherence to rules
