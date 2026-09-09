"""
Admin Script - Toggle Kill Switch via GitHub Gist.

Cara pakai:
1. Buat GitHub Personal Access Token (https://github.com/settings/tokens)
   - Scope: "gist"
2. Jalankan: python admin.py
3. Ikuti instruksi di layar
"""
import json
import urllib.request
import urllib.error
import os


# Config - edit ini
GIST_ID = ""  # Isi dengan Gist ID kamu
GITHUB_TOKEN = ""  # Isi dengan GitHub token kamu


def load_config():
    """Load config dari file atau input user."""
    global GIST_ID, GITHUB_TOKEN
    
    # Coba load dari file config_admin.json
    config_file = os.path.join(os.path.dirname(__file__), "config_admin.json")
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            config = json.load(f)
            GIST_ID = config.get("gist_id", "")
            GITHUB_TOKEN = config.get("github_token", "")
    
    # Minta input jika kosong
    if not GIST_ID:
        GIST_ID = input("Gist ID: ").strip()
    if not GITHUB_TOKEN:
        GITHUB_TOKEN = input("GitHub Token: ").strip()


def save_config():
    """Simpan config ke file."""
    config_file = os.path.join(os.path.dirname(__file__), "config_admin.json")
    with open(config_file, "w") as f:
        json.dump({
            "gist_id": GIST_ID,
            "github_token": GITHUB_TOKEN
        }, f, indent=2)
    print(f"Config tersimpan ke {config_file}")


def get_gist_content():
    """Ambil isi Gist dari GitHub."""
    url = f"https://api.github.com/gists/{GIST_ID}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    })
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))
            # Ambil isi file pertama
            for filename, file_data in data.get("files", {}).items():
                return json.loads(file_data["content"])
    except urllib.error.HTTPError as e:
        print(f"Error: {e.code} - {e.read().decode()}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def update_gist(content):
    """Update isi Gist di GitHub."""
    url = f"https://api.github.com/gists/{GIST_ID}"
    data = json.dumps({
        "files": {
            "kill_switch.json": {
                "content": json.dumps(content, indent=2)
            }
        }
    }).encode("utf-8")
    
    req = urllib.request.Request(url, data=data, headers={
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    })
    
    try:
        with urllib.request.urlopen(req) as response:
            return True
    except urllib.error.HTTPError as e:
        print(f"Error: {e.code} - {e.read().decode()}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def show_status():
    """Tampilkan status saat ini."""
    print("\n" + "="*50)
    print("  STATUS KILL SWITCH")
    print("="*50)
    
    content = get_gist_content()
    if content is None:
        print("  Gagal mengambil status!")
        return False
    
    is_active = content.get("active", True)
    message = content.get("message", "")
    shutdown_at = content.get("shutdown_at")
    
    status = "ON (Aplikasi aktif)" if is_active else "OFF (Aplikasi mati)"
    color = "\033[92m" if is_active else "\033[91m"  # Green/Red
    reset = "\033[0m"
    
    print(f"\n  Status    : {color}{status}{reset}")
    if message:
        print(f"  Message   : {message}")
    if shutdown_at:
        print(f"  Shutdown  : {shutdown_at}")
    
    print("="*50)
    return True


def toggle_kill_switch():
    """Toggle kill switch on/off."""
    content = get_gist_content()
    if content is None:
        print("Gagal mengambil status!")
        return
    
    current = content.get("active", True)
    new_status = not current
    
    # Minta pesanopsional
    message = input(f"Pesan (Enter untuk skip): ").strip()
    if not message:
        message = content.get("message", "")
    
    # Update
    new_content = {
        "active": new_status,
        "message": message,
        "shutdown_at": content.get("shutdown_at")
    }
    
    if update_gist(new_content):
        status = "ON" if new_status else "OFF"
        print(f"\nKill switch berhasil diubah ke: {status}")
    else:
        print("\nGagal mengupdate kill switch!")


def set_scheduled_shutdown():
    """Set waktu shutdown terjadwal."""
    content = get_gist_content()
    if content is None:
        print("Gagal mengambil status!")
        return
    
    print("\nFormat waktu: YYYY-MM-DDTHH:MM:SS")
    print("Contoh: 2026-09-10T18:00:00")
    shutdown_at = input("Waktu shutdown (Enter untuk hapus): ").strip()
    
    if shutdown_at:
        # Validasi format sederhana
        try:
            from datetime import datetime
            datetime.fromisoformat(shutdown_at)
        except ValueError:
            print("Format waktu tidak valid!")
            return
    else:
        shutdown_at = None
    
    new_content = {
        "active": content.get("active", True),
        "message": content.get("message", ""),
        "shutdown_at": shutdown_at
    }
    
    if update_gist(new_content):
        if shutdown_at:
            print(f"\nShutdown terjadwal: {shutdown_at}")
        else:
            print("\nShutdown terjadwal dihapus")
    else:
        print("\nGagal mengupdate!")


def main():
    """Menu utama."""
    print("\n" + "="*50)
    print("  ADMIN KILL SWITCH - Rekap SKU PDF")
    print("="*50)
    
    load_config()
    
    # Simpan config baru jika pertama kali
    config_file = os.path.join(os.path.dirname(__file__), "config_admin.json")
    if not os.path.exists(config_file):
        save_config()
    
    while True:
        print("\nMenu:")
        print("  1. Lihat Status")
        print("  2. Toggle ON/OFF")
        print("  3. Set Shutdown Terjadwal")
        print("  4. Update Config")
        print("  0. Keluar")
        
        choice = input("\nPilih (0-4): ").strip()
        
        if choice == "1":
            show_status()
        elif choice == "2":
            toggle_kill_switch()
        elif choice == "3":
            set_scheduled_shutdown()
        elif choice == "4":
            save_config()
        elif choice == "0":
            print("Bye!")
            break
        else:
            print("Pilihan tidak valid!")


if __name__ == "__main__":
    main()
