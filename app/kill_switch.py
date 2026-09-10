"""
Remote Kill Switch - kontrol akses via GitHub Gist.

Developer membuat GitHub Gist dengan isi JSON:
{
    "active": true,
    "message": "",
    "shutdown_at": null
}

Ketika developer ingin mematikan app:
- Set "active": false → app langsung mati
- Atau set "shutdown_at": "2026-08-22T18:00:00" → app mati di waktu itu

Cara pakai:
1. Buat GitHub Gist baru
2. Isi dengan JSON di atas
3. Copy Gist ID (bagian dari URL: https://gist.github.com/user/GIST_ID)
4. Set Gist ID di config.py
5. Set Gist sebagai public agar bisa diakses tanpa auth
"""

import time

import json
import os
import sys
import shutil
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path


def _get_log_path():
    """Get path for kill switch log file."""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent / "kill_switch.log"
    return Path(__file__).parent.parent / "kill_switch.log"


def _log(message):
    """Write log entry."""
    try:
        log_path = _get_log_path()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        pass


def _get_cache_path():
    """Get path for local cache file."""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent / ".ks_cache.json"
    return Path(__file__).parent.parent / ".ks_cache.json"


def _load_cache():
    """Load cached kill switch state."""
    try:
        cache_path = _get_cache_path()
        if cache_path.exists():
            with open(cache_path, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return None


def _save_cache(data):
    """Save kill switch state to local cache."""
    try:
        cache_path = _get_cache_path()
        with open(cache_path, "w") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


def get_kill_switch_config():
    """Ambil konfigurasi kill switch dari GitHub Gist."""
    try:
        from config import KILL_SWITCH_GIST_ID, KILL_SWITCH_ENABLED

        if not KILL_SWITCH_ENABLED:
            _log("Kill switch disabled in config")
            return {"active": True, "message": "Kill switch disabled", "shutdown_at": None}

        if not KILL_SWITCH_GIST_ID or KILL_SWITCH_GIST_ID == "YOUR_GIST_ID_HERE":
            _log("No Gist ID configured")
            return {"active": True, "message": "No Gist ID configured", "shutdown_at": None}

        cache_bust = int(time.time())
        url = f"https://gist.githubusercontent.com/raw/{KILL_SWITCH_GIST_ID}?t={cache_bust}"
        _log(f"Fetching: {url}")
        req = urllib.request.Request(url, headers={"User-Agent": "RekapSKU/1.0"})
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
            _log(f"Gist response: {data}")

            # Cache successful response
            _save_cache(data)

            # If gist says active:false, delete cache (no bypass)
            if not data.get("active", True):
                try:
                    _get_cache_path().unlink(missing_ok=True)
                except Exception:
                    pass

            return data

    except urllib.error.URLError as e:
        _log(f"Network error: {type(e).__name__}: {e}")

        # Network fail: check cache for fail-open behavior
        cache = _load_cache()
        if cache and cache.get("active", True):
            _log(f"Using cached state (active:true) - allowing app")
            return {"active": True, "message": "Mode offline", "shutdown_at": None}

        # No cache or cache says inactive: fail-closed
        _log("No valid cache - blocking app")
        return {"active": False, "message": "Tidak dapat memverifikasi lisensi. Periksa koneksi internet.", "shutdown_at": None}
    except json.JSONDecodeError as e:
        _log(f"JSON error: {e}")
        return {"active": False, "message": "Konfigurasi kill switch tidak valid.", "shutdown_at": None}
    except Exception as e:
        _log(f"Unknown error: {type(e).__name__}: {e}")
        return {"active": False, "message": f"Error verifikasi: {e}", "shutdown_at": None}


def check_kill_switch():
    """
    Cek apakah app masih boleh jalan.
    Return (can_run: bool, message: str)
    """
    config = get_kill_switch_config()

    # Cek apakah active
    if not config.get("active", True):
        return False, config.get("message", "Aplikasi telah dinonaktifkan oleh developer.")

    # Cek shutdown_at
    shutdown_at = config.get("shutdown_at")
    if shutdown_at:
        try:
            shutdown_time = datetime.fromisoformat(shutdown_at)
            if datetime.now() >= shutdown_time:
                return False, config.get("message", f"Aplikasi dimatikan pada {shutdown_at}")
        except ValueError:
            pass

    return True, config.get("message", "OK")


def self_destruct():
    """
    Hapus file aplikasi secara lokal (self-destruct).
    Hanya dijalankan saat running as source code, BUKAN saat EXE.
    """
    # Skip self-destruct jika running as EXE
    if getattr(sys, 'frozen', False):
        return []

    app_dir = Path(__file__).parent
    project_dir = app_dir.parent

    # File yang akan dihapus
    files_to_delete = [
        project_dir / "app",
        project_dir / "config.py",
        project_dir / "requirements.txt",
        project_dir / "run.py",
    ]

    deleted = []
    for f in files_to_delete:
        try:
            if f.is_dir():
                shutil.rmtree(f)
            elif f.is_file():
                f.unlink()
            deleted.append(str(f))
        except Exception:
            pass

    return deleted
