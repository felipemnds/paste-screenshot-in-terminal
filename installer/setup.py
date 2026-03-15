"""
paste-screenshot-in-terminal - Setup Wizard
VS Code-inspired design language
"""

import os
import subprocess
import winreg
import configparser
import threading
from pathlib import Path
from tkinter import filedialog
import customtkinter as ctk
import keyboard

# ── Design tokens (VS Code) ──────────────────────────────────────────────────
BG          = "#1e1e1e"   # editor background
BG_PANEL    = "#252526"   # sidebar / panel
BG_INPUT    = "#3c3c3c"   # input fields
BG_HOVER    = "#2a2d2e"   # hover state
BG_SELECTED = "#094771"   # selected / active
BORDER      = "#3e3e42"   # default border
BORDER_FOCUS= "#0078d4"   # focused border
TEXT        = "#cccccc"   # primary text
TEXT_MUTED  = "#9d9d9d"   # secondary text
TEXT_DIM    = "#6a6a6a"   # disabled / hint
ACCENT      = "#0078d4"   # primary blue
ACCENT_HVR  = "#1177bb"   # button hover
GREEN       = "#4ec9b0"   # success (VS Code teal)
RED         = "#f44747"   # error
YELLOW      = "#cca700"   # warning
FONT_UI     = "Segoe UI"
FONT_MONO   = "Consolas"

W, H        = 640, 420

BASE_DIR    = Path(__file__).parent.parent
CONFIG_FILE = BASE_DIR / "config.ini"
SCRIPT_MAIN = BASE_DIR / "src" / "paste-screenshot.ahk"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ── Global state ─────────────────────────────────────────────────────────────
state = {
    "key_combo":   "^+s",
    "save_folder": str(Path.home() / "Documents" / "paste-screenshot-temp"),
    "ahk_exe":     "",
}

STEPS = ["AutoHotkey", "Hotkey", "Save folder", "Test"]

# ── Helpers ──────────────────────────────────────────────────────────────────
def find_ahk_exe():
    candidates = [
        r"C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe",
        r"C:\Program Files\AutoHotkey\v2\AutoHotkey32.exe",
        r"C:\Program Files\AutoHotkey\AutoHotkey.exe",
        r"C:\Program Files (x86)\AutoHotkey\AutoHotkey.exe",
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\AutoHotkey")
        d, _ = winreg.QueryValueEx(key, "InstallDir")
        for sub in [r"v2\AutoHotkey64.exe", "AutoHotkey.exe"]:
            full = os.path.join(d, sub)
            if os.path.exists(full):
                return full
    except Exception:
        pass
    return ""


def format_key_display(combo: str) -> str:
    mod_map = {"^": "Ctrl", "+": "Shift", "!": "Alt", "#": "Win"}
    parts = []
    i = 0
    while i < len(combo):
        c = combo[i]
        if c in mod_map:
            parts.append(mod_map[c])
        else:
            parts.append(combo[i:])  # rest is the key name
            break
        i += 1
    return " + ".join(parts)


def hotkey_to_ahk(raw: str) -> str:
    parts = [p.strip().lower() for p in raw.split("+")]
    mods, keys = "", []
    for p in parts:
        if p in ("ctrl", "control"):             mods += "^"
        elif p == "shift":                        mods += "+"
        elif p == "alt":                          mods += "!"
        elif p in ("windows", "win",
                   "left windows", "right windows"): mods += "#"
        else:                                     keys.append(p)
    key = keys[-1] if keys else ""
    return mods + (key.upper() if len(key) == 1 else key.capitalize())


# ── App ───────────────────────────────────────────────────────────────────────
class WizardApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("paste-screenshot-in-terminal - Setup")
        self.geometry(f"{W}x{H}")
        self.resizable(False, False)
        self.configure(fg_color=BG)
        self._center()
        state["ahk_exe"] = find_ahk_exe()
        self.current_page = None
        self._build_shell()
        self.show_page(0)

    def _center(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - W) // 2
        y = (self.winfo_screenheight() - H) // 2
        self.geometry(f"{W}x{H}+{x}+{y}")

    def _build_shell(self):
        # ── Left sidebar (activity bar style)
        self.sidebar = ctk.CTkFrame(self, fg_color=BG_PANEL, corner_radius=0, width=160)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        ctk.CTkLabel(self.sidebar, text="SETUP",
                     font=(FONT_UI, 9, "bold"), text_color=TEXT_DIM).pack(anchor="w", padx=16, pady=(18, 10))

        self.step_btns = []
        for i, label in enumerate(STEPS):
            row = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=36)
            row.pack(fill="x")
            row.pack_propagate(False)

            num = ctk.CTkLabel(row, text=str(i + 1), width=22, height=22,
                               font=(FONT_MONO, 10, "bold"),
                               text_color=BG_PANEL,
                               fg_color=TEXT_DIM,
                               corner_radius=11)
            num.place(x=14, rely=0.5, anchor="w")

            lbl = ctk.CTkLabel(row, text=label,
                               font=(FONT_UI, 12), text_color=TEXT_DIM)
            lbl.place(x=46, rely=0.5, anchor="w")

            self.step_btns.append({"row": row, "num": num, "lbl": lbl})

        # ── Main content area
        self.content = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        self.content.pack(side="left", fill="both", expand=True)


    def show_page(self, index: int):
        # Rebuild content
        if self.current_page:
            self.current_page.destroy()

        # Highlight active step
        for i, btn in enumerate(self.step_btns):
            if i < index:
                btn["num"].configure(fg_color=GREEN,  text_color=BG)
                btn["num"].configure(text="✓")
                btn["lbl"].configure(text_color=TEXT_MUTED)
                btn["row"].configure(fg_color="transparent")
            elif i == index:
                btn["num"].configure(fg_color=ACCENT, text_color="white")
                btn["num"].configure(text=str(i + 1))
                btn["lbl"].configure(text_color=TEXT, font=(FONT_UI, 12, "bold"))
                btn["row"].configure(fg_color=BG_HOVER)
            else:
                btn["num"].configure(fg_color=TEXT_DIM, text_color=BG_PANEL)
                btn["num"].configure(text=str(i + 1))
                btn["lbl"].configure(text_color=TEXT_DIM, font=(FONT_UI, 12))
                btn["row"].configure(fg_color="transparent")

        pages = [Page1, Page2, Page3, Page4]
        self.current_page = pages[index](self.content, self, index)
        self.current_page.pack(fill="both", expand=True)


# ── Shared layout ─────────────────────────────────────────────────────────────
class BasePage(ctk.CTkFrame):
    def __init__(self, parent, app: WizardApp, index: int):
        super().__init__(parent, fg_color=BG, corner_radius=0)
        self.app   = app
        self.index = index
        self._build_title()
        self.body = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        self.body.pack(fill="both", expand=True, padx=28, pady=(0, 0))
        self.nav = ctk.CTkFrame(self, fg_color=BG_PANEL, corner_radius=0, height=52)
        self.nav.pack(fill="x", side="bottom")
        self.nav.pack_propagate(False)

    def _build_title(self):
        title_bar = ctk.CTkFrame(self, fg_color=BG, corner_radius=0, height=56)
        title_bar.pack(fill="x")
        title_bar.pack_propagate(False)
        ctk.CTkLabel(title_bar, text=STEPS[self.index],
                     font=(FONT_UI, 16, "bold"), text_color=TEXT).place(x=28, y=14)
        ctk.CTkFrame(title_bar, fg_color=BORDER, height=1).place(x=0, rely=1.0, anchor="sw", relwidth=1)

    def add_nav(self, back_fn=None, next_fn=None, next_label="Next"):
        if back_fn:
            ctk.CTkButton(self.nav, text="Back", width=80, height=28,
                          fg_color="transparent", hover_color=BG_HOVER,
                          border_width=1, border_color=BORDER,
                          text_color=TEXT_MUTED, font=(FONT_UI, 12),
                          corner_radius=3,
                          command=back_fn).place(x=12, rely=0.5, anchor="w")
        if next_fn:
            ctk.CTkButton(self.nav, text=next_label, width=100, height=28,
                          fg_color=ACCENT, hover_color=ACCENT_HVR,
                          text_color="white", font=(FONT_UI, 12, "bold"),
                          corner_radius=3,
                          command=next_fn).place(relx=1, x=-12, rely=0.5, anchor="e")

    def label(self, text, muted=False, mono=False, size=12, **kwargs):
        font = (FONT_MONO if mono else FONT_UI, size)
        color = TEXT_MUTED if muted else TEXT
        return ctk.CTkLabel(self.body, text=text, font=font,
                            text_color=color, justify="left", **kwargs)

    def vscode_input(self, width=None, placeholder="", value=""):
        e = ctk.CTkEntry(self.body,
                         width=width or 380, height=26,
                         fg_color=BG_INPUT, border_color=BORDER,
                         border_width=1, corner_radius=2,
                         font=(FONT_MONO, 12), text_color=TEXT,
                         placeholder_text=placeholder,
                         placeholder_text_color=TEXT_DIM)
        if value:
            e.insert(0, value)
        return e

    def vscode_btn(self, parent, text, command, primary=False, width=100, height=26):
        return ctk.CTkButton(parent, text=text, width=width, height=height,
                             fg_color=ACCENT if primary else "transparent",
                             hover_color=ACCENT_HVR if primary else BG_HOVER,
                             border_width=0 if primary else 1,
                             border_color=BORDER,
                             text_color="white" if primary else TEXT_MUTED,
                             font=(FONT_UI, 12, "bold") if primary else (FONT_UI, 12),
                             corner_radius=3,
                             command=command)


# ── Page 1: AutoHotkey check ──────────────────────────────────────────────────
class Page1(BasePage):
    def __init__(self, parent, app, index):
        super().__init__(parent, app, index)

        self.label("AutoHotkey v2 is required to run the paste shortcut.",
                   muted=True).pack(anchor="w", pady=(16, 20))

        # Status card
        self.card = ctk.CTkFrame(self.body, fg_color=BG_PANEL,
                                 border_color=BORDER, border_width=1,
                                 corner_radius=3)
        self.card.pack(fill="x", pady=(0, 14))

        self.status_lbl = ctk.CTkLabel(self.card, text="",
                                       font=(FONT_UI, 12), justify="left")
        self.status_lbl.pack(anchor="w", padx=14, pady=12)

        # Action row
        self.action_row = ctk.CTkFrame(self.body, fg_color="transparent")
        self.action_row.pack(anchor="w")

        self._refresh()
        self.add_nav(next_fn=self._next if state["ahk_exe"] else None)

    def _refresh(self):
        for w in self.action_row.winfo_children():
            w.destroy()

        if state["ahk_exe"]:
            self.status_lbl.configure(
                text=f"  ✓  Found at: {state['ahk_exe']}",
                text_color=GREEN)
            self.card.configure(border_color=GREEN)
        else:
            self.status_lbl.configure(
                text="  ✗  Not found. Please install AutoHotkey v2 to continue.",
                text_color=RED)
            self.card.configure(border_color=RED)
            self.vscode_btn(self.action_row, "Download AutoHotkey v2",
                            command=lambda: os.startfile("https://www.autohotkey.com/download/ahk-v2.exe"),
                            primary=True, width=190).pack(side="left", padx=(0, 8))
            self.vscode_btn(self.action_row, "Check again",
                            command=self._recheck, width=110).pack(side="left")

    def _recheck(self):
        state["ahk_exe"] = find_ahk_exe()
        self._refresh()
        if state["ahk_exe"]:
            for w in self.nav.winfo_children():
                w.destroy()
            self.add_nav(next_fn=self._next)

    def _next(self):
        self.app.show_page(1)


# ── Page 2: Hotkey recorder ───────────────────────────────────────────────────
class Page2(BasePage):
    def __init__(self, parent, app, index):
        super().__init__(parent, app, index)

        self.label("Press the key combination you want to use as your shortcut.",
                   muted=True).pack(anchor="w", pady=(16, 16))

        # Badge row
        badge_row = ctk.CTkFrame(self.body, fg_color="transparent")
        badge_row.pack(anchor="w", fill="x", pady=(0, 16))

        self.badge = ctk.CTkLabel(badge_row,
                                  text=format_key_display(state["key_combo"]),
                                  font=(FONT_MONO, 18, "bold"),
                                  text_color=TEXT,
                                  fg_color=BG_PANEL,
                                  corner_radius=3,
                                  width=300, height=48)
        self.badge.pack(side="left")

        # Record button
        self.rec_btn = ctk.CTkButton(badge_row,
                                     text="Record",
                                     width=90, height=48,
                                     fg_color=BG_INPUT,
                                     hover_color=BG_HOVER,
                                     border_width=1, border_color=BORDER,
                                     text_color=TEXT_MUTED,
                                     font=(FONT_UI, 12),
                                     corner_radius=3,
                                     command=self._start)
        self.rec_btn.pack(side="left", padx=(10, 0))

        self.hint = ctk.CTkLabel(self.body, text="Default: Ctrl+Shift+S",
                                 font=(FONT_UI, 11), text_color=TEXT_DIM)
        self.hint.pack(anchor="w")

        self.add_nav(back_fn=lambda: app.show_page(0),
                     next_fn=lambda: app.show_page(2))

    def _start(self):
        self._hook        = None
        self._held_mods   = set()
        self._last_combo  = ""
        self.rec_btn.configure(text="Listening…", fg_color=BG_SELECTED,
                               text_color=TEXT, border_color=ACCENT)
        self.badge.configure(text="…", text_color=TEXT_DIM)
        self.hint.configure(text="Press your shortcut now…", text_color=YELLOW)
        self._hook = keyboard.hook(self._on_key_event, suppress=False)

    MODS = {"ctrl", "shift", "alt", "windows", "left ctrl", "right ctrl",
            "left shift", "right shift", "left alt", "right alt",
            "left windows", "right windows"}

    def _on_key_event(self, event):
        name = event.name.lower() if event.name else ""

        if event.event_type == keyboard.KEY_DOWN:
            if name in self.MODS:
                self._held_mods.add(name)
                # Show live modifier state
                self.after(0, self._update_live)
            else:
                # Non-modifier pressed - finalize
                mods_str = "+".join(sorted(self._held_mods)) + (f"+{event.name}" if self._held_mods else event.name)
                ahk = hotkey_to_ahk(mods_str)
                state["key_combo"] = ahk
                self.after(0, self._done, mods_str)

        elif event.event_type == keyboard.KEY_UP:
            self._held_mods.discard(name)

    def _update_live(self):
        mod_map = {"ctrl": "Ctrl", "left ctrl": "Ctrl", "right ctrl": "Ctrl",
                   "shift": "Shift", "left shift": "Shift", "right shift": "Shift",
                   "alt": "Alt", "left alt": "Alt", "right alt": "Alt",
                   "windows": "Win", "left windows": "Win", "right windows": "Win"}
        labels = []
        seen   = set()
        for m in ("ctrl", "shift", "alt", "windows"):
            variants = [k for k in self._held_mods if m in k]
            if variants and m not in seen:
                labels.append(mod_map[m])
                seen.add(m)
        self.badge.configure(text=" + ".join(labels) + (" + …" if labels else "…"),
                             text_color=YELLOW)

    def _done(self, raw: str):
        keyboard.unhook(self._hook)
        self.badge.configure(text=format_key_display(state["key_combo"]),
                             text_color=TEXT)
        self.rec_btn.configure(text="Record again", fg_color=BG_INPUT,
                               text_color=TEXT_MUTED, border_color=BORDER)
        self.hint.configure(
            text=f"Captured: {raw}  →  {state['key_combo']}",
            text_color=GREEN)


# ── Page 3: Folder picker ─────────────────────────────────────────────────────
class Page3(BasePage):
    def __init__(self, parent, app, index):
        super().__init__(parent, app, index)

        self.label("Images are saved here temporarily each time you use the hotkey.",
                   muted=True).pack(anchor="w", pady=(16, 14))

        row = ctk.CTkFrame(self.body, fg_color="transparent")
        row.pack(anchor="w", fill="x")

        self.folder_var = ctk.StringVar(value=state["save_folder"])
        entry = ctk.CTkEntry(row,
                             textvariable=self.folder_var,
                             width=340, height=26,
                             fg_color=BG_INPUT,
                             border_color=BORDER, border_width=1,
                             corner_radius=2,
                             font=(FONT_MONO, 11), text_color=TEXT)
        entry.pack(side="left")

        self.vscode_btn(row, "Browse…", command=self._browse,
                        width=80).pack(side="left", padx=(8, 0))

        self.label("You can clear this folder anytime - files are never deleted automatically.",
                   muted=True, size=11).pack(anchor="w", pady=(10, 0))

        self.add_nav(back_fn=lambda: app.show_page(1),
                     next_fn=self._next)

    def _browse(self):
        chosen = filedialog.askdirectory(
            initialdir=self.folder_var.get(),
            title="Choose folder for temporary images")
        if chosen:
            self.folder_var.set(chosen.replace("/", "\\"))

    def _next(self):
        state["save_folder"] = self.folder_var.get()
        self._save_config()
        self._launch_script()
        self.app.show_page(3)

    def _save_config(self):
        cfg = configparser.ConfigParser()
        cfg["Settings"] = {
            "Hotkey":     state["key_combo"],
            "SaveFolder": state["save_folder"],
        }
        os.makedirs(state["save_folder"], exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            cfg.write(f)

    def _launch_script(self):
        ahk = state["ahk_exe"]
        if ahk and SCRIPT_MAIN.exists():
            subprocess.Popen([ahk, str(SCRIPT_MAIN)],
                             creationflags=subprocess.DETACHED_PROCESS)


# ── Page 4: Test ──────────────────────────────────────────────────────────────
class Page4(BasePage):
    def __init__(self, parent, app, index):
        super().__init__(parent, app, index)

        hotkey = format_key_display(state["key_combo"])

        # Instructions list
        steps_text = (
            f"1.  Press  Win + Shift + S  to capture any area of your screen\n"
            f"2.  Return here and press  {hotkey}  in the field below\n"
            f"3.  The image path should appear automatically"
        )
        self.label(steps_text, muted=True).pack(anchor="w", pady=(16, 14))

        # Separator
        ctk.CTkFrame(self.body, fg_color=BORDER, height=1).pack(fill="x", pady=(0, 14))

        # Test input
        self.label("Paste target:", muted=True, size=11).pack(anchor="w", pady=(0, 4))
        self.test_var = ctk.StringVar()
        self.test_entry = ctk.CTkEntry(self.body,
                                       textvariable=self.test_var,
                                       width=420, height=28,
                                       fg_color=BG_INPUT,
                                       border_color=BORDER, border_width=1,
                                       corner_radius=2,
                                       font=(FONT_MONO, 11), text_color=TEXT,
                                       placeholder_text=f"click here, then press {hotkey}",
                                       placeholder_text_color=TEXT_DIM)
        self.test_entry.pack(anchor="w")

        self.status = ctk.CTkLabel(self.body, text="",
                                   font=(FONT_UI, 11), text_color=TEXT_DIM)
        self.status.pack(anchor="w", pady=(8, 0))

        self.test_var.trace_add("write", self._check)

        self.add_nav(back_fn=lambda: app.show_page(2),
                     next_fn=self._finish, next_label="Finish")

    def _check(self, *_):
        val = self.test_var.get().strip()
        if os.path.isfile(val) and val.lower().endswith(
                (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp")):
            self.status.configure(
                text="✓  Image path detected - everything is working correctly.",
                text_color=GREEN)
            self.test_entry.configure(border_color=GREEN)
        elif len(val) > 3:
            self.status.configure(text="Waiting for a valid image path…",
                                  text_color=TEXT_DIM)

    def _finish(self):
        StartupDialog(self.app)


# ── Startup dialog ────────────────────────────────────────────────────────────
class StartupDialog(ctk.CTkToplevel):
    def __init__(self, app: WizardApp):
        super().__init__(app)
        self.app = app
        self.title("Setup complete")
        self.geometry("360x180")
        self.resizable(False, False)
        self.configure(fg_color=BG_PANEL)
        self.grab_set()
        x = app.winfo_x() + (W - 360) // 2
        y = app.winfo_y() + (H - 180) // 2
        self.geometry(f"360x180+{x}+{y}")

        ctk.CTkLabel(self, text="Setup complete",
                     font=(FONT_UI, 14, "bold"), text_color=TEXT).pack(anchor="w", padx=20, pady=(20, 6))
        ctk.CTkLabel(self,
                     text="The script is running in your system tray.\nStart automatically with Windows?",
                     font=(FONT_UI, 12), text_color=TEXT_MUTED,
                     justify="left").pack(anchor="w", padx=20, pady=(0, 20))

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(anchor="e", padx=20)

        ctk.CTkButton(row, text="No thanks", width=90, height=28,
                      fg_color="transparent", hover_color=BG_HOVER,
                      border_width=1, border_color=BORDER,
                      text_color=TEXT_MUTED, font=(FONT_UI, 12),
                      corner_radius=3,
                      command=app.destroy).pack(side="left", padx=(0, 8))

        ctk.CTkButton(row, text="Add to startup", width=120, height=28,
                      fg_color=ACCENT, hover_color=ACCENT_HVR,
                      text_color="white", font=(FONT_UI, 12, "bold"),
                      corner_radius=3,
                      command=self._add_startup).pack(side="left")

    def _add_startup(self):
        startup  = os.path.join(os.environ["APPDATA"],
                                r"Microsoft\Windows\Start Menu\Programs\Startup")
        lnk_path = os.path.join(startup, "paste-screenshot-in-terminal.lnk")
        ahk      = state["ahk_exe"]
        script   = str(SCRIPT_MAIN)
        ps = (
            f'$ws = New-Object -ComObject WScript.Shell; '
            f'$s = $ws.CreateShortcut("{lnk_path}"); '
            f'$s.TargetPath = "{ahk}"; '
            f'$s.Arguments = \'"{script}"\'; '
            f'$s.Save()'
        )
        subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                       capture_output=True)
        self.app.destroy()


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = WizardApp()
    app.mainloop()
