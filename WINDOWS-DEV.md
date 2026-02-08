# Aurivo Windows Development Branch

Bu branch **Windows 10/11** için Aurivo Media Player geliştirme ve testine odaklanmıştır.

## Branch Yapısı

- **`main`** - Linux sürümü (stabil)
- **`windows-native`** (bu branch) - Windows-specific geliştirmeler

## Kurulum (Windows)

### Gereksinimler
- Node.js 18+ (LTS önerilir)
- Visual Studio 2022 Community (C++ build tools)
- Git for Windows
- Python 3.10+ (native build için)
- ffmpeg (PATH'te)

### Adımlar
```bash
git clone https://github.com/muhammed-aurivo-dev/Aurivo-Medya-Player.git
cd Aurivo-Medya-Player
git checkout windows-native

# Bağımlılıkları kur
npm install
npm --prefix native install

# Rebuild native addon
npm run rebuild-native

# Geliştirme modunda çalıştır
npm run dev
```

## Build (Windows Installer)
```bash
# Windows NSIS installer oluştur
npm run build:win

# Veya ZIP dosyası
npm run build:win:zip
```

## Bilinen Sorunlar

### Ses Çıkmaması
- ✓ BASS DLL'leri `native/build/Release/` içinde olduğundan emin ol
- ✓ Visual C++ Redistributable (x64) yüklü mü?
- ✓ Windows sesini mute etmediysen kontrol et

### Görselleştirici (Visualizer) Eksik
- ProjectM visualizer exe'si isteğe bağlı (optional)
- Fallback mekanizması CSS animasyon kullanır

## Windows-Specific Kod

### DLL Yükleme Yolları
- **audioEngine.js** - `ensureBassPathsOnWindows()` 
- **main.js** - `ensureWindowsRuntimePaths()`
- **package.json** - Windows `extraResources` konfigürasyonu

### Diagnostik
DevTools Console'da:
```javascript
// Ses API'si kullanılabilir mi?
window.aurivo.audio.isNativeAvailable()

// Ses seviyesi kontrol
await window.aurivo.audio.getVolume()
await window.aurivo.audio.setVolume(0.5)

// Çalıyor mu?
await window.aurivo.audio.isPlaying()
```

## Gönderime Hazırlık (Windows Test)

1. Lokalte build et: `npm run build:win`
2. `dist/` klasöründe installer'ı bul
3. Farklı bir Windows makinesinde test et
4. Sorunları GitHub Issues'da rapor et

## Ana Branch'e Merge

Windows kararlı olduğunda:
```bash
git checkout main
git merge windows-native
```

---

Sorular veya hata raporları: GitHub Issues
