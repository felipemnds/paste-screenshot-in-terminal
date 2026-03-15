#Requires AutoHotkey v2.0
#SingleInstance Force

; ── Configuration ────────────────────────────────────────────────────────────
configFile := A_ScriptDir "\..\config.ini"
saveFolder := IniRead(configFile, "Settings", "SaveFolder", "")
if (saveFolder = "")
    saveFolder := A_MyDocuments "\paste-screenshot-temp"
keyCombo   := IniRead(configFile, "Settings", "Hotkey", "^+s")
if (keyCombo = "")
    keyCombo := "^+s"

; ── Register hotkey ───────────────────────────────────────────────────────────
HotKey(keyCombo, PasteScreenshot)

; ── Main function ─────────────────────────────────────────────────────────────
PasteScreenshot(_) {
    if (!DirExist(saveFolder))
        DirCreate(saveFolder)

    ; Check if clipboard has an image
    if !ClipboardHasImage() {
        ToolTip("No image found in clipboard.")
        SetTimer(() => ToolTip(), -2000)
        return
    }

    timestamp := FormatTime(, "yyyy-MM-dd_HH-mm-ss")
    filePath  := saveFolder "\screenshot_" timestamp ".png"

    ; Save image from clipboard to file
    if SaveClipboardImage(filePath) {
        A_Clipboard := filePath
        Send("^v")
        ToolTip("Image pasted: " filePath)
        SetTimer(() => ToolTip(), -2000)
    } else {
        ToolTip("Failed to save image.")
        SetTimer(() => ToolTip(), -2000)
    }
}

; ── Helpers ───────────────────────────────────────────────────────────────────
ClipboardHasImage() {
    return DllCall("IsClipboardFormatAvailable", "UInt", 2)  ; CF_BITMAP = 2
}

SaveClipboardImage(filePath) {
    ; Use PowerShell to save the clipboard image as PNG
    psCmd := 'powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -Command "'
           . 'Add-Type -AssemblyName System.Windows.Forms; '
           . 'Add-Type -AssemblyName System.Drawing; '
           . '$img = [System.Windows.Forms.Clipboard]::GetImage(); '
           . 'if ($img) { $img.Save(\"' filePath '\", [System.Drawing.Imaging.ImageFormat]::Png) }'
           . '"'
    RunWait(psCmd, , "Hide")
    return FileExist(filePath)
}
