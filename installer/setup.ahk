#Requires AutoHotkey v2.0
#SingleInstance Force

; ════════════════════════════════════════════════════════════
;  paste-screenshot-in-terminal — Setup Wizard
; ════════════════════════════════════════════════════════════

global gKeyCombo    := "^+s"
global gSaveFolder  := A_MyDocuments "\paste-screenshot-temp"
global gConfigFile  := A_ScriptDir "\..\config.ini"
global gScriptMain  := A_ScriptDir "\..\src\paste-screenshot.ahk"
global gAhkExe      := FindAHKExe()
global gKeyBadge    := ""
global gCaptureBox  := ""

ShowPage1()

; ══════════════════════════════════════════════════════════════
;  PAGE 1 — Welcome + AutoHotkey check
; ══════════════════════════════════════════════════════════════
ShowPage1() {
    global gAhkExe

    g := Gui("+AlwaysOnTop -Resize", "Setup — paste-screenshot-in-terminal")
    g.SetFont("s10", "Segoe UI")
    g.BackColor := "FFFFFF"
    g.MarginX := 0
    g.MarginY := 0

    ; ── Header bar
    hdr := g.Add("Text", "x0 y0 w500 h70 +0x200 Background1a1a2e")
    g.SetFont("s14 w700 cWhite", "Segoe UI")
    g.Add("Text", "x24 y18 w460 BackgroundTrans", "paste-screenshot-in-terminal")
    g.SetFont("s9 w400 cCCCCCC", "Segoe UI")
    g.Add("Text", "x24 y44 w460 BackgroundTrans", "Paste clipboard images into any terminal as a file path")

    ; ── Body
    g.SetFont("s10 w600 c1a1a2e", "Segoe UI")
    g.Add("Text", "x24 y90", "Step 1 of 4 — AutoHotkey")

    g.SetFont("s10 w400 c333333", "Segoe UI")
    g.Add("Text", "x24 y115 w452", "This tool requires AutoHotkey v2 to run the paste script.")

    ; Status indicator
    if (gAhkExe != "") {
        g.SetFont("s10 w600 c1e7e34", "Segoe UI")
        g.Add("Text", "x24 y148", "✔  AutoHotkey v2 is installed and ready.")
        g.SetFont("s10 w400 c333333", "Segoe UI")
        g.Add("Text", "x24 y173 w452", "Click Next to continue the setup.")

        btnNext := g.Add("Button", "x390 y230 w86 h32", "Next  →")
        btnNext.SetFont("s10 w600")
        btnNext.OnEvent("Click", (*) => (g.Destroy(), ShowPage2()))
    } else {
        g.SetFont("s10 w600 cCC2200", "Segoe UI")
        g.Add("Text", "x24 y148", "✖  AutoHotkey v2 is not installed.")
        g.SetFont("s10 w400 c333333", "Segoe UI")
        g.Add("Text", "x24 y173 w452", "Please download and install AutoHotkey v2, then click Check Again.")

        btnDl := g.Add("Button", "x24 y225 w190 h32", "⬇  Download AutoHotkey v2")
        btnDl.SetFont("s10 w600")
        btnDl.OnEvent("Click", (*) => Run("https://www.autohotkey.com/download/ahk-v2.exe"))

        btnCheck := g.Add("Button", "x224 y225 w130 h32", "↺  Check Again")
        btnCheck.SetFont("s10")
        btnCheck.OnEvent("Click", (*) => (g.Destroy(), gAhkExe := FindAHKExe(), ShowPage1()))

        btnNext := g.Add("Button", "x390 y225 w86 h32", "Next  →")
        btnNext.SetFont("s10 w600")
        btnNext.Enabled := false
    }

    g.Show("w500 h275")
}

; ══════════════════════════════════════════════════════════════
;  PAGE 2 — Hotkey recorder
; ══════════════════════════════════════════════════════════════
ShowPage2() {
    global gKeyCombo

    g := Gui("+AlwaysOnTop -Resize", "Setup — paste-screenshot-in-terminal")
    g.SetFont("s10", "Segoe UI")
    g.BackColor := "FFFFFF"
    g.MarginX := 0
    g.MarginY := 0

    ; ── Header
    g.Add("Text", "x0 y0 w500 h70 +0x200 Background1a1a2e")
    g.SetFont("s14 w700 cWhite", "Segoe UI")
    g.Add("Text", "x24 y18 w460 BackgroundTrans", "paste-screenshot-in-terminal")
    g.SetFont("s9 w400 cCCCCCC", "Segoe UI")
    g.Add("Text", "x24 y44 w460 BackgroundTrans", "Paste clipboard images into any terminal as a file path")

    ; ── Body
    g.SetFont("s10 w600 c1a1a2e", "Segoe UI")
    g.Add("Text", "x24 y90", "Step 2 of 4 — Choose your hotkey")
    g.SetFont("s10 w400 c333333", "Segoe UI")
    g.Add("Text", "x24 y115 w452", "Click the field below and press the key combination you want to use.")

    ; Key display badge
    gKeyBadge := g.Add("Text", "x24 y148 w452 h38 +0x200 +Border BackgroundF0F0F0")
    gKeyBadge.SetFont("s13 w700 c1a1a2e", "Consolas")
    gKeyBadge.Text := FormatKeyDisplay(gKeyCombo)

    g.SetFont("s9 c666666", "Segoe UI")
    g.Add("Text", "x24 y194 w452", "Click here and press your shortcut:")
    gCaptureBox := g.Add("Edit", "x24 y212 w452 h28 -Multi")
    gCaptureBox.SetFont("s9 c999999", "Segoe UI")
    gCaptureBox.Value := "← click and press your shortcut"

    OnMessage(0x100, KeyCaptureHandler)

    btnBack := g.Add("Button", "x24 y265 w80 h32", "←  Back")
    btnBack.SetFont("s10")
    btnBack.OnEvent("Click", (*) => (OnMessage(0x100, KeyCaptureHandler, 0), g.Destroy(), ShowPage1()))

    btnNext := g.Add("Button", "x390 y265 w86 h32", "Next  →")
    btnNext.SetFont("s10 w600")
    btnNext.OnEvent("Click", (*) => (OnMessage(0x100, KeyCaptureHandler, 0), g.Destroy(), ShowPage3()))

    g.Show("w500 h315")
}

; ══════════════════════════════════════════════════════════════
;  PAGE 3 — Folder picker
; ══════════════════════════════════════════════════════════════
ShowPage3() {
    global gSaveFolder

    g := Gui("+AlwaysOnTop -Resize", "Setup — paste-screenshot-in-terminal")
    g.SetFont("s10", "Segoe UI")
    g.BackColor := "FFFFFF"
    g.MarginX := 0
    g.MarginY := 0

    ; ── Header
    g.Add("Text", "x0 y0 w500 h70 +0x200 Background1a1a2e")
    g.SetFont("s14 w700 cWhite", "Segoe UI")
    g.Add("Text", "x24 y18 w460 BackgroundTrans", "paste-screenshot-in-terminal")
    g.SetFont("s9 w400 cCCCCCC", "Segoe UI")
    g.Add("Text", "x24 y44 w460 BackgroundTrans", "Paste clipboard images into any terminal as a file path")

    ; ── Body
    g.SetFont("s10 w600 c1a1a2e", "Segoe UI")
    g.Add("Text", "x24 y90", "Step 3 of 4 — Save folder")
    g.SetFont("s10 w400 c333333", "Segoe UI")
    g.Add("Text", "x24 y115 w452", "Images are saved here temporarily each time you use the hotkey. You can clear this folder anytime.")

    folderEdit := g.Add("Edit", "x24 y155 w368 h28", gSaveFolder)
    folderEdit.SetFont("s9", "Consolas")

    btnBrowse := g.Add("Button", "x400 y153 w76 h30", "Browse...")
    btnBrowse.SetFont("s9")
    btnBrowse.OnEvent("Click", (*) => PickFolder(folderEdit))

    btnBack := g.Add("Button", "x24 y205 w80 h32", "←  Back")
    btnBack.SetFont("s10")
    btnBack.OnEvent("Click", (*) => g.Destroy(), ShowPage2())

    btnNext := g.Add("Button", "x390 y205 w86 h32", "Next  →")
    btnNext.SetFont("s10 w600")
    btnNext.OnEvent("Click", (*) => (gSaveFolder := folderEdit.Value, g.Destroy(), ShowPage4()))

    g.Show("w500 h255")
}

PickFolder(editCtrl) {
    chosen := DirSelect("*" editCtrl.Value, 3, "Choose folder for temporary images")
    if (chosen != "")
        editCtrl.Value := chosen
}

; ══════════════════════════════════════════════════════════════
;  PAGE 4 — Interactive test
; ══════════════════════════════════════════════════════════════
ShowPage4() {
    global gKeyCombo, gSaveFolder, gConfigFile, gScriptMain, gAhkExe

    ; Save config now
    if (!DirExist(gSaveFolder))
        DirCreate(gSaveFolder)
    IniWrite(gKeyCombo,   gConfigFile, "Settings", "Hotkey")
    IniWrite(gSaveFolder, gConfigFile, "Settings", "SaveFolder")

    ; Launch main script
    if (gAhkExe != "" && FileExist(gScriptMain))
        Run('"' gAhkExe '" "' gScriptMain '"')

    g := Gui("+AlwaysOnTop -Resize", "Setup — paste-screenshot-in-terminal")
    g.SetFont("s10", "Segoe UI")
    g.BackColor := "FFFFFF"
    g.MarginX := 0
    g.MarginY := 0

    ; ── Header
    g.Add("Text", "x0 y0 w500 h70 +0x200 Background1a1a2e")
    g.SetFont("s14 w700 cWhite", "Segoe UI")
    g.Add("Text", "x24 y18 w460 BackgroundTrans", "paste-screenshot-in-terminal")
    g.SetFont("s9 w400 cCCCCCC", "Segoe UI")
    g.Add("Text", "x24 y44 w460 BackgroundTrans", "Paste clipboard images into any terminal as a file path")

    ; ── Body
    g.SetFont("s10 w600 c1a1a2e", "Segoe UI")
    g.Add("Text", "x24 y90", "Step 4 of 4 — Test it!")

    ; Instructions
    g.SetFont("s10 w400 c333333", "Segoe UI")
    g.Add("Text", "x24 y115 w452", "1.  Press  Win + Shift + S  and capture any area of your screen")
    g.Add("Text", "x24 y136 w452", "2.  Click the box below and press  " FormatKeyDisplay(gKeyCombo))
    g.Add("Text", "x24 y157 w452", "3.  The image path should appear automatically  ↓")

    ; Test box
    testEdit := g.Add("Edit", "x24 y183 w452 h32 -Multi")
    testEdit.SetFont("s9", "Consolas")
    testEdit.Value := ""

    ; Status feedback
    statusCtrl := g.Add("Text", "x24 y223 w452 h20", "")
    statusCtrl.SetFont("s9 w600")

    testEdit.OnEvent("Change", (*) => CheckTest(testEdit, statusCtrl))

    btnBack := g.Add("Button", "x24 y258 w80 h32", "←  Back")
    btnBack.SetFont("s10")
    btnBack.OnEvent("Click", (*) => g.Destroy(), ShowPage3())

    btnFinish := g.Add("Button", "x370 y258 w106 h32", "Finish  ✓")
    btnFinish.SetFont("s10 w600")
    btnFinish.OnEvent("Click", (*) => (g.Destroy(), ShowDone()))

    g.Show("w500 h308")
}

CheckTest(editCtrl, statusCtrl) {
    val := Trim(editCtrl.Value)
    if (FileExist(val) && RegExMatch(val, "i)\.(png|jpg|jpeg|bmp|gif|webp)$")) {
        statusCtrl.SetFont("s9 w600 c1e7e34", "Segoe UI")
        statusCtrl.Text := "✔  It worked! Image saved and path pasted correctly."
    } else if (StrLen(val) > 3) {
        statusCtrl.SetFont("s9 w400 c999999", "Segoe UI")
        statusCtrl.Text := "Waiting for a valid image path..."
    }
}

; ══════════════════════════════════════════════════════════════
;  Key capture handler (global — used by ShowPage2)
; ══════════════════════════════════════════════════════════════
KeyCaptureHandler(wParam, lParam, msg, hwnd) {
    global gKeyCombo, gKeyBadge, gCaptureBox

    if (!IsObject(gCaptureBox) || hwnd != gCaptureBox.Hwnd)
        return

    mods := ""
    if GetKeyState("Ctrl",  "P") mods .= "^"
    if GetKeyState("Shift", "P") mods .= "+"
    if GetKeyState("Alt",   "P") mods .= "!"
    if GetKeyState("LWin",  "P") || GetKeyState("RWin", "P") mods .= "#"

    keyName := GetKeyName(Format("vk{:X}", wParam))

    if RegExMatch(keyName, "i)^(Ctrl|Shift|Alt|LWin|RWin|Control|LControl|RControl|LShift|RShift|LAlt|RAlt)$")
        return

    if (mods != "") {
        gKeyCombo := mods . keyName
        gKeyBadge.Text    := FormatKeyDisplay(gKeyCombo)
        gCaptureBox.Value := gKeyCombo
        gCaptureBox.SetFont("s9 c1a1a2e", "Segoe UI")
    }
    return 0
}

; ══════════════════════════════════════════════════════════════
;  Done
; ══════════════════════════════════════════════════════════════
ShowDone() {
    global gScriptMain, gAhkExe

    result := MsgBox(
        "Setup complete!`n`nThe script is now running in your system tray.`n`nWould you like it to start automatically with Windows?",
        "All done!",
        "YesNo Icon?"
    )

    if (result = "Yes") {
        startupLink := A_Startup "\paste-screenshot-in-terminal.lnk"
        FileCreateShortcut(gScriptMain, startupLink,, "", "", gAhkExe)
    }

    ExitApp()
}

; ══════════════════════════════════════════════════════════════
;  Helpers
; ══════════════════════════════════════════════════════════════
FindAHKExe() {
    candidates := [
        "C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe",
        "C:\Program Files\AutoHotkey\v2\AutoHotkey32.exe",
        "C:\Program Files\AutoHotkey\AutoHotkey.exe",
        "C:\Program Files (x86)\AutoHotkey\AutoHotkey.exe"
    ]
    for path in candidates
        if FileExist(path)
            return path
    try {
        dir := RegRead("HKLM\SOFTWARE\AutoHotkey", "InstallDir")
        if FileExist(dir "\v2\AutoHotkey64.exe")
            return dir "\v2\AutoHotkey64.exe"
        if FileExist(dir "\AutoHotkey.exe")
            return dir "\AutoHotkey.exe"
    }
    return ""
}

FormatKeyDisplay(combo) {
    out := combo
    out := StrReplace(out, "^", "Ctrl + ")
    out := StrReplace(out, "+", "Shift + ")
    out := StrReplace(out, "!", "Alt + ")
    out := StrReplace(out, "#", "Win + ")
    return out
}
