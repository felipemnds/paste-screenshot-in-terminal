#Requires AutoHotkey v2.0
#SingleInstance Force

; ── Setup Wizard ──────────────────────────────────────────────────────────────
; Runs once to configure paste-screenshot-in-terminal

configFile := A_ScriptDir "\..\config.ini"
scriptSrc  := A_ScriptDir "\..\src\paste-screenshot.ahk"

; Welcome
result := MsgBox(
    "Welcome to paste-screenshot-in-terminal!`n`n"
    . "This tool lets you paste any image from your clipboard directly into any terminal (Claude Code, PowerShell, etc.) with a single hotkey.`n`n"
    . "The setup will:`n"
    . "  1. Choose a hotkey`n"
    . "  2. Choose where to save temporary images`n"
    . "  3. Optionally start the script on Windows startup`n`n"
    . "Click OK to continue.",
    "Setup — paste-screenshot-in-terminal",
    "OKCancel"
)

if (result = "Cancel")
    ExitApp()

; ── Step 1: Choose hotkey ─────────────────────────────────────────────────────
hotkeyChoice := InputBox(
    "Enter your preferred hotkey.`n`nExamples:`n  ^+s  →  Ctrl+Shift+S`n  ^+v  →  Ctrl+Shift+V`n  ^!s  →  Ctrl+Alt+S`n`nLeave blank to use the default: Ctrl+Shift+S",
    "Step 1 of 3 — Choose hotkey",
    "w400 h200",
    "^+s"
)

if (hotkeyChoice.Result = "Cancel")
    ExitApp()

hotkey := Trim(hotkeyChoice.Value)
if (hotkey = "")
    hotkey := "^+s"

; ── Step 2: Choose save folder ────────────────────────────────────────────────
defaultFolder := A_MyDocuments "\paste-screenshot-temp"
folderChoice := InputBox(
    "Where should temporary images be saved?`n`nLeave blank to use the default:`n" defaultFolder,
    "Step 2 of 3 — Save folder",
    "w500 h180",
    defaultFolder
)

if (folderChoice.Result = "Cancel")
    ExitApp()

saveFolder := Trim(folderChoice.Value)
if (saveFolder = "")
    saveFolder := defaultFolder

if (!DirExist(saveFolder))
    DirCreate(saveFolder)

; ── Step 3: Startup ───────────────────────────────────────────────────────────
startupResult := MsgBox(
    "Would you like paste-screenshot-in-terminal to start automatically with Windows?`n`n(Recommended)",
    "Step 3 of 3 — Startup",
    "YesNo"
)

if (startupResult = "Yes") {
    startupLink := A_Startup "\paste-screenshot-in-terminal.lnk"
    FileCreateShortcut(scriptSrc, startupLink)
}

; ── Save config ───────────────────────────────────────────────────────────────
IniWrite(hotkey,     configFile, "Settings", "Hotkey")
IniWrite(saveFolder, configFile, "Settings", "SaveFolder")

; ── Done ──────────────────────────────────────────────────────────────────────
done := MsgBox(
    "Setup complete!`n`n"
    . "Hotkey: " hotkey "`n"
    . "Save folder: " saveFolder "`n`n"
    . "Would you like to start the script now?",
    "Setup complete",
    "YesNo"
)

if (done = "Yes")
    Run(scriptSrc)

ExitApp()
