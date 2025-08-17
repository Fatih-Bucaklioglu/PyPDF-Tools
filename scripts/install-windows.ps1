# PyPDF-Stirling Tools v2 - Windows Kurulum Scripti
# PowerShell ile otomatik kurulum
# Kullanım: irm https://raw.githubusercontent.com/Fatih-Bucaklioglu/PyPDF-Tools-v2/main/install-windows.ps1 | iex

param(
    [switch]$SkipDependencies,
    [switch]$Force,
    [string]$InstallPath = "$env:LOCALAPPDATA\Programs\PyPDF-Tools-v2"
)

# Yönetici yetkisi kontrolü
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Renkli çıktı fonksiyonları
function Write-Success { param($Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Error { param($Message) Write-Host "❌ $Message" -ForegroundColor Red }
function Write-Warning { param($Message) Write-Host "⚠️  $Message" -ForegroundColor Yellow }
function Write-Info { param($Message) Write-Host "ℹ️  $Message" -ForegroundColor Cyan }
function Write-Progress { param($Message) Write-Host "⚙️  $Message" -ForegroundColor Blue }

# Ana kurulum fonksiyonu
function Install-PyPDFTools {
    Write-Host "🚀 PyPDF-Stirling Tools v2 Windows Kurulumu" -ForegroundColor Magenta
    Write-Host "=" * 50 -ForegroundColor Gray

    # Sistem bilgilerini göster
    Write-Info "İşletim Sistemi: $(Get-WmiObject Win32_OperatingSystem | Select-Object -ExpandProperty Caption)"
    Write-Info "PowerShell Sürümü: $($PSVersionTable.PSVersion)"
    Write-Info "Kurulum Yolu: $InstallPath"
    Write-Host ""

    try {
        # 1. Python kontrolü ve kurulumu
        Test-Python

        # 2. Git kontrolü
        Test-Git

        # 3. Sistem bağımlılıklarını kur
        if (-not $SkipDependencies) {
            Install-Dependencies
        }

        # 4. Kaynak kodunu indir
        Download-Source

        # 5. Python sanal ortamı oluştur
        Create-VirtualEnvironment

        # 6. Python paketlerini kur
        Install-PythonPackages

        # 7. Başlatma scripti oluştur
        Create-Launcher

        # 8. Başlat menüsü kısayolu
        Create-StartMenuShortcut

        # 9. Masaüstü kısayolu (isteğe bağlı)
        Create-DesktopShortcut

        # 10. PATH'e ekle
        Add-ToPath

        # 11. Kurulum testini çalıştır
        Test-Installation

        Write-Success "🎉 PyPDF-Stirling Tools v2 başarıyla kuruldu!"
        Write-Info "Başlatmak için: Start Menu > PyPDF-Stirling Tools v2"
        Write-Info "Terminal: pypdf-tools-v2"

    } catch {
        Write-Error "Kurulum sırasında hata oluştu: $($_.Exception.Message)"
        Write-Error "Stack Trace: $($_.ScriptStackTrace)"
        exit 1
    }
}

# Python kontrolü ve kurulumu
function Test-Python {
    Write-Progress "Python kurulumu kontrol ediliyor..."

    $pythonCmd = $null

    # Python komutlarını test et
    $pythonCommands = @("python", "python3", "py")

    foreach ($cmd in $pythonCommands) {
        try {
            $version = & $cmd --version 2>$null
            if ($version -match "Python (\d+)\.(\d+)") {
                $major = [int]$matches[1]
                $minor = [int]$matches[2]

                if (($major -eq 3 -and $minor -ge 8) -or $major -gt 3) {
                    $pythonCmd = $cmd
                    Write-Success "Python $version bulundu ($cmd)"
                    break
                }
            }
        } catch {
            continue
        }
    }

    if (-not $pythonCmd) {
        Write-Warning "Uygun Python sürümü bulunamadı (3.8+ gerekli)"
        Install-Python
    }

    $Global:PythonCommand = $pythonCmd
}

# Python kurulumu
function Install-Python {
    Write-Progress "Python kuruluyor..."

    # Chocolatey varsa kullan
    if (Get-Command choco -ErrorAction SilentlyContinue) {
        Write-Info "Chocolatey ile Python kuruluyor..."
        choco install python -y
    } else {
        # Microsoft Store Python öner
        Write-Warning "Python kurulumu için aşağıdaki seçeneklerden birini kullanın:"
        Write-Info "1. Microsoft Store'dan Python 3.11 kurun"
        Write-Info "2. https://python.org adresinden indirin"
        Write-Info "3. Chocolatey kurup tekrar deneyin: Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))"

        $choice = Read-Host "Otomatik kurulum için (1), Manuel kurulum için (2), Chocolatey için (3) seçin"

        switch ($choice) {
            "1" {
                Start-Process "ms-windows-store://pdp/?ProductId=9NRWMJP3717K"
                Write-Info "Microsoft Store açıldı. Python 3.11 kurulumunu tamamlayıp scripti tekrar çalıştırın."
                exit 0
            }
            "2" {
                Start-Process "https://www.python.org/downloads/"
                Write-Info "Python.org açıldı. Kurulumu tamamlayıp scripti tekrar çalıştırın."
                exit 0
            }
            "3" {
                Install-Chocolatey
                choco install python -y
            }
            default {
                Write-Error "Geçersiz seçim. Script sonlandırılıyor."
                exit 1
            }
        }
    }

    # PATH'i yenile
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")

    # Yeniden test et
    Start-Sleep -Seconds 3
    Test-Python
}

# Chocolatey kurulumu
function Install-Chocolatey {
    Write-Progress "Chocolatey kuruluyor..."
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
}

# Git kontrolü
function Test-Git {
    Write-Progress "Git kurulumu kontrol ediliyor..."

    try {
        $gitVersion = git --version 2>$null
        if ($gitVersion) {
            Write-Success "Git bulundu: $gitVersion"
            $Global:HasGit = $true
        }
    } catch {
        Write-Warning "Git bulunamadı"
        $Global:HasGit = $false

        if (Get-Command choco -ErrorAction SilentlyContinue) {
            Write-Progress "Git kuruluyor..."
            choco install git -y
            $Global:HasGit = $true
        }
    }
}

# Sistem bağımlılıklarını kur
function Install-Dependencies {
    Write-Progress "Sistem bağımlılıkları kuruluyor..."

    if (Get-Command choco -ErrorAction SilentlyContinue) {
        # Tesseract OCR
        Write-Progress "Tesseract OCR kuruluyor..."
        choco install tesseract -y

        # Poppler (PDF to image için)
        Write-Progress "Poppler kuruluyor..."
        choco install poppler -y

        Write-Success "Sistem bağımlılıkları kuruldu"
    } else {
        Write-Warning "Chocolatey bulunamadı. Bağımlılıkları manuel kurmanız gerekebilir:"
        Write-Info "- Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki"
        Write-Info "- Poppler: http://blog.alivate.com.au/poppler-windows/"
    }
}

# Kaynak kodunu indir
function Download-Source {
    Write-Progress "Kaynak kod indiriliyor..."

    $repoUrl = "https://github.com/Fatih-Bucaklioglu/PyPDF-Tools-v2"

    # Kurulum dizinini temizle
    if (Test-Path $InstallPath) {
        if ($Force) {
            Remove-Item $InstallPath -Recurse -Force
        } else {
            $choice = Read-Host "Kurulum dizini mevcut ($InstallPath). Üzerine yaz? (y/N)"
            if ($choice -eq "y" -or $choice -eq "Y") {
                Remove-Item $InstallPath -Recurse -Force
            } else {
                Write-Error "Kurulum iptal edildi"
                exit 1
            }
        }
    }

    New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null

    if ($Global:HasGit) {
        # Git ile indir
        git clone "$repoUrl.git" $InstallPath
    } else {
        # ZIP ile indir
        $zipUrl = "$repoUrl/archive/refs/heads/main.zip"
        $zipPath = "$env:TEMP\pypdf-tools-v2.zip"

        Write-Progress "ZIP dosyası indiriliyor..."
        Invoke-WebRequest -Uri $zipUrl -OutFile $zipPath

        Write-Progress "ZIP dosyası açılıyor..."
        Expand-Archive -Path $zipPath -DestinationPath $env:TEMP -Force

        # Dosyaları taşı
        $extractedPath = "$env:TEMP\PyPDF-Tools-v2-main"
        Get-ChildItem $extractedPath | Move-Item -Destination $InstallPath

        # Temizlik
        Remove-Item $zipPath, $extractedPath -Recurse -Force -ErrorAction SilentlyContinue
    }

    Write-Success "Kaynak kod indirildi: $InstallPath"
}

# Python sanal ortamı oluştur
function Create-VirtualEnvironment {
    Write-Progress "Python sanal ortamı oluşturuluyor..."

    Push-Location $InstallPath

    try {
        & $Global:PythonCommand -m venv venv

        # Sanal ortamı aktifleştir
        & ".\venv\Scripts\Activate.ps1"

        # pip'i güncelle
        & ".\venv\Scripts\python.exe" -m pip install --upgrade pip

        Write-Success "Sanal ortam oluşturuldu"
    } finally {
        Pop-Location
    }
}

# Python paketlerini kur
function Install-PythonPackages {
    Write-Progress "Python paketleri kuruluyor..."

    Push-Location $InstallPath

    try {
        # Sanal ortamda pip ile kur
        & ".\venv\Scripts\python.exe" -m pip install -r requirements.txt

        Write-Success "Python paketleri kuruldu"
    } catch {
        Write-Error "Python paketi kurulumu başarısız: $($_.Exception.Message)"

        # Temel paketleri tek tek dene
        $basicPackages = @("PyPDF2", "Pillow", "reportlab")
        foreach ($package in $basicPackages) {
            try {
                & ".\venv\Scripts\python.exe" -m pip install $package
                Write-Success "$package kuruldu"
            } catch {
                Write-Warning "$package kurulamadı"
            }
        }
    } finally {
        Pop-Location
    }
}

# Başlatma scripti oluştur
function Create-Launcher {
    Write-Progress "Başlatma scripti oluşturuluyor..."

    $launcherPath = "$InstallPath\pypdf-tools-v2.bat"

    $launcherContent = @"
@echo off
cd /d "$InstallPath"
call venv\Scripts\activate.bat
python main.py %*
"@

    Set-Content -Path $launcherPath -Value $launcherContent -Encoding UTF8

    Write-Success "Başlatma scripti oluşturuldu: $launcherPath"
}

# Başlat menüsü kısayolu
function Create-StartMenuShortcut {
    Write-Progress "Başlat menüsü kısayolu oluşturuluyor..."

    $startMenuPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs"
    $shortcutPath = "$startMenuPath\PyPDF-Stirling Tools v2.lnk"
    $targetPath = "$InstallPath\pypdf-tools-v2.bat"
    $iconPath = "$InstallPath\icons\app_icon.ico"

    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut($shortcutPath)
    $Shortcut.TargetPath = $targetPath
    $Shortcut.WorkingDirectory = $InstallPath
    $Shortcut.Description = "Modern PDF İşleme Uygulaması"

    if (Test-Path $iconPath) {
        $Shortcut.IconLocation = $iconPath
    }

    $Shortcut.Save()

    Write-Success "Başlat menüsü kısayolu oluşturuldu"
}

# Masaüstü kısayolu
function Create-DesktopShortcut {
    $choice = Read-Host "Masaüstü kısayolu oluşturulsun mu? (y/N)"

    if ($choice -eq "y" -or $choice -eq "Y") {
        Write-Progress "Masaüstü kısayolu oluşturuluyor..."

        $desktopPath = [Environment]::GetFolderPath("Desktop")
        $shortcutPath = "$desktopPath\PyPDF-Stirling Tools v2.lnk"
        $targetPath = "$InstallPath\pypdf-tools-v2.bat"
        $iconPath = "$InstallPath\icons\app_icon.ico"

        $WshShell = New-Object -ComObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut($shortcutPath)
        $Shortcut.TargetPath = $targetPath
        $Shortcut.WorkingDirectory = $InstallPath
        $Shortcut.Description = "Modern PDF İşleme Uygulaması"

        if (Test-Path $iconPath) {
            $Shortcut.IconLocation = $iconPath
        }

        $Shortcut.Save()

        Write-Success "Masaüstü kısayolu oluşturuldu"
    }
}

# PATH'e ekle
function Add-ToPath {
    Write-Progress "PATH yapılandırması..."

    $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")

    if (-not $currentPath.Contains($InstallPath)) {
        $newPath = "$currentPath;$InstallPath"
        [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")

        # Mevcut oturum için PATH'i güncelle
        $env:PATH += ";$InstallPath"

        Write-Success "PATH'e eklendi: $InstallPath"
    } else {
        Write-Success "PATH zaten yapılandırılmış"
    }
}

# Kurulum testi
function Test-Installation {
    Write-Progress "Kurulum test ediliyor..."

    Push-Location $InstallPath

    try {
        # Python import testleri
        $testScript = @"
import sys
print('Python version:', sys.version)

modules = ['tkinter', 'PyPDF2', 'PIL', 'reportlab']
for module in modules:
    try:
        __import__(module)
        print(f'✅ {module}: OK')
    except ImportError as e:
        print(f'❌ {module}: {e}')
        sys.exit(1)

print('🎉 Tüm bağımlılıklar başarıyla yüklendi!')
"@

        $testScript | & ".\venv\Scripts\python.exe" -

        if ($LASTEXITCODE -eq 0) {
            Write-Success "✅ Kurulum testi başarılı!"
            return $true
        } else {
            Write-Error "❌ Kurulum testi başarısız!"
            return $false
        }
    } catch {
        Write-Error "Test çalıştırılamadı: $($_.Exception.Message)"
        return $false
    } finally {
        Pop-Location
    }
}

# Scripti çalıştır
Install-PyPDFTools

Write-Host "`n🎉 Kurulum tamamlandı!" -ForegroundColor Green
Write-Host "Başlatmak için:" -ForegroundColor Cyan
Write-Host "  - Start Menu: PyPDF-Stirling Tools v2" -ForegroundColor Yellow
Write-Host "  - Terminal: pypdf-tools-v2" -ForegroundColor Yellow
Write-Host "  - PowerShell: & '$InstallPath\pypdf-tools-v2.bat'" -ForegroundColor Yellow

Read-Host "`nDevam etmek için Enter tuşuna basın"
