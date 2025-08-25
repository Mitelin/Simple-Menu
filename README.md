# Quick Menu Launcher (Tkinter + YAML + Global Hotkey)

> Čeština • [English](#english)

---

## Rychlé menu (Windows)

Lehká utilita pro **Windows**, která po stisku **globální klávesové zkratky** zobrazí u kurzoru **konfigurovatelné menu**. Strukturu menu upravíte v `menu.yaml`. Položky mohou:
- otevřít **URL** v prohlížeči,
- otevřít **soubor/složku** (Průzkumník),
- spustit **program/příkaz** (s volitelnými argumenty),
- mít libovolně hluboké **podmenu**,
- aplikaci **ukončit**.

Menu zavřete **kliknutím mimo**, klávesou **Esc** nebo **výběrem položky**.

> ⚠️ Zaměřeno na **Windows** (používá `os.startfile` a knihovnu `keyboard`).

### Požadavky
- Python **3.9+** (doporučeno 3.10+)
- Balíčky: `pyyaml`, `keyboard`

~~~bash
pip install pyyaml keyboard
~~~

### Spuštění
~~~bash
python win_menu.py
~~~
- Při prvním spuštění se automaticky vytvoří **`menu.yaml`** s přehledným CZ/EN návodem.
- Výchozí zkratka: **Ctrl+Alt+Space** (lze změnit v `settings.hotkey`).

---

## Konfigurace (`menu.yaml`)

Základní příklad:
~~~yaml
settings:
  hotkey: "ctrl+alt+space"

menu:
  - label: "Google"
    items:
      - label: "Vyhledávání"
        open: "https://www.google.com"

  - label: "Moje složka"
    path: "C:\\Users\\Me\\Documents"

  - label: "Spustit Poznámkový blok"
    cmd: "notepad.exe"
    args: ["C:\\readme.txt"]

  - separator: true

  - label: "Konec"
    action: exit
~~~

### Typy položek
- `items:` … **podmenu** (seznam dalších položek)
- `open:` … **URL**
- `path:` … **cesta** k souboru/složce (otevře asociovanou aplikaci / Průzkumník)
- `cmd:` (+ volitelné `args:`) … **spustí program/příkaz**
- `action: exit` … **ukončí aplikaci**
- `separator: true` … **oddělovač**

> **Vnořování:** `items` může být zanořeno libovolně hluboko.

### Chování & ovládání
- **Globální zkratka:** z `settings.hotkey` (výchozí `ctrl+alt+space`).
- **Zavření:** klik mimo / Esc / výběr položky — všechny cesty volají stejný „close“ proces (nejdřív zavře menu, pak uklidí overlay).
- **Živý reload:** `menu.yaml` se načítá **při každém zobrazení menu** – změny se projeví bez restartu.

### (Volitelné) Vzhled položek – ADVANCED
Tyto volby mění vzhled **jedné konkrétní položky (jeden řádek v menu)**.  
**Nepřenášejí se** automaticky na podmenu/děti. **Nelze** formátovat jen část názvu – styl se použije na **celý** text (výjimka: `underline` umí podtrhnout právě **jeden** znak podle indexu).

Klíče:
- `bold: true/false` – tučně
- `italic: true/false` – kurzíva
- `color/bg: "#RRGGBB"` – barva textu/pozadí položky
- `active_fg/active_bg` – barvy při najetí myší
- `underline: N` – podtrhne **jeden** znak na indexu N (0 = první; -1 = žádný)
- `accelerator: "Ctrl+G"` – textová nápověda vpravo (neváže zkratku)
- `icon: "icons/16x16.png"` – ikona vlevo (PNG/GIF 16×16)
- `disabled: true/false` – vysedlá položka (nejde spustit)

> Pozn.: Tato verze skriptu styly **neaplikuje** – jsou zdokumentované pro budoucí rozšíření (lze doplnit v `build_menu()` přes `entryconfigure`).

### Tipy
- **Spuštění po přihlášení:** dejte zástupce skriptu do  
  `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`
- **Kolize zkratek:** některé zkratky mohou zabírat jiné aplikace. Změňte `settings.hotkey` nebo spusťte skript **mimo IDE** / jako **správce**.

### Známá omezení
- Primárně pro **Windows**.
- `cmd` spouští proces přes `subprocess.Popen`; pokud přímé spuštění selže, skript zkusí `shell=True`.

### Řešení potíží
- **Esc nezavírá menu** → overlay musí mít fokus (ve skriptu je `overlay.lift(); overlay.focus_force()`).
- **Hotkey nereaguje** → konflikt s jiným softwarem; změňte zkratku / spusťte mimo IDE.
- **Příkaz se nespustí** → zkontrolujte cestu; případně upravte `cmd`/`args`.

---

## <a id="english"></a>Quick Menu (Windows)

A lightweight utility for **Windows** that shows a **configurable popup menu** at the mouse cursor when a **global hotkey** is pressed. The menu lives in `menu.yaml`. Items can:
- open **URLs** in your browser,
- open **files/folders** (Explorer),
- **run programs/commands** (optional args),
- have arbitrarily deep **submenus**,
- **exit** the app.

Close the menu by **clicking outside**, pressing **Esc**, or **selecting an item**.

> ⚠️ Windows-focused (uses `os.startfile` and the `keyboard` library).

### Requirements
- Python **3.9+** (3.10+ recommended)
- Packages: `pyyaml`, `keyboard`

~~~bash
pip install pyyaml keyboard
~~~

### Run
~~~bash
python win_menu.py
~~~
- On first run, a bilingual **`menu.yaml`** is generated.
- Default hotkey: **Ctrl+Alt+Space** (change via `settings.hotkey`).

---

## Configuration (`menu.yaml`)

Basic example:
~~~yaml
settings:
  hotkey: "ctrl+alt+space"

menu:
  - label: "Google"
    items:
      - label: "Search"
        open: "https://www.google.com"

  - label: "My folder"
    path: "C:\\Users\\Me\\Documents"

  - label: "Run Notepad"
    cmd: "notepad.exe"
    args: ["C:\\readme.txt"]

  - separator: true

  - label: "Exit"
    action: exit
~~~

### Item types
- `items:` … **submenu** (list of nested items)
- `open:` … **URL**
- `path:` … **file/folder path** (opens associated app / Explorer)
- `cmd:` (+ optional `args:`) … **run a program/command**
- `action: exit` … **quit the app**
- `separator: true` … **visual separator**

> **Nesting:** `items` can be nested to any depth.

### Behavior & controls
- **Global hotkey:** from `settings.hotkey` (default `ctrl+alt+space`).
- **Closing:** outside click / Esc / item selection — all routes trigger the same close flow (menu closes first, overlay is cleaned up afterwards).
- **Live reload:** `menu.yaml` is loaded **every time the menu opens**.

### (Optional) Item styling – ADVANCED
These options style a **single menu item (one row)**.  
They **do not** cascade to submenus/children. You **cannot** style parts of the text — the style applies to the **entire** label (exception: `underline` can underline **one** character by index).

Keys:
- `bold: true/false`
- `italic: true/false`
- `color/bg: "#RRGGBB"`
- `active_fg/active_bg`
- `underline: N` — underline **one** char at index N (0 = first; -1 = none)
- `accelerator: "Ctrl+G"` — right-side hint text (does not bind a hotkey)
- `icon: "icons/16x16.png"` — left icon (PNG/GIF 16×16)
- `disabled: true/false`

> Note: This script version **does not apply** styling; it’s documented for future extension (can be wired via `entryconfigure` in `build_menu()`).

### Tips
- **Run on login:** place a shortcut to the script in  
  `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`
- **Hotkey conflicts:** if another tool captures your combo, change `settings.hotkey` or run outside the IDE / as Administrator.

### Known limitations
- Windows-focused.
- `cmd` uses `subprocess.Popen`; if direct spawn fails, the script falls back to `shell=True`.

### Troubleshooting
- **Esc doesn’t close** → overlay must have focus (`overlay.lift(); overlay.focus_force()` is in code).
- **Hotkey does nothing** → likely conflict; change the hotkey or run outside the IDE.
- **Command won’t start** → verify path; adjust `cmd`/`args` if needed.

---

## Licence / License
**Public domain (The Unlicense).**  
Můžete kopírovat, upravovat, používat i komerčně, bez omezení.  
Software je poskytován „jak stojí a leží“, bez jakýchkoli záruk.

**Public domain (The Unlicense).**  
You may copy, modify, use (including commercially) without restrictions.  
Provided “as is”, without any warranty.

## Credits
Built with Python, Tkinter, PyYAML, and keyboard.
