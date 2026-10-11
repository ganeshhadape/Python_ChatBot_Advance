import os
import sys
import shutil
import subprocess
import tkinter as tk
from tkinter import filedialog

# =====================================================================
# PNG -> ICO + SPLASH_LOGO.PNG + AI_Chatbot_GKH.exe + AI_Chatbot_By_GKH.exe
# Owner & Copyright Holder: Ganesh K. Hadpe
# =====================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()

# Automatically find chatbot_3.py, chatbot.py, or chatbot_2.py
CHATBOT_SCRIPT = ""
for candidate_name in ("chatbot_3.py", "chatbot.py", "chatbot_2.py"):
    candidate_path = os.path.join(BASE_DIR, candidate_name)
    if os.path.exists(candidate_path):
        CHATBOT_SCRIPT = candidate_path
        break

ICO_OUTPUT = os.path.join(BASE_DIR, "app_icon.ico")
SPLASH_PNG_OUTPUT = os.path.join(BASE_DIR, "splash_logo.png")

# Your custom executable names — synchronized across the App, Setup Wizard, and Uninstaller
APP_EXE_NAME = "AI_Chatbot_GKH"
UNINSTALL_EXE_NAME = "Uninstall"
SETUP_EXE_NAME = "AI_Chatbot_By_GKH"

VERSION_FILE = os.path.join(BASE_DIR, "version_info.txt")
LICENSE_FILE = os.path.join(BASE_DIR, "LICENSE.txt")
UNINSTALL_SCRIPT = os.path.join(BASE_DIR, "_uninstaller_temp.py")
SETUP_SCRIPT = os.path.join(BASE_DIR, "_setup_wizard_temp.py")

LICENSE_TEXT = """========================================================================
SOFTWARE LICENSE AGREEMENT
Application: AI Chatbot & Study Studio (Windows Desktop Edition)
Author & Copyright Holder: Ganesh K. Hadpe
Copyright (c) 2026 Ganesh K. Hadpe. All Rights Reserved.
========================================================================

1. GRANT OF LICENSE
Permission is hereby granted by Ganesh K. Hadpe to install and use this
standalone software application for educational, personal, and productivity
purposes on any Windows computer.

2. CREATOR ATTRIBUTION
The creator attribution ("Made with love by Ganesh K. Hadpe") and this
copyright notice must remain intact in all copies of the Software.

3. OFFLINE PRIVACY & SECURITY
This software runs 100% locally on your Windows PC using an isolated
localhost loopback engine (127.0.0.1). No personal files or chats are
sent to external servers.
"""


def get_version_metadata(internal_name: str, orig_filename: str, description: str) -> str:
    return f"""# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(filevers=(3, 0, 0, 0), prodvers=(3, 0, 0, 0), mask=0x3f, flags=0x0, OS=0x40004, fileType=0x1, subtype=0x0, date=(0, 0)),
  kids=[
    StringFileInfo([
      StringTable('040904B0', [
        StringStruct('CompanyName', 'Ganesh K. Hadpe'),
        StringStruct('FileDescription', '{description}'),
        StringStruct('FileVersion', '3.0.0'),
        StringStruct('InternalName', '{internal_name}'),
        StringStruct('LegalCopyright', 'Copyright (c) 2026 Ganesh K. Hadpe. All Rights Reserved.'),
        StringStruct('OriginalFilename', '{orig_filename}'),
        StringStruct('ProductName', 'AI Chatbot By Ganesh K. Hadpe'),
        StringStruct('ProductVersion', '3.0.0')
      ])
    ]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)"""


# =====================================================================
# TEMPLATE 1: STANDALONE UNINSTALL.EXE GUI & SELF-CLEANUP ENGINE
# =====================================================================
UNINSTALLER_TEMPLATE = '''import os
import io
import sys
import shutil
import winreg
import tempfile
import subprocess
import tkinter as tk
from tkinter import messagebox

if sys.stdout is None:
    sys.stdout = io.StringIO()
if sys.stderr is None:
    sys.stderr = io.StringIO()

IS_FROZEN = getattr(sys, "frozen", False)
if IS_FROZEN:
    _meipass = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(sys.executable)))
    for _tcl_cand in ("_tcl_data", "tcl8.6", os.path.join("tcl", "tcl8.6")):
        _p = os.path.join(_meipass, _tcl_cand)
        if os.path.isdir(_p):
            os.environ["TCL_LIBRARY"] = _p
            break
    for _tk_cand in ("_tk_data", "tk8.6", os.path.join("tcl", "tk8.6")):
        _p = os.path.join(_meipass, _tk_cand)
        if os.path.isdir(_p):
            os.environ["TK_LIBRARY"] = _p
            break

INSTALL_DIR = (
    os.path.dirname(os.path.abspath(sys.executable))
    if IS_FROZEN
    else os.path.dirname(os.path.abspath(__file__))
)
BUNDLED_DIR = getattr(sys, "_MEIPASS", INSTALL_DIR)

# Synchronized dynamically with APP_EXE_NAME ("AI_Chatbot_GKH.exe")
APP_EXE_FILENAME = "__APP_EXE_FILENAME__"
UNINSTALL_EXE_FILENAME = "__UNINSTALL_EXE_FILENAME__"
ICON_FILENAME = "app_icon.ico"
SPLASH_FILENAME = "splash_logo.png"
REGISTRY_KEY_PATH = r"Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\AI_Chatbot_GKH"


class GaneshUninstallerWizard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Uninstall — AI Chatbot By Ganesh K. Hadpe")
        self.geometry("540x320")
        self.resizable(False, False)
        self.configure(bg="#0f172a")

        for ico_cand in (os.path.join(INSTALL_DIR, ICON_FILENAME), os.path.join(BUNDLED_DIR, ICON_FILENAME)):
            if os.path.exists(ico_cand):
                try:
                    self.iconbitmap(ico_cand)
                    break
                except Exception:
                    pass

        self.remove_user_data_var = tk.BooleanVar(value=True)
        self._build_ui()

    def _build_ui(self):
        header = tk.Frame(self, bg="#1e293b", padx=20, pady=14)
        header.pack(fill="x")

        tk.Label(
            header, text="🗑️ Uninstall AI Chatbot & Study Studio",
            bg="#1e293b", fg="#f8fafc", font=("Segoe UI", 13, "bold"), anchor="w"
        ).pack(fill="x")

        tk.Label(
            header, text="❤️ Made with love by Ganesh K. Hadpe",
            bg="#1e293b", fg="#fde047", font=("Segoe UI", 9, "bold"), anchor="w"
        ).pack(fill="x", pady=(2, 0))

        body = tk.Frame(self, bg="#0f172a", padx=20, pady=16)
        body.pack(fill="both", expand=True)

        tk.Label(
            body,
            text=f"Folder to remove:\\n{INSTALL_DIR}",
            bg="#0f172a", fg="#94a3b8", font=("Consolas", 9), justify="left", anchor="w"
        ).pack(fill="x", pady=(0, 14))

        tk.Checkbutton(
            body,
            text="Also delete downloaded AI models, chat history & saved study notes",
            variable=self.remove_user_data_var,
            bg="#0f172a", fg="#e2e8f0", selectcolor="#1e293b",
            activebackground="#0f172a", activeforeground="#4ade80",
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", pady=(0, 8))

        tk.Label(
            body,
            text="Uncheck the box above if you want to keep My_Study_Notes.txt and chat_history.db.",
            bg="#0f172a", fg="#64748b", font=("Segoe UI", 8), anchor="w"
        ).pack(fill="x")

        footer = tk.Frame(self, bg="#1e293b", padx=20, pady=10)
        footer.pack(fill="x", side="bottom")

        tk.Button(
            footer, text="Cancel", bg="#334155", fg="white",
            activebackground="#475569", activeforeground="white",
            font=("Segoe UI", 9, "bold"), relief="flat", width=10, pady=5,
            cursor="hand2", command=self.destroy
        ).pack(side="right", padx=(8, 0))

        self.uninstall_btn = tk.Button(
            footer, text="Uninstall Now", bg="#dc2626", fg="white",
            activebackground="#b91c1c", activeforeground="white",
            font=("Segoe UI", 9, "bold"), relief="flat", width=14, pady=5,
            cursor="hand2", command=self._perform_uninstall
        )
        self.uninstall_btn.pack(side="right")

    def _perform_uninstall(self):
        if not messagebox.askyesno(
            "Confirm Uninstall",
            "Are you sure you want to uninstall AI Chatbot By Ganesh K. Hadpe from this computer?"
        ):
            return

        self.uninstall_btn.configure(state="disabled", text="Removing...")
        self.update_idletasks()

        creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

        for proc_name in (APP_EXE_FILENAME, "AI_Chatbot_Ganesh_Hadpe.exe", "llama-server.exe"):
            subprocess.run(
                ["taskkill", "/F", "/IM", proc_name],
                capture_output=True,
                creationflags=creation_flags
            )

        desktop_lnk = os.path.join(os.path.expanduser("~"), "Desktop", "AI Chatbot By Ganesh K. Hadpe.lnk")
        if os.path.exists(desktop_lnk):
            try:
                os.remove(desktop_lnk)
            except Exception:
                pass

        start_menu_base = os.path.join(
            os.environ.get("APPDATA", ""), "Microsoft", "Windows", "Start Menu", "Programs"
        )
        for sm_item in (
            os.path.join(start_menu_base, "AI Chatbot By Ganesh K. Hadpe.lnk"),
            os.path.join(start_menu_base, "Uninstall AI Chatbot By Ganesh K. Hadpe.lnk"),
            os.path.join(start_menu_base, "AI Chatbot By Ganesh K. Hadpe")
        ):
            if os.path.isdir(sm_item):
                shutil.rmtree(sm_item, ignore_errors=True)
            elif os.path.exists(sm_item):
                try:
                    os.remove(sm_item)
                except Exception:
                    pass

        for reg_path in (
            REGISTRY_KEY_PATH,
            r"Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\AI_Chatbot_Ganesh_Hadpe"
        ):
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, reg_path)
            except Exception:
                pass

        core_files = [APP_EXE_FILENAME, ICON_FILENAME, SPLASH_FILENAME, "LICENSE.txt"]
        if self.remove_user_data_var.get():
            core_files.extend(["chat_history.db", "My_Study_Notes.txt"])
            for sub in ("models", "engine"):
                sub_path = os.path.join(INSTALL_DIR, sub)
                if os.path.isdir(sub_path):
                    shutil.rmtree(sub_path, ignore_errors=True)

        for fname in core_files:
            fpath = os.path.join(INSTALL_DIR, fname)
            if os.path.exists(fpath):
                try:
                    os.remove(fpath)
                except Exception:
                    pass

        messagebox.showinfo(
            "Uninstall Complete",
            "AI Chatbot By Ganesh K. Hadpe and all shortcuts have been cleanly removed."
        )

        uninstall_exe_path = os.path.join(INSTALL_DIR, UNINSTALL_EXE_FILENAME)
        if self.remove_user_data_var.get():
            cleanup_cmd = (
                f'ping 127.0.0.1 -n 4 > nul & '
                f'del /f /q "{uninstall_exe_path}" > nul 2>&1 & '
                f'rmdir /s /q "{INSTALL_DIR}" > nul 2>&1'
            )
        else:
            cleanup_cmd = (
                f'ping 127.0.0.1 -n 4 > nul & '
                f'del /f /q "{uninstall_exe_path}" > nul 2>&1'
            )

        try:
            subprocess.Popen(
                ["cmd.exe", "/c", cleanup_cmd],
                cwd=tempfile.gettempdir(),
                creationflags=creation_flags
            )
        except Exception:
            pass

        self.destroy()
        sys.exit(0)


if __name__ == "__main__":
    app = GaneshUninstallerWizard()
    app.mainloop()
'''


# =====================================================================
# TEMPLATE 2: WINDOWS SETUP WIZARD (SYNCHRONIZED WITH AI_Chatbot_GKH.exe)
# =====================================================================
SETUP_WIZARD_TEMPLATE = '''import os
import io
import sys
import shutil
import winreg
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

if sys.stdout is None:
    sys.stdout = io.StringIO()
if sys.stderr is None:
    sys.stderr = io.StringIO()

IS_FROZEN = getattr(sys, "frozen", False)
if IS_FROZEN:
    _meipass = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(sys.executable)))
    for _tcl_cand in ("_tcl_data", "tcl8.6", os.path.join("tcl", "tcl8.6")):
        _p = os.path.join(_meipass, _tcl_cand)
        if os.path.isdir(_p):
            os.environ["TCL_LIBRARY"] = _p
            break
    for _tk_cand in ("_tk_data", "tk8.6", os.path.join("tcl", "tk8.6")):
        _p = os.path.join(_meipass, _tk_cand)
        if os.path.isdir(_p):
            os.environ["TK_LIBRARY"] = _p
            break

BUNDLED_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))

# Synchronized dynamically with APP_EXE_NAME ("AI_Chatbot_GKH.exe")
APP_EXE_FILENAME = "__APP_EXE_FILENAME__"
UNINSTALL_EXE_FILENAME = "__UNINSTALL_EXE_FILENAME__"
ICON_FILENAME = "app_icon.ico"
SPLASH_FILENAME = "splash_logo.png"
LICENSE_FILENAME = "LICENSE.txt"
REGISTRY_KEY_PATH = r"Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\AI_Chatbot_GKH"

DEFAULT_INSTALL_DIR = os.path.join(
    os.environ.get("LOCALAPPDATA", os.path.expanduser("~")),
    "Programs",
    "AI_Chatbot_GKH"
)


class GaneshInstallerWizard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI Chatbot Setup Wizard — By Ganesh K. Hadpe")
        self.geometry("620x470")
        self.resizable(False, False)
        self.configure(bg="#0f172a")

        ico_path = os.path.join(BUNDLED_DIR, ICON_FILENAME)
        if os.path.exists(ico_path):
            try:
                self.iconbitmap(ico_path)
            except Exception:
                pass

        self.install_dir_var = tk.StringVar(value=DEFAULT_INSTALL_DIR)
        self.accept_var = tk.BooleanVar(value=False)
        self.desktop_shortcut_var = tk.BooleanVar(value=True)
        self.launch_now_var = tk.BooleanVar(value=True)

        self._build_ui()

    def _build_ui(self):
        header = tk.Frame(self, bg="#1e293b", padx=20, pady=14)
        header.pack(fill="x")

        tk.Label(
            header, text="📦 AI Chatbot & Study Studio — Setup Wizard",
            bg="#1e293b", fg="#f8fafc", font=("Segoe UI", 14, "bold"), anchor="w"
        ).pack(fill="x")

        tk.Label(
            header, text="❤️ Made with love by Ganesh K. Hadpe  |  Includes Custom Splash & Uninstaller",
            bg="#1e293b", fg="#fde047", font=("Segoe UI", 9, "bold"), anchor="w"
        ).pack(fill="x", pady=(2, 0))

        body = tk.Frame(self, bg="#0f172a", padx=20, pady=12)
        body.pack(fill="both", expand=True)

        tk.Label(
            body, text="License Agreement:", bg="#0f172a", fg="#38bdf8",
            font=("Segoe UI", 9, "bold"), anchor="w"
        ).pack(fill="x", pady=(0, 4))

        lic_box = tk.Text(
            body, height=8, bg="#1e293b", fg="#e2e8f0",
            font=("Consolas", 9), wrap="word", relief="flat", padx=10, pady=8
        )
        lic_box.pack(fill="x", pady=(0, 6))

        lic_file = os.path.join(BUNDLED_DIR, LICENSE_FILENAME)
        if os.path.exists(lic_file):
            with open(lic_file, "r", encoding="utf-8", errors="ignore") as f:
                lic_box.insert("1.0", f.read())
        lic_box.configure(state="disabled")

        tk.Checkbutton(
            body, text="I accept the Ganesh K. Hadpe Software License Agreement",
            variable=self.accept_var, bg="#0f172a", fg="#4ade80",
            selectcolor="#1e293b", activebackground="#0f172a", activeforeground="#4ade80",
            font=("Segoe UI", 9, "bold"), command=self._toggle_install_btn
        ).pack(anchor="w", pady=(0, 10))

        tk.Label(
            body, text="Installation Folder:", bg="#0f172a", fg="#e2e8f0",
            font=("Segoe UI", 9, "bold"), anchor="w"
        ).pack(fill="x", pady=(0, 4))

        dir_row = tk.Frame(body, bg="#0f172a")
        dir_row.pack(fill="x", pady=(0, 8))

        tk.Entry(
            dir_row, textvariable=self.install_dir_var, bg="#1e293b", fg="white",
            font=("Segoe UI", 9), relief="flat"
        ).pack(side="left", fill="x", expand=True, ipady=5, padx=(0, 8))

        tk.Button(
            dir_row, text="Browse...", bg="#334155", fg="white",
            font=("Segoe UI", 9), relief="flat", padx=10, pady=3,
            command=self._browse_dir
        ).pack(side="right")

        tk.Checkbutton(
            body, text="Create Desktop & Start Menu Shortcuts (including Uninstaller)",
            variable=self.desktop_shortcut_var, bg="#0f172a", fg="#e2e8f0",
            selectcolor="#1e293b", activebackground="#0f172a", font=("Segoe UI", 9)
        ).pack(anchor="w")

        tk.Checkbutton(
            body, text="Launch AI Chatbot immediately after installation",
            variable=self.launch_now_var, bg="#0f172a", fg="#e2e8f0",
            selectcolor="#1e293b", activebackground="#0f172a", font=("Segoe UI", 9)
        ).pack(anchor="w")

        footer = tk.Frame(self, bg="#1e293b", padx=20, pady=10)
        footer.pack(fill="x", side="bottom")

        self.status_lbl = tk.Label(
            footer, text="Ready to install", bg="#1e293b", fg="#94a3b8",
            font=("Segoe UI", 9, "bold")
        )
        self.status_lbl.pack(side="left")

        self.install_btn = tk.Button(
            footer, text="Install Now ➤", bg="#16a34a", fg="white",
            activebackground="#15803d", activeforeground="white",
            font=("Segoe UI", 10, "bold"), relief="flat", width=14, pady=5,
            state="disabled", cursor="hand2", command=self._run_install
        )
        self.install_btn.pack(side="right")

    def _toggle_install_btn(self):
        self.install_btn.configure(state="normal" if self.accept_var.get() else "disabled")

    def _browse_dir(self):
        d = filedialog.askdirectory(title="Select Installation Folder")
        if d:
            self.install_dir_var.set(os.path.join(d, "AI_Chatbot_GKH"))

    def _create_windows_shortcut(self, shortcut_path: str, target_exe: str, work_dir: str, icon_path: str, desc: str):
        vbs_path = os.path.join(work_dir, "_create_shortcut.vbs")
        vbs_code = (
            'Set oWS = WScript.CreateObject("WScript.Shell")\\r\\n'
            f'Set oLink = oWS.CreateShortcut("{shortcut_path}")\\r\\n'
            f'oLink.TargetPath = "{target_exe}"\\r\\n'
            f'oLink.WorkingDirectory = "{work_dir}"\\r\\n'
            f'oLink.Description = "{desc}"\\r\\n'
            f'oLink.IconLocation = "{icon_path}"\\r\\n'
            'oLink.Save\\r\\n'
        )
        try:
            with open(vbs_path, "w", encoding="mbcs") as vf:
                vf.write(vbs_code)
            subprocess.run(
                ["cscript", "//Nologo", vbs_path],
                capture_output=True,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
            )
        finally:
            if os.path.exists(vbs_path):
                os.remove(vbs_path)

    def _register_uninstaller_in_windows(self, target_dir: str, uninstall_exe: str, icon_path: str):
        try:
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, REGISTRY_KEY_PATH) as key:
                winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, "AI Chatbot By Ganesh K. Hadpe")
                winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, "Ganesh K. Hadpe")
                winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, "3.0.0")
                winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, icon_path)
                winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, target_dir)
                winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, f'"{uninstall_exe}"')
                winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)
        except Exception:
            pass

    def _run_install(self):
        target_dir = self.install_dir_var.get().strip()
        if not target_dir:
            return
        try:
            self.install_btn.configure(state="disabled")
            self.status_lbl.configure(text="Installing files & uninstaller...", fg="#fbbf24")
            self.update_idletasks()

            # Stop any currently running instance in the target directory before overwriting
            creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
            subprocess.run(
                ["taskkill", "/F", "/IM", APP_EXE_FILENAME],
                capture_output=True,
                creationflags=creation_flags
            )

            os.makedirs(target_dir, exist_ok=True)
            for fname in (APP_EXE_FILENAME, UNINSTALL_EXE_FILENAME, ICON_FILENAME, SPLASH_FILENAME, LICENSE_FILENAME):
                src = os.path.join(BUNDLED_DIR, fname)
                if not os.path.exists(src):
                    raise FileNotFoundError(f"Bundled installer file missing: {fname}")
                shutil.copy2(src, os.path.join(target_dir, fname))

            installed_exe = os.path.join(target_dir, APP_EXE_FILENAME)
            installed_uninst = os.path.join(target_dir, UNINSTALL_EXE_FILENAME)
            installed_ico = os.path.join(target_dir, ICON_FILENAME)

            self._register_uninstaller_in_windows(target_dir, installed_uninst, installed_ico)

            if self.desktop_shortcut_var.get():
                desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
                if os.path.isdir(desktop_dir):
                    lnk = os.path.join(desktop_dir, "AI Chatbot By Ganesh K. Hadpe.lnk")
                    self._create_windows_shortcut(
                        lnk, installed_exe, target_dir, installed_ico, "AI Chatbot By Ganesh K. Hadpe"
                    )

                start_menu_dir = os.path.join(
                    os.environ.get("APPDATA", ""),
                    "Microsoft", "Windows", "Start Menu", "Programs",
                    "AI Chatbot By Ganesh K. Hadpe"
                )
                os.makedirs(start_menu_dir, exist_ok=True)
                sm_app_lnk = os.path.join(start_menu_dir, "AI Chatbot By Ganesh K. Hadpe.lnk")
                sm_uninst_lnk = os.path.join(start_menu_dir, "Uninstall AI Chatbot.lnk")

                self._create_windows_shortcut(
                    sm_app_lnk, installed_exe, target_dir, installed_ico, "Launch AI Chatbot By Ganesh K. Hadpe"
                )
                self._create_windows_shortcut(
                    sm_uninst_lnk, installed_uninst, target_dir, installed_ico, "Uninstall AI Chatbot By Ganesh K. Hadpe"
                )

            self.status_lbl.configure(text="Installation Complete ✔", fg="#4ade80")
            messagebox.showinfo(
                "Installation Complete",
                f"AI Chatbot By Ganesh K. Hadpe ({APP_EXE_FILENAME}) has been installed to:\\n{target_dir}\\n\\n"
                "You can uninstall anytime via Uninstall.exe, Start Menu, or Windows Installed Apps."
            )

            if self.launch_now_var.get() and os.path.exists(installed_exe):
                subprocess.Popen([installed_exe], cwd=target_dir)

            self.destroy()
        except Exception as e:
            self.install_btn.configure(state="normal")
            messagebox.showerror("Install Error", str(e))


if __name__ == "__main__":
    wiz = GaneshInstallerWizard()
    wiz.mainloop()
'''


def prepare_ico_and_splash_png(py_exe: str) -> tuple[str, str]:
    print("Step 1/5: Checking Pillow, PyInstaller, and pypdf...")
    subprocess.run(
        [py_exe, "-m", "pip", "install", "--upgrade", "pillow", "pyinstaller", "pypdf"],
        check=True
    )
    from PIL import Image

    png_candidates = [
        os.path.join(BASE_DIR, f)
        for f in os.listdir(BASE_DIR)
        if f.lower().endswith(".png") and f.lower() != "splash_logo.png"
    ]

    png_path = ""
    if png_candidates:
        png_path = png_candidates[0]
        print(f"✔ Found your PNG image: {png_path}")
    elif os.path.exists(ICO_OUTPUT) and os.path.exists(SPLASH_PNG_OUTPUT):
        print("✔ Using existing app_icon.ico and splash_logo.png")
        return ICO_OUTPUT, SPLASH_PNG_OUTPUT
    else:
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        png_path = filedialog.askopenfilename(
            initialdir=BASE_DIR,
            title="Select Your .PNG Logo Image for Icon & Splash Screen",
            filetypes=[("PNG / Image Files", "*.png *.jpg *.jpeg *.webp"), ("All Files", "*.*")]
        )
        root.destroy()

    if not png_path:
        raise SystemExit("No .png image selected. Please place your .png in D:\\AI or select it when prompted.")

    img = Image.open(png_path).convert("RGBA")

    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(ICO_OUTPUT, format="ICO", sizes=icon_sizes)
    print(f"✅ Created Windows Icon: {ICO_OUTPUT}")

    splash_img = img.copy()
    splash_img.thumbnail((110, 110), Image.Resampling.LANCZOS)
    splash_img.save(SPLASH_PNG_OUTPUT, format="PNG")
    print(f"✅ Created Splash Screen Logo: {SPLASH_PNG_OUTPUT}\n")

    return ICO_OUTPUT, SPLASH_PNG_OUTPUT


def build_all():
    print("==========================================================")
    print(f"  Building {APP_EXE_NAME}.exe + {UNINSTALL_EXE_NAME}.exe + {SETUP_EXE_NAME}.exe")
    print("  Licensed to: Ganesh K. Hadpe")
    print("==========================================================\n")

    if not CHATBOT_SCRIPT or not os.path.exists(CHATBOT_SCRIPT):
        print("❌ Could not find chatbot_3.py or chatbot.py in D:\\AI.")
        return

    print(f"✔ Using source script: {CHATBOT_SCRIPT}")
    with open(CHATBOT_SCRIPT, "r", encoding="utf-8", errors="ignore") as f:
        if "class StudentOfflineBot" not in f.read():
            print(f"❌ '{CHATBOT_SCRIPT}' does not contain StudentOfflineBot!")
            return

    py_exe = sys.executable.replace("pythonw.exe", "python.exe")
    py_root = os.path.dirname(py_exe)

    # 1. Convert PNG to both app_icon.ico and splash_logo.png
    ico_file, splash_png = prepare_ico_and_splash_png(py_exe)

    # Close any running instances before overwriting
    for name in (
        f"{APP_EXE_NAME}.exe",
        f"{UNINSTALL_EXE_NAME}.exe",
        f"{SETUP_EXE_NAME}.exe",
        "AI_Chatbot_Ganesh_Hadpe.exe"
    ):
        subprocess.run(["taskkill", "/F", "/IM", name], capture_output=True)

    with open(LICENSE_FILE, "w", encoding="utf-8") as lf:
        lf.write(LICENSE_TEXT.strip())

    clean_env = os.environ.copy()
    clean_env.pop("TCL_LIBRARY", None)
    clean_env.pop("TK_LIBRARY", None)

    tcl_dir = os.path.join(py_root, "tcl", "tcl8.6")
    tk_dir = os.path.join(py_root, "tcl", "tk8.6")
    tcl_args = []
    if os.path.isdir(tcl_dir) and os.path.isdir(tk_dir):
        tcl_args = ["--add-data", f"{tcl_dir};_tcl_data", "--add-data", f"{tk_dir};_tk_data"]

    # 2. Build Standalone Application (AI_Chatbot_GKH.exe)
    print(f"Step 2/5: Building Standalone Application ({APP_EXE_NAME}.exe)...")
    with open(VERSION_FILE, "w", encoding="utf-8") as vf:
        vf.write(get_version_metadata(
            APP_EXE_NAME,
            f"{APP_EXE_NAME}.exe",
            "AI Chatbot & Study Studio - Made with love by Ganesh K. Hadpe"
        ))

    app_cmd = [
        py_exe, "-m", "PyInstaller",
        "--noconfirm", "--clean", "--onefile", "--noconsole", "--noupx",
        "--name", APP_EXE_NAME,
        "--icon", ico_file,
        "--version-file", VERSION_FILE,
        "--add-data", f"{ico_file};.",
        "--add-data", f"{splash_png};.",
        "--collect-all", "pypdf",
        "--hidden-import", "tkinter",
        "--hidden-import", "sqlite3",
        "--distpath", BASE_DIR,
        *tcl_args,
        CHATBOT_SCRIPT
    ]
    subprocess.run(app_cmd, cwd=BASE_DIR, env=clean_env, check=True)
    app_exe_path = os.path.join(BASE_DIR, f"{APP_EXE_NAME}.exe")

    # 3. Build Uninstaller (Uninstall.exe) with synchronized APP_EXE_FILENAME
    print(f"\nStep 3/5: Building Clean Uninstaller ({UNINSTALL_EXE_NAME}.exe)...")
    uninstaller_code = (
        UNINSTALLER_TEMPLATE.strip()
        .replace("__APP_EXE_FILENAME__", f"{APP_EXE_NAME}.exe")
        .replace("__UNINSTALL_EXE_FILENAME__", f"{UNINSTALL_EXE_NAME}.exe")
    )
    with open(UNINSTALL_SCRIPT, "w", encoding="utf-8") as uf:
        uf.write(uninstaller_code)

    with open(VERSION_FILE, "w", encoding="utf-8") as vf:
        vf.write(get_version_metadata(
            UNINSTALL_EXE_NAME,
            f"{UNINSTALL_EXE_NAME}.exe",
            "Uninstaller for AI Chatbot By Ganesh K. Hadpe"
        ))

    uninst_cmd = [
        py_exe, "-m", "PyInstaller",
        "--noconfirm", "--clean", "--onefile", "--noconsole", "--noupx",
        "--name", UNINSTALL_EXE_NAME,
        "--icon", ico_file,
        "--version-file", VERSION_FILE,
        "--add-data", f"{ico_file};.",
        "--hidden-import", "tkinter",
        "--distpath", BASE_DIR,
        *tcl_args,
        UNINSTALL_SCRIPT
    ]
    subprocess.run(uninst_cmd, cwd=BASE_DIR, env=clean_env, check=True)
    uninst_exe_path = os.path.join(BASE_DIR, f"{UNINSTALL_EXE_NAME}.exe")

    # 4. Build Windows Setup Installer (AI_Chatbot_By_GKH.exe) with synchronized APP_EXE_FILENAME
    print(f"\nStep 4/5: Bundling App + Splash + Uninstaller into {SETUP_EXE_NAME}.exe...")
    setup_code = (
        SETUP_WIZARD_TEMPLATE.strip()
        .replace("__APP_EXE_FILENAME__", f"{APP_EXE_NAME}.exe")
        .replace("__UNINSTALL_EXE_FILENAME__", f"{UNINSTALL_EXE_NAME}.exe")
    )
    with open(SETUP_SCRIPT, "w", encoding="utf-8") as sf:
        sf.write(setup_code)

    with open(VERSION_FILE, "w", encoding="utf-8") as vf:
        vf.write(get_version_metadata(
            SETUP_EXE_NAME,
            f"{SETUP_EXE_NAME}.exe",
            "AI Chatbot Setup Installer - Licensed to Ganesh K. Hadpe"
        ))

    setup_cmd = [
        py_exe, "-m", "PyInstaller",
        "--noconfirm", "--clean", "--onefile", "--noconsole", "--noupx",
        "--name", SETUP_EXE_NAME,
        "--icon", ico_file,
        "--version-file", VERSION_FILE,
        "--add-data", f"{app_exe_path};.",
        "--add-data", f"{uninst_exe_path};.",
        "--add-data", f"{ico_file};.",
        "--add-data", f"{splash_png};.",
        "--add-data", f"{LICENSE_FILE};.",
        "--hidden-import", "tkinter",
        "--distpath", BASE_DIR,
        *tcl_args,
        SETUP_SCRIPT
    ]
    subprocess.run(setup_cmd, cwd=BASE_DIR, env=clean_env, check=True)

    # 5. Cleanup temporary build artifacts
    print("\nStep 5/5: Cleaning temporary build files...")
    for folder in ("build", "__pycache__"):
        p = os.path.join(BASE_DIR, folder)
        if os.path.exists(p):
            shutil.rmtree(p, ignore_errors=True)
    for ftemp in (
        f"{APP_EXE_NAME}.spec",
        f"{UNINSTALL_EXE_NAME}.spec",
        f"{SETUP_EXE_NAME}.spec",
        VERSION_FILE,
        UNINSTALL_SCRIPT,
        SETUP_SCRIPT
    ):
        p = os.path.join(BASE_DIR, ftemp)
        if os.path.exists(p):
            os.remove(p)

    setup_exe_path = os.path.join(BASE_DIR, f"{SETUP_EXE_NAME}.exe")
    print("\n==========================================================")
    print("🎉 ALL DONE! YOUR SYNCHRONIZED INSTALLER IS READY:")
    print(f"1. Windows Setup Wizard: {setup_exe_path}")
    print(f"2. Standalone App .EXE:  {app_exe_path}")
    print(f"3. Standalone Uninstaller: {uninst_exe_path}")
    print("==========================================================")


if __name__ == "__main__":
    build_all()
