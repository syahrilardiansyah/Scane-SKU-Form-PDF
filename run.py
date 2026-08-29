"""
Run - Entry point aplikasi.
Cek kill switch sebelum menjalankan app utama.
"""
import sys
import tkinter.messagebox as messagebox


def main():
    # Cek kill switch
    try:
        from app.kill_switch import check_kill_switch, self_destruct
        can_run, message = check_kill_switch()

        if not can_run:
            # Tampilkan pesan error
            try:
                import customtkinter as ctk
                root = ctk.CTk()
                root.withdraw()
                messagebox.showerror("Aplikasi Dinonaktifkan", message)
                root.destroy()
            except Exception:
                print(f"ERROR: {message}")

            # Self-destruct
            try:
                deleted = self_destruct()
                if deleted:
                    print(f"File dihapus: {', '.join(deleted)}")
            except Exception:
                pass

            sys.exit(1)
    except ImportError:
        pass

    # Jalankan app utama
    from app.main import run
    run()


if __name__ == "__main__":
    main()
