### CONTRIBUTING.md
```bash
cat > CONTRIBUTING.md << 'EOF'
# 🤝 PyPDF-Stirling Tools v2'ye Katkıda Bulunma

Projeye katkıda bulunmak istediğiniz için teşekkürler! 

## 🚀 Nasıl Katkıda Bulunabilirsiniz

### 🐛 Bug Report
- [Bug Report Template](.github/ISSUE_TEMPLATE/bug_report.md) kullanın
- Detaylı bilgi ve reproduksiyon adımları sağlayın

### 💡 Feature Request  
- [Feature Request Template](.github/ISSUE_TEMPLATE/feature_request.md) kullanın
- Özelliğin neden gerekli olduğunu açıklayın

### 🔧 Code Contribution
1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)  
5. Pull Request açın

## 📋 Development Setup

```bash
git clone https://github.com/YOUR-USERNAME/PyPDF-Tools-v2.git
cd PyPDF-Tools-v2
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install -r requirements.txt
python main.py
```

## 🧪 Testing

```bash
python tests/test_app.py
```

## 📏 Code Standards

- PEP 8 Python style guide
- Docstring'ler gerekli
- Type hints kullanın
- Test coverage %80+

Katkılarınız için teşekkürler! 🎉
EOF
```
