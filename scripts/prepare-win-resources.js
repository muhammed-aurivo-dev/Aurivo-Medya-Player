const fs = require('fs');
const path = require('path');

function ensureDir(p) {
  fs.mkdirSync(p, { recursive: true });
}

function copyIfExists(from, to) {
  if (!fs.existsSync(from)) return false;
  ensureDir(path.dirname(to));
  fs.copyFileSync(from, to);
  return true;
}

function copyVisualizerDllsFromDir(dllDir, nativeDistDir) {
  if (!dllDir) return { copied: 0, skipped: 0 };
  if (!fs.existsSync(dllDir)) {
    console.warn('[prepare-win-resources] AURIVO_VISUALIZER_DLL_DIR bulunamadı:', dllDir);
    return { copied: 0, skipped: 0 };
  }

  ensureDir(nativeDistDir);

  const allowList = new Set([
    'sdl2.dll',
    'sdl2_image.dll',
    'libwinpthread-1.dll',
    'libgcc_s_seh-1.dll',
    'libstdc++-6.dll',
    'zlib1.dll',
    'libpng16-16.dll',
    'libjpeg-8.dll'
  ]);

  const shouldCopy = (name) => {
    const lower = String(name || '').toLowerCase();
    if (!lower.endsWith('.dll')) return false;
    if (allowList.has(lower)) return true;
    if (lower.startsWith('sdl2')) return true;
    if (lower.includes('projectm')) return true;
    // libprojectM-4.dll / projectM-4.dll variants
    if (lower.startsWith('libprojectm') || lower.startsWith('projectm')) return true;
    return false;
  };

  let copied = 0;
  let skipped = 0;

  for (const entry of fs.readdirSync(dllDir, { withFileTypes: true })) {
    if (!entry.isFile()) continue;
    if (!shouldCopy(entry.name)) {
      skipped++;
      continue;
    }
    const from = path.join(dllDir, entry.name);
    const to = path.join(nativeDistDir, entry.name);
    try {
      fs.copyFileSync(from, to);
      copied++;
    } catch (e) {
      console.warn('[prepare-win-resources] DLL kopyalanamadı:', entry.name, e?.message || e);
    }
  }

  if (copied) {
    console.log('[prepare-win-resources] Visualizer DLL\'leri kopyalandı:', { from: dllDir, to: nativeDistDir, copied });
  }

  return { copied, skipped };
}

function main() {
  const root = path.resolve(__dirname, '..');

  const binDir = path.join(root, 'bin');
  ensureDir(binDir);

  const ffmpegSrc = path.join(root, 'third_party', 'ffmpeg', 'ffmpeg.exe');
  const ffmpegDst = path.join(binDir, 'ffmpeg.exe');
  const copiedFfmpeg = copyIfExists(ffmpegSrc, ffmpegDst);

  if (!copiedFfmpeg) {
    console.warn('[prepare-win-resources] ffmpeg.exe bulunamadı:', ffmpegSrc);
  } else {
    const size = fs.statSync(ffmpegDst).size;
    if (size === 0) {
      console.warn('[prepare-win-resources] ffmpeg.exe 0 bayt (placeholder). Gerçek ffmpeg.exe ile değiştirin:', ffmpegDst);
    } else {
      console.log('[prepare-win-resources] ffmpeg.exe kopyalandı:', ffmpegDst);
    }
  }

  const nativeDistDir = path.join(root, 'native-dist');
  if (!fs.existsSync(nativeDistDir)) {
    console.warn('[prepare-win-resources] native-dist dizini yok:', nativeDistDir);
  } else {
    const hasExe = fs.existsSync(path.join(nativeDistDir, 'aurivo-projectm-visualizer.exe'));
    if (!hasExe) {
      console.warn('[prepare-win-resources] Visualizer exe yok (Windows build için gerekli):', path.join(nativeDistDir, 'aurivo-projectm-visualizer.exe'));
    }
  }

  // Optional: copy visualizer runtime DLLs (MSYS2/MinGW etc.)
  // Example: set AURIVO_VISUALIZER_DLL_DIR="C:\\msys64\\mingw64\\bin"
  try {
    const dllDir = process.env.AURIVO_VISUALIZER_DLL_DIR || '';
    if (dllDir) {
      copyVisualizerDllsFromDir(dllDir, nativeDistDir);
    }
  } catch (e) {
    console.warn('[prepare-win-resources] Visualizer DLL kopyalama hatası:', e?.message || e);
  }
}

main();
