# Changelog

Bu dosya PyPDF-Tools projesinin tüm önemli değişikliklerini dokümante eder.

Format [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) standardına dayanır ve bu proje [Semantic Versioning](https://semver.org/spec/v2.0.0.html) kullanır.

## [2.0.0] - 2024-12-15

### Eklenen
- 🎨 **4 Yeni Tema**: Aydınlık, Karanlık, Neon ve Gece Yarısı Mavisi temaları
- 🔄 **Animasyonlu Arayüz**: Göz alıcı ve performans odaklı animasyonlar
- 📱 **Responsive Tasarım**: Her ekran boyutuna uygun modern arayüz
- 🖱️ **Drag & Drop Desteği**: Dosyaları sürükleyip bırakma özelliği
- 📦 **Linux AppImage**: Tek dosyada taşınabilir uygulama
- 🐧 **Native Paketler**: .deb, .rpm, .pkg paketleri
- ⚡ **Otomatik Kurulum**: Her platform için özel kurulum scriptleri
- 📚 **AUR Paketi**: Arch Linux kullanıcıları için AUR desteği
- 🛡️ **Sistem Tepsisi**: Arka planda çalışma ve hızlı erişim
- 🔐 **Gelişmiş Gizlilik**: İsteğe bağlı veri saklama ve otomatik temizlik

### PDF İşleme
- ✅ PDF Birleştirme (Merge) - %300 daha hızlı
- ✅ PDF Bölme (Split) - Akıllı sayfa algılama
- ✅ Sayfa Döndürme (Rotate) - Toplu döndürme desteği
- ✅ Sayfa Yeniden Düzenleme (Reorder) - Drag & drop ile
- ✅ PDF Sıkıştırma (Compress) - 3 kalite seviyesi
- ✅ PDF Optimizasyonu (Optimize) - %50 daha az bellek kullanımı

### Dönüştürme Motoru
- 🔄 **PDF'e Dönüştürme**: Word, Excel, PowerPoint, Görsel → PDF
- 🔄 **PDF'den Dönüştürme**: PDF → Word, Excel, PowerPoint, Görsel
- ⚡ **Toplu Dönüştürme**: Batch conversion desteği
- 🎯 **Format Koruma**: Layout preservation teknolojisi

### Güvenlik ve İmzalama
- 🔒 PDF Şifreleme (Encrypt) - AES-256 desteği
- 🔓 Şifre Kaldırma (Decrypt)
- ✍️ Dijital İmzalama (Digital Signature)
- ✅ İmza Doğrulama (Signature Verification)
- 🛡️ İzin Yönetimi (Permissions)

### OCR ve Metin İşleme
- 🔍 **OCR İşlemi**: 50+ dil desteği
- 🤖 **Otomatik Dil Algılama**: Akıllı dil tanıma
- 🖼️ **Görüntü Ön İşleme**: Kalite artırma algoritmaları
- 📝 **Taranmış PDF**: Aranabilir PDF'ye dönüştürme
- 🔍 **Gelişmiş Metin Arama**: RegEx desteği ile

### PDF Okuyucu
- 📖 **Adobe Acrobat Tarzı Tasarım**: Profesyonel görünüm
- 🎨 **Çoklu Vurgulama**: Renkli vurgulama araçları
- 🖋️ **Çizim Araçları**: Kalem ile not alma ve alt çizme
- 👁️ **Göz Koruma**: Sarı ekran modu (Blue Light Filter)
- 🖼️ **Sayfa Küçük Resimleri**: Hızlı navigasyon

### Script Engine
- 🐍 **Python 3.11 Tabanlı**: Güçlü script sistemi
- 💻 **Dahili IDE**: Syntax highlighting ve auto-completion
- 🔧 **Hata Ayıklama**: Debugging araçları
- 📚 **Script Kütüphanesi**: Hazır şablonlar
- ⚡ **Çoklu Script**: Eş zamanlı çalıştırma desteği

### Otomasyon Sistemi
- 📁 **Klasör İzleme**: Otomatik dosya işleme
- ⚡ **Trigger Sistemi**: Koşullu işlem başlatma
- ⏰ **Zamanlayıcı**: Planlı görevler
- 📧 **E-posta Bildirimleri**: İşlem tamamlama bildirimleri
- 🔄 **Batch İşlemler**: Toplu dosya işleme

### Platform Desteği
- 🪟 **Windows**: 10/11 (64-bit) - MSI ve Portable
- 🍎 **macOS**: 10.15+ - DMG ve Homebrew
- 🐧 **Linux**: AppImage, .deb, .rpm, AUR paketi
- ⚡ **Otomatik Kurulumlar**: Her platform için script

### Performans İyileştirmeleri
- ⚡ %300 daha hızlı PDF işleme
- 🧠 %50 daha az bellek kullanımı
- 📁 1GB+ büyük dosya desteği
- 🔄 Akıllı önbellekleme sistemi
- ⚙️ Çoklu işlemci desteği

## [1.0.0] - 2024-06-01

### Eklenen
- Temel PDF işleme özellikleri
- Basit GUI arayüzü
- Merge ve Split işlemleri
- OCR desteği (Tesseract)
- Windows ve Linux desteği

### Değiştirilen
- N/A (İlk sürüm)

### Kullanımdan Kaldırılan
- N/A (İlk sürüm)

### Kaldırılan
- N/A (İlk sürüm)

### Güvenlik
- N/A (İlk sürüm)

## [0.9.0-beta] - 2024-05-15

### Eklenen
- Beta sürümü özellikleri
- Temel PDF merge/split
- İlk GUI tasarımı

---

## Sürüm Notları

### v2.0.0 Hakkında
Bu ana sürüm, uygulamanın tamamen yeniden yazıldığı ve modern Python/Qt teknolojileri ile geliştirildiği sürümdür. Stirling-PDF'den ilham alınarak, ancak masaüstü uygulaması olarak tasarlanmıştır.

### Planlanan Özellikler (v2.1.0)
- [ ] Plugin sistemi
- [ ] REST API desteği
- [ ] Gelişmiş automation rules
- [ ] Cloud storage entegrasyonu
- [ ] AI-powered PDF analysis

### Bilinen Sorunlar
- macOS M1 chiplerinde ilk açılışta yavaşlık olabilir
- Linux'ta bazı Qt temalarında ikon eksikliği
- Windows'ta büyük dosyalarda (>500MB) geçici donmalar

### Destek Versiyon
- **Aktif Destek**: v2.x serisi
- **Güvenlik Güncellemeleri**: v1.x serisi (2025 sonuna kadar)
- **Destek Sonu**: v0.x serisi

---

**Not**: Daha fazla detay için [GitHub Releases](https://github.com/Fatih-Bucaklioglu/PyPDF-Tools/releases) sayfasını ziyaret edebilirsiniz.
