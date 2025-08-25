import os
import webbrowser
import tkinter as tk
from tkinter import Menu
import keyboard

HOTKEY = "ctrl+alt+space"

MENU_SPEC = [
    ("Oblíbené", [
        ("Google", "https://www.google.com"),
        ("GitHub", "https://github.com"),
        ("Stack Overflow", "https://stackoverflow.com"),
    ]),
    ("Práce", [
        ("Confluence", "https://confluence.example.com"),
        ("Kibana", "https://kibana.example.com"),
        ("Sdílená složka", r"C:\Shared"),
    ]),
    "---",
    ("Mapy", [
        ("Mapy.cz", "https://mapy.cz"),
        ("Google Maps", "https://maps.google.com"),
    ]),
    "---",
    ("Konec", lambda: os._exit(0)),
]

root = tk.Tk()
root.withdraw()

def run_action(action):
    if callable(action):
        try: action(); return
        except Exception: return
    if isinstance(action, str):
        try:
            if action.lower().startswith(("http://", "https://")):
                webbrowser.open(action)
            else:
                os.startfile(action)
        except Exception:
            pass

def build_menu(spec) -> Menu:
    m = Menu(root, tearoff=0)
    for item in spec:
        if item == "---":
            m.add_separator(); continue
        text, action = item
        if isinstance(action, list):
            sub = build_menu(action)
            m.add_cascade(label=text, menu=sub)
        else:
            m.add_command(label=text, command=lambda a=action: run_action(a))
    return m

def show_menu():
    def _popup():
        menu = build_menu(MENU_SPEC)

        ov = tk.Toplevel(root)
        ov.overrideredirect(True)
        ov.attributes("-topmost", True)
        try: ov.attributes("-alpha", 0.01)
        except Exception: pass
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        ov.geometry(f"{sw}x{sh}+0+0")

        ov.lift()  # dej overlay navrch
        ov.focus_force()  # ať overlay dostává klávesy (ESC)

        # --- JEDINÁ společná funkce: požádej o zavření menu ---
        def request_close():
            root.after(0, menu.unpost)

        # Klik mimo -> stejná funkce
        for seq in ("<Button-1>", "<Button-2>", "<Button-3>"):
            ov.bind(seq, lambda e: request_close())

        # ESC -> stejná funkce (navázat přímo na MENU i globálně v Tk; ponecháme i keyboard jako pojistku)
        menu.bind("<Escape>", lambda e: request_close())
        tk_esc = root.bind_all("<Escape>", lambda e: request_close(), add="+")
        esc_hook = keyboard.add_hotkey("esc", request_close, suppress=False)

        try:
            try: x, y = root.winfo_pointerxy()
            except Exception:
                x, y = sw // 2, sh // 2
            menu.tk_popup(x, y)  # vrátí se až po zavření
        finally:
            # úklid – až TEĎ je menu zavřené, tak smažeme overlay & hooky
            try: keyboard.remove_hotkey(esc_hook)
            except Exception: pass
            try: root.unbind_all("<Escape>")
            except Exception: pass
            try: ov.destroy()
            except Exception: pass

    root.after(0, _popup)

keyboard.add_hotkey(HOTKEY, show_menu)

print(f"Hotkey: {HOTKEY} → menu u kurzoru. Esc i klik mimo volají stejnou funkci (menu.unpost). Ukončení Ctrl+C.")
try:
    root.mainloop()
finally:
    keyboard.unhook_all_hotkeys()
