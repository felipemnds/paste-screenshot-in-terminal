# paste-screenshot-in-terminal

Paste any image from your clipboard directly into a terminal with a single hotkey.

Built for [Claude Code](https://claude.ai/code) users, but works with any terminal.

---

## The problem

Claude Code (and most terminals) accept image paths, not raw images. To share a screenshot you have to:

1. Take a screenshot
2. Find where it was saved
3. Copy the path
4. Paste it manually

This tool cuts all of that down to one keystroke.

---

## How it works

1. Copy any image to your clipboard (print screen, Snipping Tool, browser right-click, anything)
2. Focus your terminal
3. Press **Ctrl+Shift+S**
4. The image path is automatically typed into the terminal

That's it.

---

## Requirements

- Windows 10 or 11
- [AutoHotkey v2](https://www.autohotkey.com/) (free)

---

## Installation

**1. Install AutoHotkey v2**

Download from [autohotkey.com](https://www.autohotkey.com/) and run the installer. Choose **AutoHotkey v2**.

**2. Download this project**

Click **Code → Download ZIP** on this page, then extract it anywhere.

**3. Run the setup**

Double-click `installer/setup.ahk`.

The setup wizard will ask you to:
- Choose a hotkey (default: Ctrl+Shift+S)
- Choose where temporary images are saved
- Optionally start the script automatically with Windows

**4. That's it**

The script runs in the system tray. Next time you have an image in your clipboard, press your hotkey inside a terminal.

---

## Manual setup (skip the wizard)

Edit `config.ini` directly:

```ini
[Settings]
Hotkey=^+s
SaveFolder=C:\Users\YourName\Documents\paste-screenshot-temp
```

Then double-click `src/paste-screenshot.ahk` to start.

---

## Hotkey syntax

| Symbol | Key   |
|--------|-------|
| `^`    | Ctrl  |
| `+`    | Shift |
| `!`    | Alt   |
| `#`    | Win   |

Examples: `^+s` = Ctrl+Shift+S, `^!v` = Ctrl+Alt+V

---

## Temporary files

Images are saved with a timestamp (`screenshot_2025-01-15_14-30-00.png`) and never deleted automatically. You can clear the folder manually whenever you want.

To change the folder, edit `config.ini` or re-run `installer/setup.ahk`.

---

## Troubleshooting

**Hotkey does not work**
- Make sure `src/paste-screenshot.ahk` is running (check system tray)
- Check if another program is using the same hotkey

**"No image found in clipboard"**
- The script only works when there is an image in the clipboard, not a file path or text

**AutoHotkey version error**
- This script requires AutoHotkey v2. If you have v1 installed, download v2 from [autohotkey.com](https://www.autohotkey.com/)

---

## License

MIT
