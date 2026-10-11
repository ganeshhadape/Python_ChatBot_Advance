import os
import io
import re
import sys
import ast
import math
import json
import time
import queue
import random
import ctypes
import shutil
import socket
import sqlite3
import zipfile
import atexit
import operator
import datetime
import threading
import subprocess
import urllib.request
import multiprocessing
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# =====================================================================
# 0. STANDALONE .EXE GUARDS & WINDOWS HD CLEARTYPE FONTS
# =====================================================================
IS_FROZEN = getattr(sys, "frozen", False)

if sys.stdout is None:
    sys.stdout = io.StringIO()
if sys.stderr is None:
    sys.stderr = io.StringIO()

# Single-instance Windows Mutex so the .exe can never spawn duplicate processes
_SINGLE_INSTANCE_MUTEX = None
if IS_FROZEN:
    try:
        _SINGLE_INSTANCE_MUTEX = ctypes.windll.kernel32.CreateMutexW(
            None, False, "Local\\GaneshHadpe_AIChatbot_SingleInstance_v4"
        )
        if ctypes.windll.kernel32.GetLastError() == 183:
            sys.exit(0)
    except Exception:
        pass

# Locate bundled Tcl/Tk data inside standalone .exe
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

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

try:
    from pypdf import PdfReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    if not IS_FROZEN and "python" in os.path.basename(sys.executable).lower():
        try:
            _py_exe = sys.executable.replace("pythonw.exe", "python.exe")
            subprocess.run([_py_exe, "-m", "pip", "install", "pypdf"], check=False)
            from pypdf import PdfReader
            PDF_AVAILABLE = True
        except Exception:
            PDF_AVAILABLE = False

print("==========================================================")
print("   Made with love by Ganesh K. Hadpe")
print("   Copyright (c) 2026 Ganesh K. Hadpe. All Rights Reserved.")
print("==========================================================")

# =====================================================================
# 1. MULTI-MODEL CATALOG, LICENSE & PATHS
# =====================================================================
AUTHOR_SIGNATURE = "Made with love by Ganesh K. Hadpe"
LICENSE_TEXT = (
    "AI CHATBOT & STUDY STUDIO\n"
    "Copyright © 2026 Ganesh K. Hadpe. All Rights Reserved.\n\n"
    "Licensed under the Ganesh K. Hadpe Software License:\n"
    "Permission is hereby granted to use this standalone application for personal, "
    "educational, and productivity purposes. The creator credit and license notice "
    "('Made with love by Ganesh K. Hadpe') must remain intact in all copies.\n\n"
    "Security Status: 100% Offline Local Execution (127.0.0.1 Loopback Isolated).\n"
    "No user data, files, or chats are ever transmitted to external servers."
)

if IS_FROZEN:
    BASE_DIR = os.path.dirname(os.path.abspath(sys.executable))
    BUNDLED_DIR = getattr(sys, "_MEIPASS", BASE_DIR)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
    BUNDLED_DIR = BASE_DIR

MODEL_DIR = os.path.join(BASE_DIR, "models")
ENGINE_DIR = os.path.join(BASE_DIR, "engine")
SERVER_EXE = os.path.join(ENGINE_DIR, "llama-server.exe")
DB_PATH = os.path.join(BASE_DIR, "chat_history.db")
NOTES_EXPORT_PATH = os.path.join(BASE_DIR, "My_Study_Notes.txt")

# Locate custom converted .ico icon
ICON_PATH = os.path.join(BASE_DIR, "app_icon.ico")
if not os.path.exists(ICON_PATH):
    ICON_PATH = os.path.join(BUNDLED_DIR, "app_icon.ico")


def find_splash_logo_png() -> str:
    """Finds splash_logo.png (bundled or local) or any .png file in BASE_DIR."""
    for candidate in (
        os.path.join(BASE_DIR, "splash_logo.png"),
        os.path.join(BUNDLED_DIR, "splash_logo.png"),
    ):
        if os.path.exists(candidate):
            return candidate
    try:
        for fname in os.listdir(BASE_DIR):
            if fname.lower().endswith(".png"):
                return os.path.join(BASE_DIR, fname)
    except Exception:
        pass
    return ""


SPLASH_PNG_PATH = find_splash_logo_png()

GITHUB_RELEASES_API = "https://api.github.com/repos/ggml-org/llama.cpp/releases?per_page=10"
CPU_THREADS = max(2, (os.cpu_count() or 4) // 2)

MODELS = {
    "Llama-3.2-1B (Fast Everyday & Hinglish - 808 MB)": {
        "filename": "Llama-3.2-1B-Instruct-Q4_K_M.gguf",
        "url": (
            "https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF/"
            "resolve/main/Llama-3.2-1B-Instruct-Q4_K_M.gguf"
        )
    },
    "Qwen2.5-1.5B (Best for Math, Science & Coding - 1.1 GB)": {
        "filename": "qwen2.5-1.5b-instruct-q4_k_m.gguf",
        "url": (
            "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/"
            "resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf"
        )
    },
    "Gemma-2-2B (Best Marathi & Hindi Fluency - 1.7 GB)": {
        "filename": "gemma-2-2b-it-Q4_K_M.gguf",
        "url": (
            "https://huggingface.co/bartowski/gemma-2-2b-it-GGUF/"
            "resolve/main/gemma-2-2b-it-Q4_K_M.gguf"
        )
    }
}

PERSONAS = {
    "All-Round AI (Gemini Mode)": (
        "You are an authentic, adaptive, highly intelligent, and witty AI assistant like Gemini. "
        "You can discuss and answer literally anything: general knowledge, everyday questions, life advice, "
        "creative ideas, philosophy, history, movies, or casual everyday chat. "
        "Do not restrict yourself to academic tutoring—converse naturally and insightfully with zero robotic fluff."
    ),
    "Friendly Study Partner": (
        "You are a warm, smart, encouraging study partner and best friend. "
        "Explain concepts clearly with relatable real-life examples. Never sound robotic."
    ),
    "Exam & Concept Tutor": (
        "You are an expert academic tutor for school and college students. "
        "Break down definitions, key formulas, and exam-ready points clearly step-by-step."
    ),
    "Python & Coding Mentor": (
        "You are a patient senior programmer mentoring a student. "
        "Explain how code works line-by-line and provide clean Python 3.12 examples."
    )
}

LANGUAGE_MODES = [
    "Auto-Detect (Match My Language)",
    "English Only",
    "Hinglish",
    "Marathi / Minglish)",
    "Hindi / Marathi (Devanagari Script)"
]

MULTILINGUAL_EXAMPLES = {
    "marathi_roman": [
        {"role": "user", "content": "tumhi mala thodi madat karal ka?"},
        {"role": "assistant", "content": "Ho nakki! Sanga na, konta topic kiwa vishay aahe? Mi nakki madat karen!"},
        {"role": "user", "content": "kasa aahes bhau, kay chalay?"},
        {"role": "assistant", "content": "Mi ekdum majet aahe! Tumhi sanga, aaj kay navin vishayavar bolaycha aahe?"}
    ],
    "hinglish": [
        {"role": "user", "content": "kya aap meri madad kar sakte ho?"},
        {"role": "assistant", "content": "Haan bilkul! Batao na, kis cheez mein help chahiye? Main ready hoon!"},
        {"role": "user", "content": "aur bhai kya haal chaal hai?"},
        {"role": "assistant", "content": "Sab badhiya chal raha hai yaar! Aap batao, aaj kis topic pe baat karni hai?"}
    ]
}


# =====================================================================
# 2. CUSTOM STARTUP SPLASH SCREEN (WITH .PNG LOGO & CREATOR CREDIT)
# =====================================================================
class StartupSplashScreen(tk.Toplevel):
    """Borderless centered startup splash screen displaying the user's PNG logo and creator credit."""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(bg="#38bdf8")  # Outer glowing cyan accent border

        w, h = 540, 360
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        self.logo_photo = None
        self._step_val = 0
        self._anim_id = None

        self._build_splash_ui()
        self._animate_loading()

    def _build_splash_ui(self):
        card = tk.Frame(self, bg="#0f172a", padx=28, pady=22)
        card.pack(fill="both", expand=True, padx=2, pady=2)

        # 1. Load User's Custom .PNG Logo (with automatic scaling if large)
        logo_loaded = False
        if SPLASH_PNG_PATH and os.path.exists(SPLASH_PNG_PATH):
            try:
                raw_img = tk.PhotoImage(file=SPLASH_PNG_PATH)
                iw, ih = raw_img.width(), raw_img.height()
                if iw > 120 or ih > 120:
                    factor = max(1, int(max(iw, ih) / 110))
                    raw_img = raw_img.subsample(factor, factor)
                self.logo_photo = raw_img
                tk.Label(card, image=self.logo_photo, bg="#0f172a", bd=0).pack(pady=(2, 10))
                logo_loaded = True
            except Exception:
                logo_loaded = False

        if not logo_loaded:
            tk.Label(
                card, text="🎓", bg="#0f172a", fg="#38bdf8",
                font=("Segoe UI", 42, "bold")
            ).pack(pady=(2, 6))

        # 2. Application Title & Subtitle
        tk.Label(
            card, text="AI CHATBOT & STUDY STUDIO",
            bg="#0f172a", fg="#f8fafc", font=("Segoe UI", 16, "bold")
        ).pack(pady=(0, 2))

        tk.Label(
            card, text="100% Offline Windows AI Assistant • PDF • Flashcards • Exact Math",
            bg="#0f172a", fg="#94a3b8", font=("Segoe UI", 9)
        ).pack(pady=(0, 12))

        # 3. Prominent Creator Signature Banner ("Made with love by Ganesh K. Hadpe")
        sig_badge = tk.Frame(card, bg="#1e293b", padx=18, pady=7)
        sig_badge.pack(pady=(0, 16))

        tk.Label(
            sig_badge, text=f"❤️  {AUTHOR_SIGNATURE}",
            bg="#1e293b", fg="#fde047", font=("Segoe UI", 11, "bold")
        ).pack()

        # 4. Animated Progress Bar & Live Status
        self.progress = ttk.Progressbar(card, orient="horizontal", mode="determinate", maximum=100)
        self.progress.pack(fill="x", padx=10, pady=(0, 8))

        self.status_lbl = tk.Label(
            card, text="Starting Offline AI Engine & Workspace...",
            bg="#0f172a", fg="#38bdf8", font=("Segoe UI", 9, "bold")
        )
        self.status_lbl.pack()

        tk.Label(
            card, text="Copyright © 2026 Ganesh K. Hadpe. All Rights Reserved.",
            bg="#0f172a", fg="#64748b", font=("Segoe UI", 8)
        ).pack(side="bottom", pady=(6, 0))

    def _animate_loading(self):
        stages = [
            (15, "Loading Windows ClearType HD Interface..."),
            (38, "Initializing Local SQLite Memory & Math Engine..."),
            (65, "Preparing Flashcard Studio & PDF Reader..."),
            (88, "Connecting Local CPU AI Engine..."),
            (100, "Launching AI Studio...")
        ]
        self._step_val += 4
        self.progress["value"] = min(100, self._step_val)

        for threshold, msg in stages:
            if self._step_val <= threshold:
                self.status_lbl.configure(text=msg)
                break

        if self._step_val < 100:
            self._anim_id = self.after(75, self._animate_loading)
        else:
            self.after(200, self.finish_splash)

    def finish_splash(self):
        if self._anim_id is not None:
            try:
                self.after_cancel(self._anim_id)
            except Exception:
                pass
        try:
            self.destroy()
        except Exception:
            pass
        try:
            self.parent.deiconify()
            self.parent.lift()
            self.parent.focus_force()
        except Exception:
            pass


# =====================================================================
# 3. SMOOTH HOVER TOOLTIP ENGINE
# =====================================================================
class HoverTooltip:
    """Displays a modern dark-mode floating tooltip when hovering over any UI control."""

    def __init__(self, widget, title: str, description: str, delay_ms: int = 220):
        self.widget = widget
        self.title = title
        self.description = description
        self.delay_ms = delay_ms
        self.tip_window = None
        self.after_id = None

        self.widget.bind("<Enter>", self._on_enter, add="+")
        self.widget.bind("<Leave>", self._on_leave, add="+")
        self.widget.bind("<ButtonPress>", self._on_leave, add="+")

    def _on_enter(self, _event=None):
        self._cancel_scheduled()
        self.after_id = self.widget.after(self.delay_ms, self._show_tooltip)

    def _on_leave(self, _event=None):
        self._cancel_scheduled()
        self._hide_tooltip()

    def _cancel_scheduled(self):
        if self.after_id is not None:
            try:
                self.widget.after_cancel(self.after_id)
            except Exception:
                pass
            self.after_id = None

    def _show_tooltip(self):
        if self.tip_window is not None:
            return
        try:
            x = self.widget.winfo_rootx() + 14
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6

            screen_w = self.widget.winfo_screenwidth()
            if x + 310 > screen_w:
                x = max(10, screen_w - 320)

            self.tip_window = tw = tk.Toplevel(self.widget)
            tw.wm_overrideredirect(True)
            tw.wm_geometry(f"+{x}+{y}")
            tw.attributes("-topmost", True)

            border = tk.Frame(tw, bg="#38bdf8", padx=1, pady=1)
            border.pack(fill="both", expand=True)

            inner = tk.Frame(border, bg="#0f172a", padx=10, pady=7)
            inner.pack(fill="both", expand=True)

            tk.Label(
                inner, text=self.title, bg="#0f172a", fg="#38bdf8",
                font=("Segoe UI", 9, "bold"), anchor="w", justify="left"
            ).pack(fill="x", pady=(0, 2))

            tk.Label(
                inner, text=self.description, bg="#0f172a", fg="#e2e8f0",
                font=("Segoe UI", 9), wraplength=280, anchor="w", justify="left"
            ).pack(fill="x")
        except Exception:
            self._hide_tooltip()

    def _hide_tooltip(self):
        if self.tip_window is not None:
            try:
                self.tip_window.destroy()
            except Exception:
                pass
            self.tip_window = None


# =====================================================================
# 4. DETERMINISTIC PYTHON MATH & FORMULA ENGINE
# =====================================================================
def _safe_pow(a, b):
    if abs(b) > 1000 or (abs(a) > 1e6 and abs(b) > 20):
        raise ValueError("Exponent too large for safe evaluation")
    return operator.pow(a, b)


def _safe_factorial(n):
    n_int = int(n)
    if n_int < 0 or n_int > 170:
        raise ValueError("Factorial input must be between 0 and 170")
    return math.factorial(n_int)


class ExactMathSolver:
    ALLOWED_OPS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: _safe_pow,
        ast.Mod: operator.mod,
        ast.FloorDiv: operator.floordiv,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    ALLOWED_FUNCS = {
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "asin": math.asin,
        "acos": math.acos,
        "atan": math.atan,
        "sind": lambda x: math.sin(math.radians(x)),
        "cosd": lambda x: math.cos(math.radians(x)),
        "tand": lambda x: math.tan(math.radians(x)),
        "log": math.log,
        "ln": math.log,
        "log10": math.log10,
        "log2": math.log2,
        "exp": math.exp,
        "factorial": _safe_factorial,
        "gcd": math.gcd,
        "lcm": getattr(math, "lcm", lambda a, b: abs(a * b) // math.gcd(a, b)),
        "degrees": math.degrees,
        "radians": math.radians,
        "abs": abs,
        "round": round,
        "pi": math.pi,
        "e": math.e,
    }

    @classmethod
    def _eval_node(cls, node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.Name):
            if node.id in cls.ALLOWED_FUNCS and isinstance(cls.ALLOWED_FUNCS[node.id], (int, float)):
                return cls.ALLOWED_FUNCS[node.id]
            raise ValueError(f"Unknown constant: {node.id}")
        if isinstance(node, ast.BinOp) and type(node.op) in cls.ALLOWED_OPS:
            left = cls._eval_node(node.left)
            right = cls._eval_node(node.right)
            return cls.ALLOWED_OPS[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp) and type(node.op) in cls.ALLOWED_OPS:
            return cls.ALLOWED_OPS[type(node.op)](cls._eval_node(node.operand))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            fname = node.func.id.lower()
            if fname in cls.ALLOWED_FUNCS and callable(cls.ALLOWED_FUNCS[fname]):
                args = [cls._eval_node(a) for a in node.args]
                return cls.ALLOWED_FUNCS[fname](*args)
        raise ValueError("Unsupported math expression")

    @classmethod
    def solve_quadratic(cls, text: str):
        cleaned = text.replace(" ", "").replace("**", "^").lower()
        pattern = r"([+-]?\d*\.?\d*)?\*?x\^2([+-]\d*\.?\d*)?\*?x([+-]\d+\.?\d*)=0"
        match = re.search(pattern, cleaned)
        if not match:
            return None

        def _parse_coeff(s, default=1.0):
            if not s or s == "+":
                return default
            if s == "-":
                return -default
            return float(s)

        a = _parse_coeff(match.group(1), 1.0)
        b = _parse_coeff(match.group(2), 0.0)
        c = float(match.group(3))
        if a == 0:
            return None

        disc = (b ** 2) - (4 * a * c)
        if disc > 0:
            r1 = (-b + math.sqrt(disc)) / (2 * a)
            r2 = (-b - math.sqrt(disc)) / (2 * a)
            return (
                f"Quadratic Equation ({a}x² + {b}x + {c} = 0) → "
                f"Discriminant Δ = {disc:.4g}, Exact Roots: x₁ = {r1:.6g}, x₂ = {r2:.6g}"
            )
        if disc == 0:
            r = -b / (2 * a)
            return f"Quadratic Equation ({a}x² + {b}x + {c} = 0) → Discriminant Δ = 0, Repeated Root: x = {r:.6g}"
        real_p = -b / (2 * a)
        imag_p = math.sqrt(-disc) / (2 * a)
        return (
            f"Quadratic Equation ({a}x² + {b}x + {c} = 0) → "
            f"Discriminant Δ = {disc:.4g} (Complex Roots): x = {real_p:.4g} ± {imag_p:.4g}i"
        )

    @classmethod
    def try_evaluate(cls, user_text: str):
        if len(user_text) > 300:
            return None
        quad = cls.solve_quadratic(user_text)
        if quad:
            return quad

        expr = user_text.strip()
        prefixes = [
            "calculate", "solve", "evaluate", "compute", "what is", "find the value of",
            "exact math:", "solve step-by-step:"
        ]
        lower_expr = expr.lower()
        for p in prefixes:
            if lower_expr.startswith(p):
                expr = expr[len(p):].strip()
                lower_expr = expr.lower()

        expr = expr.rstrip("?=.")
        expr = expr.replace("^", "**").replace("×", "*").replace("÷", "/")
        expr = re.sub(r"(\d)\s*\(", r"\1*(", expr)

        if not any(ch.isdigit() for ch in expr):
            return None

        try:
            tree = ast.parse(expr, mode="eval")
            result = cls._eval_node(tree.body)
            formatted = f"{result:.8g}" if isinstance(result, float) else str(result)
            return f"{expr} = {formatted}"
        except Exception:
            inline_matches = re.findall(
                r"(?:sqrt|sin|cos|tan|sind|cosd|tand|log10|log|ln|factorial|gcd|lcm)?\s*[\d\.\+\-\*\/\^\(\)\s]{3,}",
                user_text
            )
            for candidate in inline_matches:
                cand = candidate.strip().replace("^", "**")
                if any(op in cand for op in ("+", "-", "*", "/", "**", "(")) and any(c.isdigit() for c in cand):
                    try:
                        tree = ast.parse(cand, mode="eval")
                        val = cls._eval_node(tree.body)
                        formatted = f"{val:.8g}" if isinstance(val, float) else str(val)
                        return f"{cand} = {formatted}"
                    except Exception:
                        continue
            return None


# =====================================================================
# 5. UPGRADED INTERACTIVE FLASHCARD STUDIO 2.0 POPUP WINDOW
# =====================================================================
class FlashcardFlipperPopup(tk.Toplevel):
    def __init__(self, parent, topic_title: str, cards: list[dict]):
        super().__init__(parent)
        self.parent_app = parent
        self.topic_title = topic_title
        self.title(f"🃏 Interactive Study Flashcards — {topic_title[:40]} | {AUTHOR_SIGNATURE}")
        self.geometry("720x510")
        self.minsize(620, 440)
        self.configure(bg="#0f172a")
        if os.path.exists(ICON_PATH):
            try:
                self.iconbitmap(ICON_PATH)
            except Exception:
                pass

        self.all_cards = cards if cards else [
            {"q": "No cards parsed.", "a": "Try clicking Flashcards again with a clear topic."}
        ]
        self.active_indices = list(range(len(self.all_cards)))
        self.pos = 0
        self.showing_answer = False
        self.hint_shown = False
        self.review_only_mode = False
        self.mastered_ids = set()
        self.review_ids = set()

        self._build_popup_ui()
        self._render_card()

        self.bind("<space>", lambda e: self._flip_card())
        self.bind("<Right>", lambda e: self._next_card())
        self.bind("<Left>", lambda e: self._prev_card())
        self.bind("h", lambda e: self._show_hint())
        self.bind("H", lambda e: self._show_hint())
        self.bind("1", lambda e: self._mark_mastered())
        self.bind("2", lambda e: self._mark_review())
        self.focus_set()

    def _build_popup_ui(self):
        top_bar = tk.Frame(self, bg="#1e293b", padx=16, pady=10)
        top_bar.pack(fill="x")

        self.progress_lbl = tk.Label(
            top_bar, text="Card 1 of 5", bg="#1e293b", fg="#38bdf8",
            font=("Segoe UI", 11, "bold")
        )
        self.progress_lbl.pack(side="left")

        self.score_lbl = tk.Label(
            top_bar, text="✅ Mastered: 0   |   🔁 Review: 0", bg="#1e293b", fg="#4ade80",
            font=("Segoe UI", 10, "bold")
        )
        self.score_lbl.pack(side="right")

        bar_frame = tk.Frame(self, bg="#0f172a", padx=24, pady=6)
        bar_frame.pack(fill="x")
        self.mastery_bar = ttk.Progressbar(bar_frame, orient="horizontal", mode="determinate")
        self.mastery_bar.pack(fill="x")

        tool_row = tk.Frame(self, bg="#0f172a", padx=24, pady=2)
        tool_row.pack(fill="x")

        hint_btn = tk.Button(
            tool_row, text="💡 Hint (H)", bg="#334155", fg="#fde047",
            activebackground="#475569", activeforeground="#fde047",
            font=("Segoe UI", 9, "bold"), relief="flat", padx=10, pady=3,
            cursor="hand2", command=self._show_hint
        )
        hint_btn.pack(side="left", padx=(0, 6))
        HoverTooltip(hint_btn, "💡 Peek at a Hint (Key: H)", "Reveals the first few words of the answer to jog your memory without flipping.")

        shuffle_btn = tk.Button(
            tool_row, text="🔀 Shuffle", bg="#334155", fg="#f8fafc",
            activebackground="#475569", activeforeground="white",
            font=("Segoe UI", 9, "bold"), relief="flat", padx=10, pady=3,
            cursor="hand2", command=self._shuffle_deck
        )
        shuffle_btn.pack(side="left", padx=4)
        HoverTooltip(shuffle_btn, "🔀 Shuffle Cards", "Randomizes the order of the flashcards.")

        self.filter_btn = tk.Button(
            tool_row, text="🎯 Study 'Review' Only", bg="#334155", fg="#38bdf8",
            activebackground="#475569", activeforeground="white",
            font=("Segoe UI", 9, "bold"), relief="flat", padx=10, pady=3,
            cursor="hand2", command=self._toggle_review_filter
        )
        self.filter_btn.pack(side="left", padx=4)
        HoverTooltip(self.filter_btn, "🎯 Focus on Weak Cards", "Filters the deck to show only cards marked for Review 🔁.")

        save_deck_btn = tk.Button(
            tool_row, text="💾 Save Deck to Notes", bg="#059669", fg="white",
            activebackground="#047857", activeforeground="white",
            font=("Segoe UI", 9, "bold"), relief="flat", padx=10, pady=3,
            cursor="hand2", command=self._save_deck_to_notes
        )
        save_deck_btn.pack(side="right")
        HoverTooltip(save_deck_btn, "💾 Export All Cards", "Saves this entire Q&A flashcard deck into My_Study_Notes.txt.")

        self.card_frame = tk.Frame(
            self, bg="#1e293b", bd=2, relief="ridge", padx=26, pady=20, cursor="hand2"
        )
        self.card_frame.pack(fill="both", expand=True, padx=24, pady=12)

        self.side_badge = tk.Label(
            self.card_frame, text="❓ QUESTION (Click or Press Space to Flip)",
            bg="#1e293b", fg="#93c5fd", font=("Segoe UI", 9, "bold")
        )
        self.side_badge.pack(anchor="n", pady=(0, 10))

        self.card_text_lbl = tk.Label(
            self.card_frame, text="", bg="#1e293b", fg="#ffffff",
            font=("Segoe UI", 14, "bold"), wraplength=610, justify="center", cursor="hand2"
        )
        self.card_text_lbl.pack(fill="both", expand=True)

        self.hint_lbl = tk.Label(
            self.card_frame, text="", bg="#1e293b", fg="#fde047",
            font=("Segoe UI", 10, "italic"), wraplength=580, justify="center"
        )
        self.hint_lbl.pack(anchor="s", pady=(8, 0))

        for w in (self.card_frame, self.card_text_lbl, self.side_badge, self.hint_lbl):
            w.bind("<Button-1>", lambda e: self._flip_card())

        ctrl_bar = tk.Frame(self, bg="#0f172a", padx=24, pady=6)
        ctrl_bar.pack(fill="x", side="bottom")

        prev_btn = tk.Button(
            ctrl_bar, text="⬅ Prev", bg="#334155", fg="white",
            activebackground="#475569", activeforeground="white",
            font=("Segoe UI", 10, "bold"), relief="flat", width=9, pady=6,
            cursor="hand2", command=self._prev_card
        )
        prev_btn.pack(side="left", padx=(0, 8))

        flip_btn = tk.Button(
            ctrl_bar, text="🔄 Flip Card (Space)", bg="#2563eb", fg="white",
            activebackground="#1d4ed8", activeforeground="white",
            font=("Segoe UI", 10, "bold"), relief="flat", width=15, pady=6,
            cursor="hand2", command=self._flip_card
        )
        flip_btn.pack(side="left", padx=4)

        got_btn = tk.Button(
            ctrl_bar, text="Got It ✅ (1)", bg="#16a34a", fg="white",
            activebackground="#15803d", activeforeground="white",
            font=("Segoe UI", 10, "bold"), relief="flat", width=11, pady=6,
            cursor="hand2", command=self._mark_mastered
        )
        got_btn.pack(side="left", padx=8)

        rev_btn = tk.Button(
            ctrl_bar, text="Review 🔁 (2)", bg="#d97706", fg="white",
            activebackground="#b45309", activeforeground="white",
            font=("Segoe UI", 10, "bold"), relief="flat", width=11, pady=6,
            cursor="hand2", command=self._mark_review
        )
        rev_btn.pack(side="left", padx=4)

        next_btn = tk.Button(
            ctrl_bar, text="Next ➡", bg="#334155", fg="white",
            activebackground="#475569", activeforeground="white",
            font=("Segoe UI", 10, "bold"), relief="flat", width=9, pady=6,
            cursor="hand2", command=self._next_card
        )
        next_btn.pack(side="right")

        tk.Label(
            self, text=f"❤️ {AUTHOR_SIGNATURE}", bg="#0f172a", fg="#f472b6",
            font=("Segoe UI", 8, "bold")
        ).pack(side="bottom", pady=(0, 4))

    def _render_card(self):
        total_all = len(self.all_cards)
        mastered_count = len(self.mastered_ids)
        pct = (mastered_count / max(1, total_all)) * 100
        self.mastery_bar["value"] = pct

        if not self.active_indices:
            self.active_indices = list(range(total_all))
            self.review_only_mode = False
            self.filter_btn.configure(text="🎯 Study 'Review' Only", bg="#334155")

        self.pos = self.pos % len(self.active_indices)
        real_idx = self.active_indices[self.pos]
        card = self.all_cards[real_idx]

        status_tag = ""
        if real_idx in self.mastered_ids:
            status_tag = "  [✅ Mastered]"
        elif real_idx in self.review_ids:
            status_tag = "  [🔁 Needs Review]"

        mode_prefix = "🎯 Review Deck: " if self.review_only_mode else ""
        self.progress_lbl.configure(
            text=f"{mode_prefix}Card {self.pos + 1} of {len(self.active_indices)}{status_tag}"
        )
        self.score_lbl.configure(
            text=f"✅ Mastered: {mastered_count}/{total_all} ({pct:.0f}%)   |   🔁 Review: {len(self.review_ids)}"
        )

        if not self.showing_answer:
            self.card_frame.configure(bg="#1e293b")
            self.side_badge.configure(
                text="❓ QUESTION (Click card or press Spacebar to reveal Answer)",
                bg="#1e293b", fg="#93c5fd"
            )
            self.card_text_lbl.configure(
                text=card["q"], bg="#1e293b", fg="#ffffff", font=("Segoe UI", 14, "bold")
            )
            self.hint_lbl.configure(bg="#1e293b")
            if not self.hint_shown:
                self.hint_lbl.configure(text="")
        else:
            self.card_frame.configure(bg="#062e1e")
            self.side_badge.configure(
                text="💡 ANSWER (Press '1' for Got It ✅  or  '2' for Review 🔁)",
                bg="#062e1e", fg="#86efac"
            )
            self.card_text_lbl.configure(
                text=card["a"], bg="#062e1e", fg="#4ade80", font=("Segoe UI", 13, "bold")
            )
            self.hint_lbl.configure(text="", bg="#062e1e")

    def _show_hint(self):
        if self.showing_answer:
            return
        real_idx = self.active_indices[self.pos]
        ans_words = self.all_cards[real_idx]["a"].split()
        reveal_count = max(2, len(ans_words) // 3)
        hint_preview = " ".join(ans_words[:reveal_count]) + "..."
        self.hint_shown = True
        self.hint_lbl.configure(text=f"💡 Hint: Starts with \"{hint_preview}\"")

    def _shuffle_deck(self):
        random.shuffle(self.active_indices)
        self.pos = 0
        self.showing_answer = False
        self.hint_shown = False
        self._render_card()

    def _toggle_review_filter(self):
        if not self.review_only_mode:
            if not self.review_ids:
                messagebox.showinfo(
                    "No Review Cards Yet",
                    "Mark at least one tough card with 'Review 🔁' first, then click this button to drill your weak cards!"
                )
                return
            self.review_only_mode = True
            self.active_indices = sorted(list(self.review_ids))
            self.filter_btn.configure(text="📚 Show All Cards", bg="#d97706", fg="white")
        else:
            self.review_only_mode = False
            self.active_indices = list(range(len(self.all_cards)))
            self.filter_btn.configure(text="🎯 Study 'Review' Only", bg="#334155", fg="#38bdf8")
        self.pos = 0
        self.showing_answer = False
        self.hint_shown = False
        self._render_card()

    def _save_deck_to_notes(self):
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
            with open(NOTES_EXPORT_PATH, "a", encoding="utf-8") as f:
                f.write(f"=== Flashcard Deck: {self.topic_title} ({timestamp}) ===\n")
                for i, c in enumerate(self.all_cards, 1):
                    f.write(f"Q{i}: {c['q']}\nA{i}: {c['a']}\n\n")
            messagebox.showinfo(
                "Flashcards Saved",
                f"Saved all {len(self.all_cards)} flashcards to:\n{NOTES_EXPORT_PATH}"
            )
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def _flip_card(self):
        self.showing_answer = not self.showing_answer
        self._render_card()

    def _next_card(self):
        self.pos = (self.pos + 1) % len(self.active_indices)
        self.showing_answer = False
        self.hint_shown = False
        self._render_card()

    def _prev_card(self):
        self.pos = (self.pos - 1) % len(self.active_indices)
        self.showing_answer = False
        self.hint_shown = False
        self._render_card()

    def _mark_mastered(self):
        real_idx = self.active_indices[self.pos]
        self.mastered_ids.add(real_idx)
        self.review_ids.discard(real_idx)
        if len(self.mastered_ids) == len(self.all_cards):
            self._render_card()
            messagebox.showinfo(
                "🎉 Deck Mastered!",
                f"Awesome job! You mastered all {len(self.all_cards)} flashcards on '{self.topic_title}'!"
            )
            return
        self._next_card()

    def _mark_review(self):
        real_idx = self.active_indices[self.pos]
        self.review_ids.add(real_idx)
        self.mastered_ids.discard(real_idx)
        self._next_card()


# =====================================================================
# 6. LOCAL SQLITE MEMORY
# =====================================================================
class LocalMemory:
    def __init__(self, db_path: str):
        self.db_path = db_path
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fact TEXT NOT NULL UNIQUE
                )
            """)

    def save_message(self, role: str, content: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO messages (role, content) VALUES (?, ?)", (role, content))

    def load_recent_messages(self, limit: int = 8) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "SELECT role, content FROM (SELECT id, role, content FROM messages ORDER BY id DESC LIMIT ?) ORDER BY id ASC",
                (limit,)
            )
            return [{"role": r[0], "content": r[1]} for r in cur.fetchall()]

    def clear_messages(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM messages")

    def add_fact(self, fact: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT OR IGNORE INTO user_facts (fact) VALUES (?)", (fact.strip(),))

    def get_facts(self) -> list[str]:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("SELECT fact FROM user_facts ORDER BY id ASC")
            return [r[0] for r in cur.fetchall()]


# =====================================================================
# 7. MAIN STUDENT AI DESKTOP APPLICATION
# =====================================================================
class StudentOfflineBot(tk.Tk):
    def __init__(self):
        super().__init__()
        # Hide main window initially while the custom PNG Splash Screen is displayed
        self.withdraw()

        self.title("AI CHATBOT By Ganesh K. Hadpe")
        self.geometry("1100x730")
        self.minsize(880, 560)
        self.configure(bg="#0f172a")

        if os.path.exists(ICON_PATH):
            try:
                self.iconbitmap(ICON_PATH)
            except Exception:
                pass

        # Launch the custom PNG Splash Screen immediately
        self.splash = StartupSplashScreen(self)
        self.update_idletasks()

        self.db = LocalMemory(DB_PATH)
        self.server_proc = None
        self.tts_proc = None
        self.server_port = self._find_free_port()
        self.server_ready = False
        self.is_generating = False
        self.stop_requested = False
        self.ui_queue = queue.Queue()

        self.model_var = tk.StringVar(value=list(MODELS.keys())[0])
        self.persona_var = tk.StringVar(value=list(PERSONAS.keys())[0])
        self.lang_var = tk.StringVar(value="Auto-Detect (Match My Language)")
        self.human_pacing_var = tk.BooleanVar(value=True)
        self.voice_tts_var = tk.BooleanVar(value=False)

        self.messages = []
        self.last_ai_reply = ""
        self.loaded_doc_name = ""
        self.loaded_doc_text = ""

        self.pomo_running = False
        self.pomo_seconds = 25 * 60

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        atexit.register(self._kill_server)

        self._build_interface()
        self._restore_history()

        self.after(30, self._poll_queue)
        threading.Thread(
            target=self._switch_or_init_model_worker,
            args=(self.model_var.get(),),
            daemon=True
        ).start()

    @staticmethod
    def _find_free_port() -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))
            return s.getsockname()[1]

    def _build_interface(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Left Sidebar ---
        sidebar = tk.Frame(self, bg="#1e293b", width=280, padx=16, pady=12)
        sidebar.grid(row=0, column=0, rowspan=3, sticky="nsew")
        sidebar.grid_propagate(False)

        title_lbl = tk.Label(
            sidebar, text="🎓 AI Study Studio", bg="#1e293b", fg="#f8fafc",
            font=("Segoe UI", 16, "bold"), anchor="w"
        )
        title_lbl.pack(fill="x", pady=(0, 8))
        HoverTooltip(
            title_lbl,
            "Offline AI Studio",
            f"❤️ {AUTHOR_SIGNATURE}\n100% local Windows AI assistant running directly on your CPU."
        )

        # 1. AI Brain Selector
        tk.Label(
            sidebar, text="Active AI Brain:", bg="#1e293b", fg="#4ade80",
            font=("Segoe UI", 9, "bold"), anchor="w"
        ).pack(fill="x", pady=(0, 3))

        self.model_menu = ttk.Combobox(
            sidebar, textvariable=self.model_var, values=list(MODELS.keys()), state="readonly"
        )
        self.model_menu.pack(fill="x", pady=(0, 8))
        self.model_menu.bind("<<ComboboxSelected>>", self._on_model_dropdown_change)
        HoverTooltip(
            self.model_menu,
            "🧠 Switch AI Brain (Model)",
            "• Llama-3.2-1B: Fastest for general chat & Hinglish\n"
            "• Qwen2.5-1.5B: Best for Math, Science & Coding\n"
            "• Gemma-2-2B: Best for Marathi & Hindi fluency"
        )

        # 2. Language Selector
        tk.Label(
            sidebar, text="Language Mode:", bg="#1e293b", fg="#38bdf8",
            font=("Segoe UI", 9, "bold"), anchor="w"
        ).pack(fill="x", pady=(0, 3))

        self.lang_menu = ttk.Combobox(
            sidebar, textvariable=self.lang_var, values=LANGUAGE_MODES, state="readonly"
        )
        self.lang_menu.pack(fill="x", pady=(0, 8))
        self.lang_menu.bind("<<ComboboxSelected>>", self._rebuild_system_prompt)
        HoverTooltip(
            self.lang_menu,
            "🌐 Language Detection & Lock",
            "• Auto-Detect: Replies in English when you ask English, or switches to Hinglish/Marathi when you ask in them.\n"
            "• Or lock English, Hinglish, or Marathi manually."
        )

        # 3. Tutor / Bot Style Selector
        tk.Label(
            sidebar, text="Bot Mode / Personality:", bg="#1e293b", fg="#e2e8f0",
            font=("Segoe UI", 9, "bold"), anchor="w"
        ).pack(fill="x", pady=(0, 3))

        persona_menu = ttk.Combobox(
            sidebar, textvariable=self.persona_var, values=list(PERSONAS.keys()), state="readonly"
        )
        persona_menu.pack(fill="x", pady=(0, 8))
        persona_menu.bind("<<ComboboxSelected>>", self._rebuild_system_prompt)
        HoverTooltip(
            persona_menu,
            "🎭 Bot Mode & Personality",
            "• All-Round AI (Gemini Mode): Answer ANYTHING!\n"
            "• Friendly Study Partner: Relatable real-life examples\n"
            "• Exam & Concept Tutor: Structured definitions & revision\n"
            "• Coding Mentor: Code explanations"
        )

        # 4. Checkboxes
        pacing_chk = tk.Checkbutton(
            sidebar, text="Smooth Human Typing", variable=self.human_pacing_var,
            bg="#1e293b", fg="#e2e8f0", selectcolor="#0f172a",
            activebackground="#1e293b", activeforeground="#4ade80",
            font=("Segoe UI", 9), anchor="w"
        )
        pacing_chk.pack(fill="x", pady=(0, 1))
        HoverTooltip(
            pacing_chk,
            "⌨️ Natural Human Rhythm",
            "Adds subtle micro-pauses at periods and question marks so replies stream like a real human typing."
        )

        voice_chk = tk.Checkbutton(
            sidebar, text="🔊 Read Replies Aloud", variable=self.voice_tts_var,
            bg="#1e293b", fg="#fbbf24", selectcolor="#0f172a",
            activebackground="#1e293b", activeforeground="#fbbf24",
            font=("Segoe UI", 9, "bold"), anchor="w"
        )
        voice_chk.pack(fill="x", pady=(0, 8))
        HoverTooltip(
            voice_chk,
            "🔊 Offline Voice Output",
            "Uses Windows' built-in speech synthesizer to read the AI's reply out loud after it finishes typing."
        )

        # 5. PDF Textbook & Notes Controls
        tk.Label(
            sidebar, text="PDF Textbook & Study Notes:", bg="#1e293b", fg="#c084fc",
            font=("Segoe UI", 9, "bold"), anchor="w"
        ).pack(fill="x", pady=(0, 4))

        doc_btn_frame = tk.Frame(sidebar, bg="#1e293b")
        doc_btn_frame.pack(fill="x", pady=(0, 4))
        doc_btn_frame.grid_columnconfigure(0, weight=1)
        doc_btn_frame.grid_columnconfigure(1, weight=1)

        load_file_btn = tk.Button(
            doc_btn_frame, text="📂 Load PDF/File", bg="#3b82f6", fg="white",
            activebackground="#2563eb", activeforeground="white",
            font=("Segoe UI", 9, "bold"), relief="flat", pady=4,
            cursor="hand2", command=self._load_study_file
        )
        load_file_btn.grid(row=0, column=0, padx=(0, 4), sticky="ew")
        HoverTooltip(
            load_file_btn,
            "📂 Load Material (.pdf, .txt, .py, .csv)",
            "Open a local PDF textbook chapter, notes, or code file so the AI can answer questions and create flashcards from it."
        )

        save_notes_btn = tk.Button(
            doc_btn_frame, text="💾 Save Notes", bg="#059669", fg="white",
            activebackground="#047857", activeforeground="white",
            font=("Segoe UI", 9, "bold"), relief="flat", pady=4,
            cursor="hand2", command=self._export_last_reply
        )
        save_notes_btn.grid(row=0, column=1, padx=(4, 0), sticky="ew")
        HoverTooltip(
            save_notes_btn,
            "💾 Export to My_Study_Notes.txt",
            "Saves the AI's last reply with a timestamp into 'My_Study_Notes.txt' in your app folder."
        )

        self.doc_status_label = tk.Label(
            sidebar, text="No PDF or study file loaded", bg="#1e293b", fg="#94a3b8",
            font=("Segoe UI", 8), anchor="w"
        )
        self.doc_status_label.pack(fill="x", pady=(0, 8))

        # 6. Pomodoro Focus Timer
        pomo_frame = tk.Frame(sidebar, bg="#0f172a", padx=10, pady=8)
        pomo_frame.pack(fill="x", pady=(0, 8))

        self.pomo_label = tk.Label(
            pomo_frame, text="⏱️ Focus Timer: 25:00", bg="#0f172a", fg="#38bdf8",
            font=("Segoe UI", 10, "bold"), anchor="w"
        )
        self.pomo_label.pack(fill="x", pady=(0, 4))

        pomo_btns = tk.Frame(pomo_frame, bg="#0f172a")
        pomo_btns.pack(fill="x")
        self.pomo_start_btn = tk.Button(
            pomo_btns, text="Start 25m", bg="#16a34a", fg="white",
            font=("Segoe UI", 8, "bold"), relief="flat", width=10,
            cursor="hand2", command=self._toggle_pomodoro
        )
        self.pomo_start_btn.pack(side="left", padx=(0, 6))

        pomo_reset_btn = tk.Button(
            pomo_btns, text="Reset", bg="#334155", fg="white",
            font=("Segoe UI", 8), relief="flat", width=8,
            cursor="hand2", command=self._reset_pomodoro
        )
        pomo_reset_btn.pack(side="left")

        # 7. Student Profile Fact Input
        self.fact_entry = tk.Entry(
            sidebar, bg="#0f172a", fg="#ffffff", insertbackground="white",
            font=("Segoe UI", 9), relief="flat"
        )
        self.fact_entry.pack(fill="x", ipady=4, pady=(0, 4))
        self.fact_entry.insert(0, "e.g. My name is Alex")
        self.fact_entry.bind(
            "<FocusIn>",
            lambda e: self.fact_entry.delete(0, "end") if self.fact_entry.get().startswith("e.g.") else None
        )
        self.fact_entry.bind("<Return>", lambda e: self._save_user_fact())

        action_row = tk.Frame(sidebar, bg="#1e293b")
        action_row.pack(fill="x", pady=(0, 4))
        action_row.grid_columnconfigure(0, weight=1)
        action_row.grid_columnconfigure(1, weight=1)

        save_fact_btn = tk.Button(
            action_row, text="+ Save Fact", bg="#475569", fg="white",
            font=("Segoe UI", 8, "bold"), relief="flat", pady=4,
            cursor="hand2", command=self._save_user_fact
        )
        save_fact_btn.grid(row=0, column=0, padx=(0, 3), sticky="ew")

        clear_chat_btn = tk.Button(
            action_row, text="Clear Chat", bg="#334155", fg="#f8fafc",
            font=("Segoe UI", 8), relief="flat", pady=4,
            cursor="hand2", command=self._clear_history
        )
        clear_chat_btn.grid(row=0, column=1, padx=(3, 0), sticky="ew")

        # Status & Progress Bar at Bottom
        self.status_label = tk.Label(
            sidebar, text="Status: Starting...", bg="#1e293b", fg="#fbbf24",
            font=("Segoe UI", 9, "bold"), wraplength=245, justify="left", anchor="w"
        )
        self.status_label.pack(side="bottom", fill="x", pady=(4, 0))

        self.progress_bar = ttk.Progressbar(sidebar, orient="horizontal", mode="determinate")
        self.progress_bar.pack(side="bottom", fill="x", pady=(0, 4))

        # --- Top Right: Clean Quick-Actions Bar ---
        study_bar = tk.Frame(self, bg="#1e293b", padx=12, pady=8)
        study_bar.grid(row=0, column=1, padx=16, pady=(14, 0), sticky="ew")

        tk.Label(
            study_bar, text="Student Tools:", bg="#1e293b", fg="#94a3b8",
            font=("Segoe UI", 9, "bold")
        ).pack(side="left", padx=(0, 6))

        quick_tools = [
            (
                "🧒 Explain Simply",
                "Explain this topic in super simple terms with a real-life example: ",
                "🧒 Explain Simply",
                "Type a topic in the bottom box and click here to get a crystal-clear explanation using everyday examples."
            ),
            (
                "📝 Exam Notes",
                "Create structured, bulleted exam revision notes and key definitions for: ",
                "📝 Generate Exam Revision Notes",
                "Turns your typed topic or loaded PDF chapter into structured bullet points, key formulas, and definitions."
            ),
            (
                "❓ Quiz Me",
                "Give me a 3-question Multiple Choice Quiz (MCQs) on this topic. Do NOT show the answers yet—wait for me to reply first: ",
                "❓ 3-Question Practice Quiz",
                "Tests your knowledge with 3 Multiple-Choice Questions (MCQs) and waits for you to answer before grading."
            ),
        ]

        for label, prompt_prefix, tip_title, tip_desc in quick_tools:
            btn = tk.Button(
                study_bar, text=label, bg="#334155", fg="#f8fafc",
                activebackground="#475569", activeforeground="#4ade80",
                font=("Segoe UI", 9, "bold"), relief="flat", padx=9, pady=3,
                cursor="hand2",
                command=lambda p=prompt_prefix: self._trigger_study_tool(p)
            )
            btn.pack(side="left", padx=3)
            HoverTooltip(btn, tip_title, tip_desc)

        flashcard_btn = tk.Button(
            study_bar, text="🃏 Flashcards", bg="#7c3aed", fg="white",
            activebackground="#6d28d9", activeforeground="white",
            font=("Segoe UI", 9, "bold"), relief="flat", padx=10, pady=3,
            cursor="hand2", command=self._generate_flashcards_clicked
        )
        flashcard_btn.pack(side="left", padx=4)
        HoverTooltip(
            flashcard_btn,
            "🃏 Interactive Flashcard Studio 2.0",
            "Generates 5 Q&A cards with Hints (H), Shuffle, Weak-Card Filter, Mastery Bar, and Notes Export!"
        )

        math_btn = tk.Button(
            study_bar, text="🧮 Exact Math", bg="#d97706", fg="white",
            activebackground="#b45309", activeforeground="white",
            font=("Segoe UI", 9, "bold"), relief="flat", padx=10, pady=3,
            cursor="hand2", command=self._solve_math_clicked
        )
        math_btn.pack(side="left", padx=4)
        HoverTooltip(
            math_btn,
            "🧮 Deterministic Python Math Solver",
            "Computes 100% exact answers for arithmetic, trigonometry (sind, cosd), logs, and quadratic equations (2x^2 - 5x + 2 = 0)."
        )

        license_btn = tk.Button(
            study_bar, text="📜 License", bg="#0f172a", fg="#fde047",
            activebackground="#334155", activeforeground="#fde047",
            font=("Segoe UI", 9, "bold"), relief="flat", padx=9, pady=3,
            cursor="hand2", command=self._show_license_popup
        )
        license_btn.pack(side="right", padx=2)
        HoverTooltip(
            license_btn,
            "📜 Software License & Copyright",
            "View official license and copyright information (Licensed to Ganesh K. Hadpe)."
        )

        # --- Center Right: Smooth Modern Chat Canvas ---
        chat_container = tk.Frame(self, bg="#090d16", bd=0)
        chat_container.grid(row=1, column=1, padx=16, pady=(10, 10), sticky="nsew")
        chat_container.grid_rowconfigure(0, weight=1)
        chat_container.grid_columnconfigure(0, weight=1)

        self.chat_box = tk.Text(
            chat_container, bg="#090d16", fg="#ffffff", insertbackground="white",
            font=("Segoe UI", 11), wrap="word", relief="flat",
            padx=20, pady=14, spacing1=0, spacing2=1, spacing3=0,
            state="disabled", cursor="arrow"
        )
        self.chat_box.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(chat_container, orient="vertical", command=self.chat_box.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.chat_box.configure(yscrollcommand=scrollbar.set)

        self.chat_box.tag_config(
            "author_banner", foreground="#fde047", background="#1e293b",
            font=("Segoe UI", 11, "bold"), spacing1=4, spacing3=8
        )
        self.chat_box.tag_config(
            "user_badge", foreground="#93c5fd", font=("Segoe UI", 10, "bold"), spacing1=14, spacing3=2
        )
        self.chat_box.tag_config(
            "user", foreground="#ffffff", font=("Segoe UI", 11, "bold"), spacing1=0, spacing3=0
        )
        self.chat_box.tag_config(
            "bot_badge", foreground="#4ade80", font=("Segoe UI", 10, "bold"), spacing1=12, spacing3=2
        )
        self.chat_box.tag_config(
            "bot", foreground="#4ade80", font=("Segoe UI", 11), spacing1=0, spacing3=0
        )
        self.chat_box.tag_config(
            "bot_bold", foreground="#86efac", font=("Segoe UI", 11, "bold"), spacing1=0, spacing3=0
        )
        self.chat_box.tag_config(
            "bot_code", foreground="#fde047", background="#1e293b", font=("Consolas", 10)
        )
        self.chat_box.tag_config(
            "math_verified", foreground="#fbbf24", background="#1e293b",
            font=("Consolas", 11, "bold"), spacing1=6, spacing3=4
        )
        self.chat_box.tag_config(
            "system", foreground="#94a3b8", font=("Segoe UI", 10, "italic"), spacing1=6, spacing3=4
        )

        # --- Bottom Right: Smooth Input Bar ---
        bottom_frame = tk.Frame(self, bg="#0f172a")
        bottom_frame.grid(row=2, column=1, padx=16, pady=(0, 16), sticky="ew")
        bottom_frame.grid_columnconfigure(0, weight=1)

        self.entry_box = tk.Entry(
            bottom_frame, bg="#1e293b", fg="#ffffff", insertbackground="white",
            font=("Segoe UI", 11), relief="flat"
        )
        self.entry_box.grid(row=0, column=0, ipady=9, padx=(0, 10), sticky="ew")
        self.entry_box.bind("<Return>", lambda event: self._send_message())

        self.send_btn = tk.Button(
            bottom_frame, text="Send ➤", bg="#16a34a", fg="white",
            activebackground="#15803d", activeforeground="white",
            font=("Segoe UI", 10, "bold"), relief="flat", width=11, pady=7,
            state="disabled", cursor="hand2", command=self._send_message
        )
        self.send_btn.grid(row=0, column=1, padx=(0, 6))

        self.stop_btn = tk.Button(
            bottom_frame, text="Stop ⏹", bg="#dc2626", fg="white",
            activebackground="#b91c1c", activeforeground="white",
            font=("Segoe UI", 10, "bold"), relief="flat", width=8, pady=7,
            state="disabled", cursor="hand2", command=self._stop_generation
        )
        self.stop_btn.grid(row=0, column=2)

    def _show_license_popup(self):
        messagebox.showinfo("Software License — Ganesh K. Hadpe", LICENSE_TEXT)

    # =================================================================
    # 8. STUDENT TOOLS: FLASHCARDS 2.0, PDF READER & EXACT MATH
    # =================================================================
    def _trigger_study_tool(self, prompt_prefix: str):
        if self.is_generating or not self.server_ready:
            return
        typed_topic = self.entry_box.get().strip()
        if not typed_topic and self.loaded_doc_text:
            typed_topic = f"the loaded study file ({self.loaded_doc_name})"
        elif not typed_topic:
            self._append_text(
                "💡 Tip: Type a topic or question in the box below first (or load a PDF/file), then click a button!\n",
                "system"
            )
            self.entry_box.focus_set()
            return

        self.entry_box.delete(0, "end")
        self.entry_box.insert(0, f"{prompt_prefix}{typed_topic}")
        self._send_message()

    def _solve_math_clicked(self):
        if self.is_generating:
            return
        expr = self.entry_box.get().strip()
        if not expr:
            self._append_text(
                "🧮 Math Solver Tip: Type any math expression or equation in the box below "
                "(e.g., 'sqrt(625) * 18 + log10(1000)' or '2x^2 - 7x + 3 = 0') and click '🧮 Exact Math'!\n",
                "system"
            )
            self.entry_box.focus_set()
            return

        exact_ans = ExactMathSolver.try_evaluate(expr)
        if exact_ans:
            self._append_text("You (Math Query)\n", "user_badge")
            self._append_text(f"{expr}\n", "user")
            self._append_text(f"  🧮 Verified Python Math Engine: {exact_ans}  \n", "math_verified")
            if self.server_ready:
                self.entry_box.delete(0, "end")
                self.entry_box.insert(
                    0, f"Explain step-by-step how to solve {expr} where the verified answer is {exact_ans}"
                )
                self._send_message()
        else:
            self._trigger_study_tool("Solve this math/science problem step-by-step showing all formulas: ")

    def _generate_flashcards_clicked(self):
        if self.is_generating or not self.server_ready:
            return

        topic = self.entry_box.get().strip()
        if not topic and self.loaded_doc_text:
            topic = f"the loaded material ({self.loaded_doc_name})"
        elif not topic and self.last_ai_reply:
            topic = "our last study topic"
        elif not topic:
            self._append_text(
                "🃏 Flashcards Tip: Type a subject or chapter topic in the box below (or load a PDF) "
                "and click '🃏 Flashcards' to launch the interactive card flipper!\n",
                "system"
            )
            self.entry_box.focus_set()
            return

        self.entry_box.delete(0, "end")
        self.is_generating = True
        self.send_btn.configure(state="disabled")
        self.status_label.configure(text="Status: Creating 5 Flashcards...", fg="#c084fc")
        self._append_text(f"🃏 Generating 5 high-recall flashcards for '{topic}'...\n", "system")

        threading.Thread(
            target=self._flashcard_worker,
            args=(topic,),
            daemon=True
        ).start()

    def _flashcard_worker(self, topic: str):
        try:
            source_context = ""
            if self.loaded_doc_text:
                source_context = f"\nUse this study material:\n{self.loaded_doc_text[:1800]}\n"
            elif self.last_ai_reply:
                source_context = f"\nUse this recent lesson context:\n{self.last_ai_reply[:1200]}\n"

            fc_messages = [
                {
                    "role": "system",
                    "content": (
                        "You are an expert academic flashcard creator. "
                        "Generate exactly 5 high-value exam flashcards. "
                        "Every single line MUST follow the exact format: Q: [Question] | A: [Concise Answer]"
                    )
                },
                {
                    "role": "user",
                    "content": "Create 2 example flashcards about: Photosynthesis"
                },
                {
                    "role": "assistant",
                    "content": (
                        "Q: What is the primary pigment used by plants to absorb light during photosynthesis? | A: Chlorophyll, located inside the chloroplasts.\n"
                        "Q: What are the two main stages of photosynthesis? | A: The Light-dependent reactions and the Calvin Cycle (Light-independent reactions)."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Now create exactly 5 study flashcards about: {topic}.{source_context}\n"
                        "Output ONLY the 5 lines in the exact 'Q: ... | A: ...' format with no intro or outro."
                    )
                }
            ]

            payload = json.dumps({
                "messages": fc_messages,
                "max_tokens": 500,
                "temperature": 0.45,
                "repeat_penalty": 1.15,
                "stream": False
            }).encode("utf-8")

            req = urllib.request.Request(
                f"http://127.0.0.1:{self.server_port}/v1/chat/completions",
                data=payload,
                headers={"Content-Type": "application/json"}
            )

            with urllib.request.urlopen(req, timeout=90) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                raw_output = data["choices"][0]["message"]["content"]

            cards = self._parse_flashcards(raw_output, topic)
            self.ui_queue.put(("open_flashcards", (topic, cards)))

        except Exception as e:
            self.ui_queue.put(("append", (f"\n[Flashcard Error: {e}]\n", "system")))
            self.ui_queue.put(("done", "Ready"))

    @staticmethod
    def _parse_flashcards(raw_text: str, topic: str) -> list[dict]:
        cleaned_text = raw_text.replace("**", "").strip()
        cards = []

        for line in cleaned_text.splitlines():
            line_clean = re.sub(r"^[\d\-\*\.\)\s]+", "", line.strip())
            if "|" in line_clean:
                parts = line_clean.split("|", 1)
                q_part = re.sub(r"^(?:Q\d*|Question\s*\d*|Front)\s*[:\-]\s*", "", parts[0].strip(), flags=re.IGNORECASE)
                a_part = re.sub(r"^(?:A\d*|Answer\s*\d*|Back)\s*[:\-]\s*", "", parts[1].strip(), flags=re.IGNORECASE)
                if len(q_part) > 3 and len(a_part) > 1:
                    cards.append({"q": q_part, "a": a_part})

        if len(cards) < 2:
            cards = []
            matches = re.findall(
                r"(?:Q\d*|Question\s*\d*|Front)\s*[:\-\.]\s*(.+?)\s*(?:\n+|\s*\|\s*)\s*(?:A\d*|Answer\s*\d*|Back)\s*[:\-\.]\s*(.+)",
                cleaned_text,
                flags=re.IGNORECASE
            )
            for q_m, a_m in matches:
                q_s = q_m.strip()
                a_s = a_m.strip()
                if q_s and a_s:
                    cards.append({"q": q_s, "a": a_s})

        if not cards:
            lines = [ln.strip() for ln in cleaned_text.splitlines() if ln.strip()]
            i = 0
            while i < len(lines) - 1:
                if "?" in lines[i]:
                    q_s = re.sub(r"^[\d\-\*\.\)\sQ:]+", "", lines[i]).strip()
                    a_s = re.sub(r"^(?:A|Answer)\s*[:\-]\s*", "", lines[i + 1], flags=re.IGNORECASE).strip()
                    if q_s and a_s:
                        cards.append({"q": q_s, "a": a_s})
                        i += 2
                        continue
                i += 1

        if not cards:
            cards.append({
                "q": f"What is the core concept of {topic}?",
                "a": cleaned_text[:320] or "Try entering a specific topic like 'Newton's Laws' or 'Python Lists'."
            })
        return cards[:8]

    def _load_study_file(self):
        file_path = filedialog.askopenfilename(
            title="Select PDF Textbook, Study Notes, Code, or CSV File",
            filetypes=[
                ("Study & PDF Files", "*.pdf *.txt *.md *.py *.csv *.json"),
                ("PDF Textbooks", "*.pdf"),
                ("All Files", "*.*")
            ]
        )
        if not file_path:
            return

        ext = os.path.splitext(file_path)[1].lower()
        self.loaded_doc_name = os.path.basename(file_path)

        try:
            if ext == ".pdf":
                if not PDF_AVAILABLE:
                    messagebox.showwarning("PDF Library Missing", "pypdf is not installed yet.")
                    return

                reader = PdfReader(file_path)
                total_pages = len(reader.pages)
                extracted_pages = []
                char_count = 0

                for idx, page in enumerate(reader.pages):
                    page_txt = page.extract_text() or ""
                    if page_txt.strip():
                        extracted_pages.append(f"[Page {idx + 1}] {page_txt.strip()}")
                        char_count += len(page_txt)
                    if char_count >= 4000:
                        break

                self.loaded_doc_text = "\n".join(extracted_pages)[:4200].strip()
                if not self.loaded_doc_text:
                    messagebox.showwarning(
                        "Scanned PDF",
                        "This PDF appears to contain scanned images rather than selectable text."
                    )
                    return

                self.doc_status_label.configure(
                    text=f"📕 PDF: {self.loaded_doc_name[:20]} ({total_pages}p)", fg="#4ade80"
                )
                self._append_text(
                    f"📕 Loaded PDF Textbook: '{self.loaded_doc_name}' ({total_pages} total pages, "
                    f"{len(self.loaded_doc_text)} chars indexed).\n",
                    "system"
                )
            else:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    raw_text = f.read()
                self.loaded_doc_text = raw_text[:4000].strip()
                self.doc_status_label.configure(
                    text=f"📄 Active: {self.loaded_doc_name[:22]}", fg="#4ade80"
                )
                self._append_text(
                    f"📂 Loaded study file: '{self.loaded_doc_name}' ({len(self.loaded_doc_text)} chars).\n",
                    "system"
                )
        except Exception as e:
            messagebox.showerror("File Error", f"Could not read file:\n{e}")

    def _export_last_reply(self):
        if not self.last_ai_reply.strip():
            messagebox.showinfo("No Notes Yet", "Ask the AI a question first, then click Save Notes!")
            return
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
            with open(NOTES_EXPORT_PATH, "a", encoding="utf-8") as f:
                f.write(f"=== Study Note ({timestamp}) ===\n")
                f.write(self.last_ai_reply.strip() + "\n\n")
            self._append_text(
                f"💾 Saved last AI explanation to: {NOTES_EXPORT_PATH}\n", "system"
            )
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def _toggle_pomodoro(self):
        self.pomo_running = not self.pomo_running
        if self.pomo_running:
            self.pomo_start_btn.configure(text="Pause", bg="#d97706")
            self._tick_pomodoro()
        else:
            self.pomo_start_btn.configure(text="Resume", bg="#16a34a")

    def _reset_pomodoro(self):
        self.pomo_running = False
        self.pomo_seconds = 25 * 60
        self.pomo_label.configure(text="⏱️ Focus Timer: 25:00", fg="#38bdf8")
        self.pomo_start_btn.configure(text="Start 25m", bg="#16a34a")

    def _tick_pomodoro(self):
        if not self.pomo_running:
            return
        if self.pomo_seconds > 0:
            self.pomo_seconds -= 1
            mins, secs = divmod(self.pomo_seconds, 60)
            self.pomo_label.configure(text=f"⏱️ Focus Timer: {mins:02d}:{secs:02d}")
            self.after(1000, self._tick_pomodoro)
        else:
            self.pomo_running = False
            self.pomo_label.configure(text="🎉 25m Session Complete!", fg="#4ade80")
            self.pomo_start_btn.configure(text="Start 25m", bg="#16a34a")
            self._append_text(
                "🎉 Pomodoro Complete! Great job studying for 25 minutes—take a 5 minute water break!\n",
                "system"
            )
            self._speak_offline_windows("Great job! Your 25 minute study session is complete. Take a 5 minute break.")

    # =================================================================
    # 9. ACCURATE LANGUAGE DETECTOR & ZERO-DOLLAR-SIGN SPEECH ENGINE
    # =================================================================
    def _detect_user_language(self, text: str) -> str:
        chosen_mode = self.lang_var.get()
        if chosen_mode == "English Only":
            return "english"
        if "Marathi" in chosen_mode and "Devanagari" not in chosen_mode:
            return "marathi_roman"
        if "Hinglish" in chosen_mode:
            return "hinglish"
        if "Devanagari" in chosen_mode:
            return "devanagari"

        if re.search(r"[\u0900-\u097F]", text):
            return "devanagari"

        words = re.findall(r"[a-zA-Z]+", text.lower())
        if not words:
            return "english"
        word_set = set(words)

        marathi_markers = {
            "tumhi", "mala", "tula", "karal", "madat", "aahe", "aahet",
            "kasa", "kashi", "nakki", "sanga", "bhau", "majha", "tumcha", "kuthe",
            "barobar", "chhan", "mahit", "shakto", "shakte", "pahije", "abhyas",
            "vishay", "konta", "kiwa", "bhashet", "samjun", "kalji", "naka"
        }
        hinglish_markers = {
            "kya", "aap", "meri", "mera", "madad", "sakte", "sakta", "hain",
            "hai", "hoon", "bhai", "yaar", "batao", "kaise", "kaisa", "mujhe",
            "tum", "achha", "theek", "bilkul", "chahiye", "karo", "karna",
            "samjhao", "aur", "nahi", "kaunsa", "padhna", "aasaan"
        }

        marathi_hits = len(word_set.intersection(marathi_markers))
        hinglish_hits = len(word_set.intersection(hinglish_markers))

        if marathi_hits >= 1 and marathi_hits >= hinglish_hits:
            return "marathi_roman"
        if hinglish_hits >= 1:
            return "hinglish"
        return "english"

    def _speak_offline_windows(self, text: str):
        if not self.voice_tts_var.get() or not text.strip():
            return
        try:
            if self.tts_proc and self.tts_proc.poll() is None:
                self.tts_proc.terminate()
            clean_text = re.sub(r"[*#`~_]", "", text).strip()[:500]
            if not clean_text:
                return

            env = os.environ.copy()
            env["SPEECH_TEXT"] = clean_text
            ps_cmd = (
                "Add-Type -AssemblyName System.Speech; "
                "(New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak("
                "[System.Environment]::GetEnvironmentVariable('SPEECH_TEXT'))"
            )
            creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
            self.tts_proc = subprocess.Popen(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd],
                env=env,
                creationflags=creation_flags
            )
        except Exception:
            pass

    # =================================================================
    # 10. ENGINE & DYNAMIC MODEL SWITCHER
    # =================================================================
    def _on_model_dropdown_change(self, _event=None):
        if self.is_generating:
            self.stop_requested = True
        chosen_model = self.model_var.get()
        self.server_ready = False
        self.send_btn.configure(state="disabled")
        self._append_text(f"🔄 Switching AI Brain to: {chosen_model}...\n", "system")
        threading.Thread(
            target=self._switch_or_init_model_worker,
            args=(chosen_model,),
            daemon=True
        ).start()

    def _download_with_progress(self, url: str, dest_path: str, label_prefix: str):
        if not url.startswith("https://"):
            raise ValueError("Security policy: Only HTTPS download URLs are permitted.")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        temp_path = dest_path + ".part"
        with urllib.request.urlopen(req, timeout=60) as resp, open(temp_path, "wb") as out:
            total = int(resp.headers.get("Content-Length", 0))
            downloaded = 0
            while True:
                chunk = resp.read(65536)
                if not chunk:
                    break
                out.write(chunk)
                downloaded += len(chunk)
                if total > 0:
                    pct = min(100.0, (downloaded / total) * 100)
                    mb_done = downloaded / (1024 * 1024)
                    mb_total = total / (1024 * 1024)
                    self.ui_queue.put((
                        "progress",
                        (pct, f"{label_prefix}: {pct:.1f}% ({mb_done:.0f}/{mb_total:.0f} MB)")
                    ))
        os.replace(temp_path, dest_path)

    def _find_cpu_engine_url(self) -> str:
        req = urllib.request.Request(GITHUB_RELEASES_API, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            releases = json.loads(resp.read().decode("utf-8"))
        for rel in releases:
            for asset in rel.get("assets", []):
                name = asset.get("name", "")
                dl_url = asset.get("browser_download_url", "")
                if name.endswith("bin-win-cpu-x64.zip") and dl_url.startswith("https://"):
                    return dl_url
        raise RuntimeError("Could not find bin-win-cpu-x64.zip on GitHub.")

    def _switch_or_init_model_worker(self, model_key: str):
        try:
            os.makedirs(MODEL_DIR, exist_ok=True)
            os.makedirs(ENGINE_DIR, exist_ok=True)

            self._kill_server()

            if not os.path.exists(SERVER_EXE):
                self.ui_queue.put(("append", ("⚙️ Installing Universal CPU Engine (~25 MB)...\n", "system")))
                zip_url = self._find_cpu_engine_url()
                zip_path = os.path.join(ENGINE_DIR, "llama_cpu_engine.zip")
                self._download_with_progress(zip_url, zip_path, "Engine")

                allowed_exts = {".exe", ".dll"}
                with zipfile.ZipFile(zip_path, "r") as zf:
                    for member in zf.infolist():
                        if member.is_dir():
                            continue
                        fname = os.path.basename(member.filename)
                        ext = os.path.splitext(fname)[1].lower()
                        if fname and ext in allowed_exts:
                            target = os.path.join(ENGINE_DIR, fname)
                            with zf.open(member) as src, open(target, "wb") as dst:
                                shutil.copyfileobj(src, dst)
                os.remove(zip_path)

            model_info = MODELS[model_key]
            model_path = os.path.join(MODEL_DIR, model_info["filename"])

            if not os.path.exists(model_path):
                self.ui_queue.put(("append", (
                    f"⬇️ First-time download for {model_key}...\n"
                    f"Saving to ./models/{model_info['filename']}\n",
                    "system"
                )))
                self._download_with_progress(model_info["url"], model_path, "Model")

            self.ui_queue.put(("progress", (100, f"Loading {model_info['filename']} into RAM...")))
            self.server_port = self._find_free_port()
            creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

            self.server_proc = subprocess.Popen(
                [
                    SERVER_EXE,
                    "-m", model_path,
                    "-c", "2048",
                    "-t", str(CPU_THREADS),
                    "--host", "127.0.0.1",
                    "--port", str(self.server_port)
                ],
                cwd=ENGINE_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=creation_flags
            )

            health_url = f"http://127.0.0.1:{self.server_port}/health"
            for _ in range(180):
                if self.server_proc.poll() is not None:
                    out = self.server_proc.stdout.read() if self.server_proc.stdout else ""
                    raise RuntimeError(f"Engine exited early:\n{out[-350:]}")
                try:
                    with urllib.request.urlopen(health_url, timeout=1) as resp:
                        if resp.status == 200:
                            self.server_ready = True
                            self.ui_queue.put(("ready", model_key))
                            return
                except Exception:
                    time.sleep(0.5)

            raise RuntimeError("Timed out loading model into RAM.")

        except Exception as e:
            self.ui_queue.put(("status", (f"Error: {e}", "#f87171")))
            self.ui_queue.put(("append", (f"\n❌ Error: {e}\n", "system")))

    # =================================================================
    # 11. STRICT LANGUAGE-LOCKED PROMPT BUILDER & STREAMING CHAT
    # =================================================================
    def _build_system_message(self, detected_lang: str = "english", verified_math: str = None) -> str:
        now_str = datetime.datetime.now().strftime("%A, %I:%M %p")
        persona_prompt = PERSONAS[self.persona_var.get()]

        if detected_lang == "english":
            lang_rule = (
                "CRITICAL LANGUAGE RULE: The user is writing in ENGLISH. "
                "You MUST reply 100% in clear, natural ENGLISH only. "
                "Do NOT use any Hindi, Hinglish, or Marathi words, even if older messages in the chat used them."
            )
        elif detected_lang == "marathi_roman":
            lang_rule = (
                "CRITICAL LANGUAGE RULE: The user is speaking in Roman Marathi (Minglish). "
                "Reply ONLY in warm, natural Roman Marathi using the English alphabet "
                "(e.g., 'Ho nakki! Sanga mi tumchi kay madat karu shakto?')."
            )
        elif detected_lang == "hinglish":
            lang_rule = (
                "CRITICAL LANGUAGE RULE: The user is speaking in Roman Hinglish. "
                "Reply ONLY in warm, natural Roman Hinglish using the English alphabet "
                "(e.g., 'Haan bilkul! Batao main aapki kya madad kar sakta hoon?')."
            )
        else:
            lang_rule = (
                "CRITICAL LANGUAGE RULE: Reply in pure, natural Hindi (हिंदी) or Marathi (मराठी) "
                "using Devanagari script."
            )

        base_prompt = f"{persona_prompt}\n{lang_rule}\nCurrent local time: {now_str}."
        facts = self.db.get_facts()
        if facts:
            facts_str = "; ".join(facts)
            base_prompt += f"\nUser profile facts: {facts_str}."

        if self.loaded_doc_text:
            base_prompt += (
                f"\n\n--- LOADED STUDY MATERIAL ({self.loaded_doc_name}) ---\n"
                f"{self.loaded_doc_text}\n"
                "--- END STUDY MATERIAL ---\n"
                "Use the loaded study material above whenever the user asks about it."
            )

        if verified_math:
            base_prompt += (
                f"\n\nCRITICAL MATH FACT: Python's exact math engine verified that {verified_math}. "
                "Use this exact result in your explanation and do NOT contradict it."
            )
        return base_prompt

    def _rebuild_system_prompt(self, _event=None):
        if self.messages and self.messages[0]["role"] == "system":
            self.messages[0]["content"] = self._build_system_message()
        else:
            self.messages.insert(0, {"role": "system", "content": self._build_system_message()})

    def _save_user_fact(self):
        fact = self.fact_entry.get().strip()
        if not fact or fact.startswith("e.g."):
            return
        self.db.add_fact(fact)
        self.fact_entry.delete(0, "end")
        self._rebuild_system_prompt()
        self._append_text(f"🧠 Saved to user profile: \"{fact}\"\n", "system")

    def _auto_extract_facts(self, user_text: str):
        patterns = [
            r"\b(my name is [a-zA-Z0-9_ -]+)",
            r"\b(mera naam [a-zA-Z0-9_ -]+ hai)",
            r"\b(majha naav [a-zA-Z0-9_ -]+ aahe)",
            r"\b(i study [a-zA-Z0-9_ -]+)",
            r"\b(i am in [a-zA-Z0-9_ -]+)"
        ]
        for pat in patterns:
            match = re.search(pat, user_text, re.IGNORECASE)
            if match:
                extracted = match.group(1).strip()
                if len(extracted) < 60:
                    self.db.add_fact(extracted)

    def _restore_history(self):
        self.messages = [{"role": "system", "content": self._build_system_message("english")}]
        self._append_text(f"  ❤️ {AUTHOR_SIGNATURE}  \n", "author_banner")

        recent = self.db.load_recent_messages(limit=8)
        if recent:
            self._append_text("--- Restored Chat Session ---\n", "system")
            for msg in recent:
                self.messages.append(msg)
                if msg["role"] == "user":
                    self._append_text("You\n", "user_badge")
                    self._append_text(f"{msg['content'].strip()}\n", "user")
                else:
                    self._append_text("AI Assistant\n", "bot_badge")
                    compact_reply = re.sub(r"\n{2,}", "\n", msg["content"].strip())
                    self._append_formatted_bot_text(f"{compact_reply}\n")
        else:
            self._append_text(
                "👋 Welcome to your Offline AI Studio!\n"
                "• Set to 'All-Round AI (Gemini Mode)'—ask anything: life, code, ideas, or study topics!\n"
                "• Hover over any button to see tooltips, or switch Study Modes anytime on the left.\n",
                "system"
            )

    def _clear_history(self):
        if self.is_generating:
            return
        self.db.clear_messages()
        self.messages = [{"role": "system", "content": self._build_system_message("english")}]
        self.chat_box.configure(state="normal")
        self.chat_box.delete("1.0", "end")
        self.chat_box.configure(state="disabled")
        self._append_text(f"  ❤️ {AUTHOR_SIGNATURE}  \n", "author_banner")
        self._append_text("✨ Chat cleared (saved profile facts kept).\n", "system")

    def _stop_generation(self):
        if self.is_generating:
            self.stop_requested = True
        if self.tts_proc and self.tts_proc.poll() is None:
            try:
                self.tts_proc.terminate()
            except Exception:
                pass

    def _send_message(self):
        if self.is_generating or not self.server_ready:
            return
        user_text = self.entry_box.get().strip()
        if not user_text:
            return

        self.entry_box.delete(0, "end")
        self._auto_extract_facts(user_text)

        detected_lang = self._detect_user_language(user_text)
        verified_math = ExactMathSolver.try_evaluate(user_text)

        self._append_text("You\n", "user_badge")
        self._append_text(f"{user_text}\n", "user")

        if verified_math:
            self._append_text(f"  🧮 Verified Python Math Engine: {verified_math}  \n", "math_verified")

        badge_name = "AI Assistant" if "Gemini" in self.persona_var.get() else "AI Tutor"
        self._append_text(f"{badge_name}\n", "bot_badge")

        self.messages[0] = {
            "role": "system",
            "content": self._build_system_message(detected_lang, verified_math)
        }
        self.messages.append({"role": "user", "content": user_text})
        self.db.save_message("user", user_text)

        self.is_generating = True
        self.stop_requested = False
        self.send_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")

        lang_badge = {
            "english": "English",
            "hinglish": "Hinglish",
            "marathi_roman": "Marathi",
            "devanagari": "Devanagari"
        }.get(detected_lang, "English")

        self.status_label.configure(
            text=f"Status: Replying in {lang_badge}...",
            fg="#38bdf8"
        )

        threading.Thread(
            target=self._generate_worker,
            args=(detected_lang,),
            daemon=True
        ).start()

    def _generate_worker(self, detected_lang: str):
        full_reply = ""
        tokens = 0
        t0 = time.perf_counter()
        prev_ended_with_newline = False

        try:
            context = [self.messages[0]]

            if detected_lang in MULTILINGUAL_EXAMPLES:
                context.extend(MULTILINGUAL_EXAMPLES[detected_lang])
                recent_slice = [dict(m) for m in self.messages[-6:]]
            else:
                recent_slice = []
                for m in self.messages[-6:]:
                    recent_slice.append(dict(m))

            if recent_slice and recent_slice[-1]["role"] == "user":
                last_content = recent_slice[-1]["content"]
                if detected_lang == "english":
                    recent_slice[-1]["content"] = (
                        f"{last_content}\n\n[Instruction: Reply strictly in English only. Do not use Hindi or Marathi.]"
                    )
                elif detected_lang == "marathi_roman":
                    recent_slice[-1]["content"] = (
                        f"{last_content}\n\n[Instruction: Reply in conversational Roman Marathi (Minglish).]"
                    )
                elif detected_lang == "hinglish":
                    recent_slice[-1]["content"] = (
                        f"{last_content}\n\n[Instruction: Reply in conversational Roman Hinglish.]"
                    )

            context.extend(recent_slice)

            payload = json.dumps({
                "messages": context,
                "max_tokens": 600,
                "temperature": 0.70,
                "min_p": 0.06,
                "repeat_penalty": 1.15,
                "stream": True
            }).encode("utf-8")

            req = urllib.request.Request(
                f"http://127.0.0.1:{self.server_port}/v1/chat/completions",
                data=payload,
                headers={"Content-Type": "application/json"}
            )

            with urllib.request.urlopen(req, timeout=120) as resp:
                for raw_line in resp:
                    if self.stop_requested:
                        self.ui_queue.put(("append", (" [Stopped]", "system")))
                        break
                    line = raw_line.decode("utf-8", errors="ignore").strip()
                    if not line.startswith("data: "):
                        continue
                    data_str = line[6:].strip()
                    if data_str == "[DONE]":
                        break
                    chunk = json.loads(data_str)
                    delta = chunk["choices"][0]["delta"].get("content", "")
                    if delta:
                        full_reply += delta
                        tokens += 1

                        clean_delta = delta.replace("**", "")
                        clean_delta = re.sub(r"\n{2,}", "\n", clean_delta)
                        if prev_ended_with_newline and clean_delta.startswith("\n"):
                            clean_delta = clean_delta.lstrip("\n")

                        if clean_delta:
                            prev_ended_with_newline = clean_delta.endswith("\n")
                            self.ui_queue.put(("append", (clean_delta, "bot")))

                        if self.human_pacing_var.get() and any(p in delta for p in (".", "!", "?")):
                            time.sleep(0.04)

            elapsed = max(0.001, time.perf_counter() - t0)
            speed = tokens / elapsed

            if full_reply.strip():
                self.last_ai_reply = full_reply
                self.messages.append({"role": "assistant", "content": full_reply})
                self.db.save_message("assistant", full_reply)
                if not self.stop_requested:
                    self._speak_offline_windows(full_reply)

            self.ui_queue.put(("done", f"Ready • Speed: {speed:.1f} tokens/sec"))

        except Exception as e:
            self.ui_queue.put(("append", (f"\n[Error: {e}]", "system")))
            self.ui_queue.put(("done", "Error during reply"))

    # =================================================================
    # 12. SMOOTH TYPOGRAPHY RENDERER & UI QUEUE
    # =================================================================
    def _append_text(self, text: str, tag: str = "system"):
        self.chat_box.configure(state="normal")
        self.chat_box.insert("end", text, tag)
        self.chat_box.see("end")
        self.chat_box.configure(state="disabled")

    def _append_formatted_bot_text(self, text: str):
        self.chat_box.configure(state="normal")
        tokens = re.split(r"(\*\*.*?\*\*|`.*?`)", text)
        for part in tokens:
            if part.startswith("**") and part.endswith("**") and len(part) > 4:
                self.chat_box.insert("end", part[2:-2], "bot_bold")
            elif part.startswith("`") and part.endswith("`") and len(part) > 2:
                self.chat_box.insert("end", f" {part[1:-1]} ", "bot_code")
            else:
                self.chat_box.insert("end", part, "bot")
        self.chat_box.see("end")
        self.chat_box.configure(state="disabled")

    def _poll_queue(self):
        try:
            while True:
                kind, data = self.ui_queue.get_nowait()
                if kind == "append":
                    if isinstance(data, tuple):
                        text, tag = data
                    else:
                        text, tag = data, "system"
                    self._append_text(text, tag)
                elif kind == "progress":
                    pct, msg = data
                    self.progress_bar["value"] = pct
                    self.status_label.configure(text=msg, fg="#fbbf24")
                elif kind == "status":
                    msg, color = data
                    self.status_label.configure(text=msg, fg=color)
                elif kind == "ready":
                    self.progress_bar["value"] = 100
                    self.status_label.configure(text=f"Active: {data.split()[0]} ✔", fg="#4ade80")
                    self.send_btn.configure(state="normal")
                    self._append_text(f"✅ {data} is loaded and ready!\n", "system")
                elif kind == "open_flashcards":
                    topic, cards = data
                    self.is_generating = False
                    self.send_btn.configure(state="normal")
                    self.stop_btn.configure(state="disabled")
                    self.status_label.configure(text="Flashcards Ready ✔", fg="#4ade80")
                    self._append_text(
                        f"🃏 Opened Flashcard Studio with {len(cards)} cards for '{topic}'!\n",
                        "system"
                    )
                    FlashcardFlipperPopup(self, topic, cards)
                elif kind == "done":
                    self._append_text("\n", "bot")
                    self.is_generating = False
                    self.send_btn.configure(state="normal")
                    self.stop_btn.configure(state="disabled")
                    self.status_label.configure(text=data, fg="#4ade80")
        except queue.Empty:
            pass
        finally:
            self.after(30, self._poll_queue)

    def _kill_server(self):
        if self.tts_proc and self.tts_proc.poll() is None:
            try:
                self.tts_proc.terminate()
            except Exception:
                pass
        if self.server_proc and self.server_proc.poll() is None:
            try:
                self.server_proc.terminate()
                self.server_proc.wait(timeout=3)
            except Exception:
                try:
                    self.server_proc.kill()
                except Exception:
                    pass

    def _on_close(self):
        self._kill_server()
        self.destroy()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = StudentOfflineBot()
    app.mainloop()
