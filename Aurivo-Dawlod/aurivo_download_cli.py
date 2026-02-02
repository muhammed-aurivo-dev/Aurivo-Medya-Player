from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys

from yt_dlp_utils import build_yt_dlp_command


def _looks_like_retryable_youtube_error(line: str) -> bool:
    s = (line or "").lower()
    return (
        "http error 403" in s
        or "403" in s and "forbidden" in s
        or "unable to download video data" in s
        or "forcing sabr streaming" in s
    )


def _is_youtube_url(url: str) -> bool:
    u = (url or "").strip().lower()
    return "youtube.com/" in u or "music.youtube.com/" in u or "youtu.be/" in u


def _run_and_stream(cmd: list[str]) -> tuple[int, bool, bool]:
    """
    Runs yt-dlp and streams stdout; returns (exit_code, saw_retryable_error, saw_ffmpeg_missing).
    """
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True,
    )

    saw_retryable = False
    saw_ffmpeg_missing = False
    assert proc.stdout is not None
    for line in proc.stdout:
        if _looks_like_retryable_youtube_error(line):
            saw_retryable = True
        if ("ffmpeg" in (line or "").lower()) and ("not found" in (line or "").lower() or "ffprobe" in (line or "").lower()):
            saw_ffmpeg_missing = True
        sys.stdout.write(line)
        sys.stdout.flush()

    return int(proc.wait() or 0), saw_retryable, saw_ffmpeg_missing


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="aurivo_download_cli")
    p.add_argument("--url", required=True)
    p.add_argument("--mode", choices=["video", "audio"], default="video")
    p.add_argument("--output", required=True)

    # Video
    p.add_argument("--video-height", default="", help="Max video height (e.g. 1080)")
    p.add_argument("--video-codec", default="", help="Preferred video codec (avc1/av01/vp9/mp4v)")

    # Audio
    p.add_argument("--audio-format", default="mp3")
    p.add_argument("--audio-quality", default="192")
    p.add_argument("--normalize-audio", action="store_true", help="ffmpeg loudnorm uygula (daha yüksek/denge ses)")

    # Advanced
    p.add_argument("--proxy", default="")
    p.add_argument("--cookies", default="", help="Path to cookies.txt")
    p.add_argument("--cookies-from-browser", default="", help="Browser name for cookies extraction")
    p.add_argument("--config", default="", help="yt-dlp config file path")
    p.add_argument("--custom-args", default="", help="Custom yt-dlp args (single string)")
    p.add_argument("--format-override", default="", help="Override yt-dlp -f format string/id")

    # Playlist
    p.add_argument("--playlist", action="store_true", help="Allow playlists (default is no-playlist)")
    p.add_argument("--playlist-filename-format", default="%(playlist_index)s.%(title)s.%(ext)s")
    p.add_argument("--playlist-foldername-format", default="%(playlist_title)s")

    args = p.parse_args(argv)

    cookies_path = (args.cookies or os.environ.get("AURIVO_YTDLP_COOKIES") or "").strip()
    cookies_from_browser = (args.cookies_from_browser or os.environ.get("AURIVO_YTDLP_COOKIES_FROM_BROWSER") or "").strip()

    proxy = (args.proxy or "").strip()
    config_path = (args.config or "").strip()
    format_override = (args.format_override or "").strip()

    # Custom args parsing (best-effort)
    extra_args: list[str] = []
    if args.custom_args and str(args.custom_args).strip():
        raw = str(args.custom_args).strip()
        try:
            extra_args = shlex.split(raw, posix=(os.name != "nt"))
        except Exception:
            extra_args = [raw]

    video_height: int | None = None
    if args.video_height and str(args.video_height).strip().isdigit():
        video_height = int(str(args.video_height).strip())

    video_codec = (args.video_codec or "").strip()

    # YouTube bazen client'a göre 403/SABR verebiliyor. Sırayla dene.
    youtube_clients = ["android", "ios", "web"] if _is_youtube_url(args.url) else [None]

    last_code = 1
    saw_retryable_any = False
    saw_ffmpeg_missing_any = False

    for attempt_idx, client in enumerate(youtube_clients, start=1):
        if client:
            sys.stdout.write(f"[aurivo] Deneme {attempt_idx}/{len(youtube_clients)} (YouTube client: {client})\n")
            sys.stdout.flush()

        cmd = build_yt_dlp_command(
            url=args.url,
            mode=args.mode,
            output_dir=args.output,
            audio_format=args.audio_format,
            audio_quality=args.audio_quality,
            youtube_player_client=client,
            cookies_path=cookies_path or None,
            cookies_from_browser=cookies_from_browser or None,
            normalize_audio=bool(args.normalize_audio),
            proxy=proxy or None,
            config_path=config_path or None,
            format_override=format_override or None,
            extra_args=extra_args,
            no_playlist=not bool(args.playlist),
            playlist_filename_format=(args.playlist_filename_format or "").strip() or "%(playlist_index)s.%(title)s.%(ext)s",
            playlist_foldername_format=(args.playlist_foldername_format or "").strip() or "%(playlist_title)s",
            video_height=video_height,
            video_codec=video_codec or None,
        )

        code, saw_retryable, saw_ffmpeg_missing = _run_and_stream(cmd)
        last_code = code
        saw_retryable_any = saw_retryable_any or saw_retryable
        saw_ffmpeg_missing_any = saw_ffmpeg_missing_any or saw_ffmpeg_missing

        if code == 0:
            return 0

        # Retry only when it looks like the YouTube issue we can work around.
        if not saw_retryable:
            break

        if attempt_idx < len(youtube_clients):
            sys.stdout.write("[aurivo] İndirme hatası, alternatif client ile tekrar deneniyor...\n")
            sys.stdout.flush()

    if saw_retryable_any and last_code != 0:
        sys.stdout.write(
            "[aurivo] Not: Bu hata genelde YouTube taraflı 403/SABR kaynaklıdır. "
            "Çözüm olarak `yt-dlp` güncellemek veya cookie kullanmak gerekebilir.\n"
        )
        sys.stdout.write(
            "[aurivo] Cookie için: AURIVO_YTDLP_COOKIES=/path/cookies.txt veya "
            "AURIVO_YTDLP_COOKIES_FROM_BROWSER=chrome (veya chromium/firefox) ayarlayabilirsiniz.\n"
        )
        sys.stdout.flush()

    if saw_ffmpeg_missing_any and last_code != 0:
        sys.stdout.write(
            "[aurivo] Not: Ses dönüştürme/thumbnail/embed için `ffmpeg` gerekebilir. "
            "Sisteminize ffmpeg kurup tekrar deneyin.\n"
        )
        sys.stdout.flush()

    return int(last_code or 1)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
