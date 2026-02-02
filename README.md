# Aurivo Medya Player

Aurivo Medya Player; müzik çalma, web sekmesi (YouTube/YouTube Music vb.) ve gelişmiş DSP/ses efektleri (EQ, PEQ, limiter, reverb…) gibi özellikleri tek arayüzde birleştiren Electron tabanlı bir medya oynatıcıdır.

## Ekran Görüntüleri

<p align="center">
  <img src="screenshots/Ekran%20G%C3%B6r%C3%BCnt%C3%BCs%C3%BC_20260203_012651.png" width="32%" alt="Screenshot 1" />
  <img src="screenshots/Ekran%20G%C3%B6r%C3%BCnt%C3%BCs%C3%BC_20260203_012729.png" width="32%" alt="Screenshot 2" />
  <img src="screenshots/Ekran%20G%C3%B6r%C3%BCnt%C3%BCs%C3%BC_20260203_012803.png" width="32%" alt="Screenshot 3" />
  <img src="screenshots/Ekran%20G%C3%B6r%C3%BCnt%C3%BCs%C3%BC_20260203_012822.png" width="32%" alt="Screenshot 4" />
  <img src="screenshots/Ekran%20G%C3%B6r%C3%BCnt%C3%BCs%C3%BC_20260203_012847.png" width="32%" alt="Screenshot 5" />
  <img src="screenshots/Ekran%20G%C3%B6r%C3%BCnt%C3%BCs%C3%BC_20260203_012905.png" width="32%" alt="Screenshot 6" />
  <img src="screenshots/Ekran%20G%C3%B6r%C3%BCnt%C3%BCs%C3%BC_20260203_012919.png" width="32%" alt="Screenshot 7" />
  <img src="screenshots/Ekran%20G%C3%B6r%C3%BCnt%C3%BCs%C3%BC_20260203_012932.png" width="32%" alt="Screenshot 8" />
</p>

## Kurulum

### 1) Node.js bağımlılıkları

```bash
npm install
```

### 2) Python bağımlılıkları (indirici altyapısı için)

`Aurivo-Dawlod/` içindeki indirme altyapısı `yt-dlp` kullanır.

```bash
pip install -r requirements.txt
```

> Not: Bazı dönüştürme/kapak gömme işlemleri için sisteminizde `ffmpeg` kurulu olmalıdır.

## Çalıştırma

```bash
npm run dev
```

