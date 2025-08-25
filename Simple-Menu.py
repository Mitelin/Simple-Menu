"""
Quick Menu Launcher (Tkinter + YAML + global hotkey)

OVERVIEW
--------
This script shows a native-looking popup menu at the mouse cursor when a global
hotkey is pressed. The menu structure is defined in a user-editable YAML file
(`menu.yaml`). Items can open URLs, open files/folders, run programs with
arguments, or open nested submenus. A special "exit" action quits the app.

The menu can be closed in three ways:
  1) Selecting an item (standard Tk behavior closes the popup).
  2) Clicking anywhere outside the menu (we use a transparent fullscreen
     overlay window to capture "outside" clicks).
  3) Pressing Esc (the overlay is given focus so it will receive Esc).
All closure paths call the same logic: first unpost/close the menu, then
destroy the overlay and remove temporary hooks. This prevents "stuck" states.

FILES
-----
- menu.yaml  : user configuration (auto-created on first run from DEFAULT_YAML)
- this script: run it, keep console open, and use the configured hotkey.

DEPENDENCIES
------------
pip install pyyaml keyboard

WHY AN OVERLAY?
---------------
Tk's popup Menu handles clicks inside itself. To reliably capture *outside*
clicks and the Esc key (even when focus would be ambiguous), we create a
borderless, transparent, full-screen Toplevel window (the "overlay") behind
the menu. We immediately bring it to top and give it focus so it receives
Esc and mouse clicks. When we request closing the menu, we only unpost the
menu; the overlay is destroyed after tk_popup() returns (in a finally block).

YAML SCHEMA (short)
-------------------
settings:
  hotkey: "<global hotkey string>"  # e.g. "ctrl+alt+space"

menu:
  - separator: true
  - label: "Text"
    open: "https://..."
  - label: "Text"
    path: "C:\\Folder\\Or\\File"
  - label: "Text"
    cmd: "program.exe"
    args: ["arg1", "arg2"]
  - label: "Submenu"
    items: [ ... nested items ... ]
  - label: "Exit"
    action: exit

See DEFAULT_YAML below for a full bilingual (CZ+EN) template + advanced notes.
"""

import os, subprocess, webbrowser
import tkinter as tk
from tkinter import Menu
import keyboard
import yaml

CONFIG_FILE = "menu.yaml"
DEFAULT_HOTKEY = "ctrl+alt+space"

# -----------------------------------------------------------------------------
# DEFAULT_YAML
# -----------------------------------------------------------------------------
# If menu.yaml is missing, we write this template for the user to edit.
# (Kept bilingual as you requested; no behavior depends on comments.)
DEFAULT_YAML = r"""# ================================
#  KONFIG: Rychlé menu  (CZ)
#
#  JAK PŘIDAT POLOŽKY (ZÁKLAD):
#  - Otevřít URL v prohlížeči:
#      - label: "Google"
#        open: "https://www.google.com"
#
#  - Otevřít soubor/složku ve Windows:
#      - label: "Moje složka"
#        path: "C:\\Users\\Me\\Documents"
#
#  - Spustit program/příkaz (volitelně s argumenty):
#      - label: "Poznámkový blok"
#        cmd: "notepad.exe"
#        args: ["C:\\readme.txt"]
#
#  - Podmenu (libovolná hloubka):
#      - label: "Google"
#        items:
#          - label: "Záložky"
#            items:
#              - label: "Moje stránka"
#                open: "https://example.com"
#
#  - Oddělovač:
#      - separator: true
#
#  - Ukončit aplikaci:
#   (kompletne zavre program)   
#      - label: "Konec"
#        action: exit
#
#  PRAVIDLA:
#   • Každá položka má buď "items" (podmenu), NEBO jednu akci: open/path/cmd/action, NEBO "separator: true".
#   • "args" je volitelné pole (jen k "cmd").
#   • Vnoření "items" může být libovolně hluboké.
#
#  ADVANCED (VOLITELNÉ VZHLEDY POLOŽEK):
#   • Tyto volby upravují vzhled JEDNÉ položky (jeden řádek). Nepřenáší se na podmenu/děti.
#   • Nelze formátovat jen část názvu – styl se použije na celý text (výjimka: underline jedním znakem).
#   • Klíče: 
#       - bold: true/false        (tučně)
#       - italic: true/false      (kurzíva)
#       - color/bg: "#RRGGBB"     (barva textu/pozadí řádku)
#       - active_fg/active_bg     (barvy při najetí)
#       - underline: N            (podtrhne 1 znak na indexu N; 0 = první; -1 = žádný; „všechny“ nejde)
#       - accelerator: "Ctrl+G"   (jen popisek vpravo, neváže zkratku)
#       - icon: "icons/16x16.png" (ikona vlevo, PNG/GIF 16×16)
#       - disabled: true/false    (vysedlá, nejde spustit)
# ================================
#
# ================================
#  CONFIG: Quick Menu  (EN)
#
#  HOW TO ADD ITEMS (BASIC):
#  - Open a URL in the browser:
#      - label: "Google"
#        open: "https://www.google.com"
#
#  - Open a file/folder in Windows:
#      - label: "My folder"
#        path: "C:\\Users\\Me\\Documents"
#
#  - Run a program/command (optional args):
#      - label: "Notepad"
#        cmd: "notepad.exe"
#        args: ["C:\\readme.txt"]
#
#  - Submenu (any depth):
#      - label: "Google"
#        items:
#          - label: "Bookmarks"
#            items:
#              - label: "My page"
#                open: "https://example.com"
#
#  - Separator:
#      - separator: true
#
#  - Quit the app:
#   (compleatly close the program)
#      - label: "Exit"
#        action: exit
#
#  RULES:
#   • Each entry must have either "items" (submenu), OR exactly one action: open/path/cmd/action, OR "separator: true".
#   • "args" is optional (only with "cmd").
#   • "items" can be nested arbitrarily.
#
#  ADVANCED (OPTIONAL ITEM STYLING):
#   • These options style a SINGLE menu item (one row). They do NOT cascade to submenus/children.
#   • You cannot style parts of the label; the style applies to the whole text (exception: underline one char).
#   • Keys:
#       - bold: true/false
#       - italic: true/false
#       - color/bg: "#RRGGBB"
#       - active_fg/active_bg
#       - underline: N            (underline ONE char at index N; 0 = first; -1 = none)
#       - accelerator: "Ctrl+G"   (right hint text; does not bind a hotkey)
#       - icon: "icons/16x16.png" (left icon, PNG/GIF 16×16)
#       - disabled: true/false
# ================================

settings:
  hotkey: "ctrl+alt+space"

menu:
  - label: "Google"
    items:
      - label: "Záložky / Bookmarks"
        items:
          - label: "Moje stránka / My page"
            open: "https://example.com"
      - label: "Vyhledávání / Search"
        open: "https://www.google.com"

  - label: "Práce / Work"
    items:
      - label: "Confluence"
        open: "https://confluence.example.com"
      - label: "Kibana"
        open: "https://kibana.example.com"
      - label: "Sdílená složka / Shared folder"
        path: "C:\\Shared"

  - separator: true

  - label: "Nástroje / Tools"
    items:
      - label: "Poznámkový blok s readme / Notepad with readme"
        cmd: "notepad.exe"
        args: ["C:\\readme.txt"]

  - separator: true

  - label: "Konec / Exit"
    action: exit

"""

def ensure_config():
    """
    Ensure the YAML config file exists.

    Behavior
    --------
    - If CONFIG_FILE does not exist, write DEFAULT_YAML into it.
    - If it exists, leave it untouched (user edits are preserved).
    """
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            f.write(DEFAULT_YAML)

def load_config():
    """
    Load configuration from YAML.

    Returns
    -------
    (hotkey: str, menu_spec: list)
      - hotkey: global hotkey string (fallback to DEFAULT_HOTKEY if missing)
      - menu_spec: list of menu item dictionaries from YAML (may be empty)

    Notes
    -----
    Uses yaml.safe_load to avoid executing arbitrary YAML tags.
    Any missing sections are replaced with safe defaults.
    """
    ensure_config()
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    settings = data.get("settings", {}) or {}
    menu = data.get("menu", []) or []
    hotkey = settings.get("hotkey") or DEFAULT_HOTKEY
    return hotkey, menu

# -----------------------------------------------------------------------------
# Actions
# -----------------------------------------------------------------------------
def run_action(node):
    """
    Execute an action represented by a menu node.

    Supported keys on `node`:
      - "open": URL → open in default web browser.
      - "path": file or directory path → open via os.startfile (Explorer/Shell).
      - "cmd" : executable/command → spawn process (optionally with "args").
      - "action": special keywords; currently supports:
          * "exit" → terminate the process immediately.

    Error handling
    --------------
    - All branches are wrapped in try/except to avoid crashing the UI.
    - For "cmd", we first try Popen without shell (safer). If that fails
      (e.g., command found only via shell PATH rules), we fall back to
      Popen(shell=True) with a single command line string.
    """
    if "open" in node:
        webbrowser.open(str(node["open"]))
        return

    if "path" in node:
        path = str(node["path"])
        try:
            os.startfile(path)  # Windows: opens file/folder in associated app/Explorer
        except Exception:
            pass
        return

    if "cmd" in node:
        cmd = str(node["cmd"])
        args = node.get("args") or []
        if not isinstance(args, list):
            args = [str(args)]
        try:
            subprocess.Popen([cmd, *map(str, args)], shell=False)
        except Exception:
            # Fallback: more permissive; allows shell builtins etc.
            try:
                subprocess.Popen(cmd if not args else " ".join([cmd, *map(str, args)]), shell=True)
            except Exception:
                pass
        return

    if node.get("action") == "exit":
        os._exit(0)  # immediate process termination; no cleanup callbacks are guaranteed

# -----------------------------------------------------------------------------
# Validation + Menu construction
# -----------------------------------------------------------------------------
def validate_node(node, path="root"):
    """
    Validate a single menu node recursively.

    Valid forms:
      1) Separator item:
           {"separator": true}
      2) Submenu:
           {"label": "...", "items": [ ...child items... ]}
      3) Action item (exactly one of the following keys may be present,
         but we allow any single one to pass in practice):
           {"label": "...", "open": URL}
           {"label": "...", "path": FILE_OR_DIR}
           {"label": "...", "cmd": EXE, "args": [...]}
           {"label": "...", "action": "exit"}

    Parameters
    ----------
    node : dict
        The YAML-parsed node to validate.
    path : str
        Human-readable path used in error messages (e.g., "menu[3] > Tools[2]").

    Returns
    -------
    (ok: bool, err: Optional[str])
        ok=True if valid; otherwise ok=False and err describes the problem.
    """
    # Separator
    if node.get("separator", False):
        return True, None

    # Submenu
    if "items" in node:
        if not isinstance(node.get("items"), list):
            return False, f'"items" must be a list ({path})'
        for i, child in enumerate(node["items"], 1):
            ok, err = validate_node(child, f"{path} > {node.get('label','?')}[{i}]")
            if not ok:
                return False, err
        return True, None

    # Single-action item
    if any(k in node for k in ("open", "path", "cmd", "action")):
        return True, None

    return False, f'Each item must have "items" OR one action (open/path/cmd/action) OR "separator: true" ({path})'

def build_menu(root, spec) -> Menu:
    """
    Recursively build a Tkinter Menu from a list of node dicts.

    Implementation notes
    --------------------
    - Uses recursion for nested submenus (`items` key).
    - For action items, we capture the current `item` value into a default
      argument of the lambda (`lambda node=item: ...`) to avoid late-binding
      closure issues where all commands would see the last loop item.
    - We do *not* apply advanced styling keys here (bold/color/etc.). Those
      could be added later via `entryconfigure` if you decide to support them.

    Returns
    -------
    tk.Menu
        A fully constructed (but not yet posted) menu instance.
    """
    m = Menu(root, tearoff=0)
    for item in spec:
        if item.get("separator"):
            m.add_separator()
            continue

        label = item.get("label", "")

        if "items" in item:  # submenu
            sub = build_menu(root, item["items"])
            m.add_cascade(label=label, menu=sub)
        else:
            # action item
            m.add_command(label=label, command=lambda node=item: (close_menu(), run_action(node)))
    return m

# -----------------------------------------------------------------------------
# UI & interaction (overlay + Esc + global hotkey)
# -----------------------------------------------------------------------------
root = tk.Tk()
root.withdraw()  # hide the root window; we only use popup menus and a temporary overlay

# Global mutable state (only for the active popup cycle)
state = {"overlay": None, "menu": None, "esc_hook": None}

def request_close_menu():
    """
    Ask Tk to close the currently posted popup menu.

    Rationale
    ---------
    `tk.Menu.tk_popup(...)` installs a local grab and does not return until the
    menu is dismissed. We *must not* destroy the overlay before the popup menu
    finishes, or we risk leaving the menu posted without a way to capture clicks.

    Therefore: this function only unposts the menu (asynchronously via after(0)),
    and actual overlay destruction happens in `close_menu()` which is called
    after `tk_popup()` returns (inside a `finally` block).
    """
    if state["menu"] is not None:
        root.after(0, state["menu"].unpost)

def close_menu(_e=None):
    """
    Final cleanup after a popup cycle ends.

    Order matters:
      1) Remove the temporary global Esc hotkey (if any).
      2) Destroy the overlay (the transparent Toplevel).
      3) Clear references in `state` so next cycle starts fresh.
    """
    # 1) Unhook temporary Esc
    if state["esc_hook"] is not None:
        try:
            keyboard.remove_hotkey(state["esc_hook"])
        except Exception:
            pass
        state["esc_hook"] = None

    # 2) Destroy overlay window (if it exists)
    if state["overlay"] is not None:
        try:
            state["overlay"].destroy()
        except Exception:
            pass
        state["overlay"] = None

    # 3) Drop the menu reference
    state["menu"] = None

def show_menu():
    """
    Schedule showing the popup menu at the current mouse cursor position.

    We use `root.after(0, _popup)` to ensure the UI work runs on Tk's event loop
    and not directly in the keyboard hotkey callback thread.
    """
    def _popup():
        """
        The actual popup routine:
          - Load YAML (so edits are picked up without restarting).
          - Validate the spec and build a fresh menu.
          - Create a transparent full-screen overlay that captures clicks and Esc.
          - Post the menu at the mouse cursor.
          - In a finally block, always clean up overlay + temporary Esc hook.
        """
        # Load config at each open so users can edit YAML while the app runs
        hotkey, menu_spec = load_config()

        # Lightweight validation to catch common mistakes early
        for i, node in enumerate(menu_spec, 1):
            ok, err = validate_node(node, f"menu[{i}]")
            if not ok:
                from tkinter import messagebox
                messagebox.showerror("menu.yaml error", err)
                return

        # Build a fresh menu for this popup cycle
        state["menu"] = build_menu(root, menu_spec)

        # Create the overlay (transparent, topmost, full-screen)
        ov = tk.Toplevel(root)
        state["overlay"] = ov
        ov.overrideredirect(True)  # no border/title
        ov.attributes("-topmost", True)
        try:
            ov.attributes("-alpha", 0.01)  # almost invisible but focusable
        except Exception:
            pass
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        ov.geometry(f"{sw}x{sh}+0+0")

        # IMPORTANT: bring overlay to front and give it focus so it captures Esc
        ov.lift()
        ov.focus_force()

        # Outside click OR Esc → request to close the menu (same function)
        for seq in ("<Button-1>", "<Button-2>", "<Button-3>", "<Escape>"):
            ov.bind(seq, lambda e: request_close_menu())

        # Extra safety: a temporary global "Esc" hotkey as a fallback
        state["esc_hook"] = keyboard.add_hotkey("esc", request_close_menu, suppress=False)

        # Post the popup at the current mouse cursor (tk_popup blocks until closed)
        try:
            try:
                x, y = root.winfo_pointerxy()
            except Exception:
                x, y = sw // 2, sh // 2
            state["menu"].tk_popup(x, y)
        finally:
            # Once the popup returns, the menu is dismissed → now we can clean up.
            close_menu()

    # Run the popup logic on the Tk event loop
    root.after(0, _popup)

# Register the global hotkey (from YAML, with fallback)
hotkey, _ = load_config()
keyboard.add_hotkey(hotkey or DEFAULT_HOTKEY, show_menu)

print(f"Hotkey: {hotkey or DEFAULT_HOTKEY} – YAML: {os.path.abspath(CONFIG_FILE)}")

try:
    # Enter Tk's event loop. Use Ctrl+C in console to quit.
    root.mainloop()
finally:
    # Make sure no global hotkeys remain if the app exits abnormally.
    keyboard.unhook_all_hotkeys()
