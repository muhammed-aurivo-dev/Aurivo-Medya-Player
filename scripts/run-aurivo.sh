#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

# Projedeki start scripti Wayland ortam değişkenlerini zaten ayarlıyor
exec npm start
