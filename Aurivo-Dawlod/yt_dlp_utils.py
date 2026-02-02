import importlib.util
import os
import shutil
import sys
from pathlib import Path


def _is_youtube_url(url: str) -> bool:
    u = (url or "").strip().lower()
    return "youtube.com/" in u or "music.youtube.com/" in u or "youtu.be/" in u


def resolve_yt_dlp_command():
    """
    Prefer repo-local yt-dlp; fall back to PATH or python -m yt_dlp.
    Returns command list or None if not found.
    """
    candidates = []
    exe_dir = os.path.dirname(sys.executable)
    repo_root = os.path.dirname(os.path.abspath(__file__))

    # Optional local venv (if user creates it)
    candidates.append(os.path.join(repo_root, "pyqt_venv", "bin", "yt-dlp"))
    candidates.append(os.path.join(repo_root, "pyqt_venv", "Scripts", "yt-dlp.exe"))

    for name in ("yt-dlp", "yt_dlp"):
        candidates.append(os.path.join(exe_dir, name))
        candidates.append(shutil.which(name))

    candidates.append(os.path.join(repo_root, "yt-dlp"))
    candidates.append(os.path.join(repo_root, "yt-dlp.exe"))

    for cand in candidates:
        if cand and os.path.exists(cand) and os.access(cand, os.X_OK):
            return [cand]

    try:
        if importlib.util.find_spec("yt_dlp"):
            return [sys.executable, "-m", "yt_dlp"]
    except Exception:
        pass

    return None


def build_yt_dlp_command(
    *,
    url: str,
    mode: str,
    output_dir: str,
    video_format: str | None = None,
    audio_format: str = "mp3",
    audio_quality: str = "192",
    youtube_player_client: str | None = None,
    cookies_path: str | None = None,
    cookies_from_browser: str | None = None,
    normalize_audio: bool = False,
    proxy: str | None = None,
    config_path: str | None = None,
    format_override: str | None = None,
    extra_args: list[str] | None = None,
    no_playlist: bool = True,
    playlist_filename_format: str = "%(playlist_index)s.%(title)s.%(ext)s",
    playlist_foldername_format: str = "%(playlist_title)s",
    video_height: int | None = None,
    video_codec: str | None = None,
) -> list[str]:
    cmd_base = resolve_yt_dlp_command()
    if not cmd_base:
        raise RuntimeError(
            "yt-dlp bulunamadı. Lütfen `python -m pip install yt-dlp` kurun veya PATH'e `yt-dlp` ekleyin."
        )

    output_dir = str(output_dir or "").strip()
    if not output_dir:
        raise ValueError("output_dir boş")

    # Ensure output exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    cmd: list[str] = list(cmd_base)
    cmd += ["--newline"]
    if no_playlist:
        cmd += ["--no-playlist"]

    # Cookies support (optional)
    cpath = str(cookies_path or "").strip()
    if cpath:
        cmd += ["--cookies", cpath]
    cb = str(cookies_from_browser or "").strip()
    if cb:
        # Example: chrome, chromium, firefox, edge, opera...
        cmd += ["--cookies-from-browser", cb]

    prx = str(proxy or "").strip()
    if prx:
        cmd += ["--proxy", prx]

    cfg = str(config_path or "").strip()
    if cfg:
        cmd += ["--config-location", cfg]

    if not no_playlist:
        folder_fmt = str(playlist_foldername_format or "%(playlist_title)s").strip() or "%(playlist_title)s"
        file_fmt = str(playlist_filename_format or "%(playlist_index)s.%(title)s.%(ext)s").strip() or "%(playlist_index)s.%(title)s.%(ext)s"
        out_tmpl = os.path.join(output_dir, folder_fmt, file_fmt)
    else:
        out_tmpl = os.path.join(output_dir, "%(title)s.%(ext)s")
    cmd += ["-o", out_tmpl]

    # YouTube client workaround (SABR / 403 bazı durumlarda)
    if _is_youtube_url(url):
        client = str(youtube_player_client or "android").strip().lower()
        if client:
            cmd += ["--extractor-args", f"youtube:player_client={client}"]

    m = (mode or "").strip().lower()
    if m == "audio":
        fov = str(format_override or "").strip()
        if fov:
            cmd += ["-f", fov]

        afmt = str(audio_format or "mp3").lower()
        cmd += ["-x", "--audio-format", afmt]

        q = str(audio_quality or "").strip()
        if q.isdigit() and int(q) > 10:
            cmd += ["--audio-quality", f"{q}K"]
        else:
            cmd += ["--audio-quality", "0"]

        # Thumbnails: MP3 embedding is more reliable with jpg
        if afmt == "mp3":
            cmd += ["--convert-thumbnails", "jpg"]

        cmd += ["--embed-thumbnail", "--add-metadata"]

        # Loudness normalization (requires ffmpeg). Helps "ses zayıf" downloads.
        # Target: streaming-friendly loudness.
        if normalize_audio:
            # IMPORTANT: scope args to audio extract postprocessor only.
            # Using generic "ffmpeg:" can break other ffmpeg postprocessors (e.g. embed-thumbnail).
            loudnorm = "loudnorm=I=-14:TP=-1.5:LRA=11"
            cmd += ["--postprocessor-args", f"ExtractAudio:-af {loudnorm}"]
            cmd += ["--postprocessor-args", f"FFmpegExtractAudio:-af {loudnorm}"]
    else:
        fov = str(format_override or "").strip()
        if fov:
            vf = fov
        else:
            # Build format from preferred height/codec (ytDownloader-style)
            filters: list[str] = []
            if isinstance(video_height, int) and video_height > 0:
                filters.append(f"height<={video_height}")
            vcodec = str(video_codec or "").strip()
            if vcodec:
                filters.append(f"vcodec^={vcodec}")

            if filters:
                vsel = "bestvideo[" + "][".join(filters) + "]"
                if isinstance(video_height, int) and video_height > 0:
                    vf = f"{vsel}+bestaudio/best[height<={video_height}]/best"
                else:
                    vf = f"{vsel}+bestaudio/best"
            else:
                vf = str(video_format or "bestvideo+bestaudio/best")

        cmd += ["-f", vf, "--embed-thumbnail", "--add-metadata"]

    # Allow power users to pass extra yt-dlp args (best-effort). This comes last so it can override defaults.
    if extra_args:
        for a in extra_args:
            if a is None:
                continue
            s = str(a).strip()
            if s:
                cmd.append(s)

    cmd.append(str(url).strip())
    return cmd
