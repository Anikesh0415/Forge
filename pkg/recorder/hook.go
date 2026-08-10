package recorder

import (
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"syscall"
	"time"
	"unsafe"

	"forge/pkg/executor"
	"forge/pkg/skills"
)

func notifyUser(title, message string) {
	ps1 := fmt.Sprintf(`
Add-Type -AssemblyName System.Windows.Forms
$balloon = New-Object System.Windows.Forms.NotifyIcon
$balloon.Icon = [System.Drawing.SystemIcons]::Information
$balloon.BalloonTipIcon = "Info"
$balloon.BalloonTipText = "%s"
$balloon.BalloonTipTitle = "%s"
$balloon.Visible = $true
$balloon.ShowBalloonTip(2000)
Start-Sleep -Seconds 3
$balloon.Dispose()
`, message, title)
	os.WriteFile("notify.ps1", []byte(ps1), 0644)
	cmd := exec.Command("powershell", "-ExecutionPolicy", "Bypass", "-File", "notify.ps1")
	cmd.SysProcAttr = &syscall.SysProcAttr{HideWindow: true}
	cmd.Start()
}

var (
	user32               = syscall.NewLazyDLL("user32.dll")
	procSetWindowsHookEx = user32.NewProc("SetWindowsHookExW")
	procCallNextHookEx   = user32.NewProc("CallNextHookEx")
	procUnhookWindowsHookEx = user32.NewProc("UnhookWindowsHookEx")
	procGetMessageW      = user32.NewProc("GetMessageW")

	keyboardHook uintptr
	mouseHook    uintptr

	isRecording     bool
	recordedActions []executor.Action
)

const (
	WH_KEYBOARD_LL = 13
	WH_MOUSE_LL    = 14
	WM_KEYDOWN     = 0x0100
	WM_LBUTTONDOWN = 0x0201
	VK_R         = 0x52
	VK_CONTROL   = 0x11
	VK_SHIFT     = 0x10
)

var procGetAsyncKeyState = user32.NewProc("GetAsyncKeyState")

func isKeyDown(vkCode int) bool {
	ret, _, _ := procGetAsyncKeyState.Call(uintptr(vkCode))
	return (ret & 0x8000) != 0
}

type KBDLLHOOKSTRUCT struct {
	VkCode      uint32
	ScanCode    uint32
	Flags       uint32
	Time        uint32
	DwExtraInfo uintptr
}

type POINT struct {
	X int32
	Y int32
}

type MSLLHOOKSTRUCT struct {
	Pt          POINT
	MouseData   uint32
	Flags       uint32
	Time        uint32
	DwExtraInfo uintptr
}

func keyboardCallback(nCode int, wParam uintptr, lParam uintptr) uintptr {
	if nCode >= 0 && wParam == WM_KEYDOWN {
		kbd := (*KBDLLHOOKSTRUCT)(unsafe.Pointer(lParam))
		
		// Trigger on Ctrl + Shift + R
		if kbd.VkCode == VK_R && isKeyDown(VK_CONTROL) && isKeyDown(VK_SHIFT) {
			toggleRecording()
			return 1 // block the R key from reaching other apps to prevent typing 'r'
		}
		
		if isRecording {
			// Extremely naive key capture for demo purposes
			keyName := fmt.Sprintf("%c", kbd.VkCode)
			// Handle space specifically
			if kbd.VkCode == 0x20 {
				keyName = "space"
			}
			recordedActions = append(recordedActions, executor.Action{
				Type: "type",
				Text: strings.ToLower(keyName),
			})
		}
	}
	ret, _, _ := procCallNextHookEx.Call(keyboardHook, uintptr(nCode), wParam, lParam)
	return ret
}

func mouseCallback(nCode int, wParam uintptr, lParam uintptr) uintptr {
	if nCode >= 0 && wParam == WM_LBUTTONDOWN {
		ms := (*MSLLHOOKSTRUCT)(unsafe.Pointer(lParam))
		
		if isRecording {
			recordedActions = append(recordedActions, executor.Action{
				Type: "move",
				X:    int(ms.Pt.X),
				Y:    int(ms.Pt.Y),
			})
			recordedActions = append(recordedActions, executor.Action{
				Type: "sleep",
				Ms:   200,
			})
			recordedActions = append(recordedActions, executor.Action{
				Type: "click",
			})
		}
	}
	ret, _, _ := procCallNextHookEx.Call(mouseHook, uintptr(nCode), wParam, lParam)
	return ret
}

func toggleRecording() {
	if !isRecording {
		fmt.Println("\n[REC] Started recording macro... Press Ctrl+Shift+R again to stop.")
		notifyUser("Forge Recorder", "🔴 Started recording macro... Press Ctrl+Shift+R to stop.")
		recordedActions = []executor.Action{}
		isRecording = true
	} else {
		isRecording = false
		fmt.Println("[REC] Stopped recording.")
		notifyUser("Forge Recorder", "⏹️ Stopped recording.")
		
		if len(recordedActions) > 0 {
			saveMacro()
		}
	}
}

func saveMacro() {
	timestamp := time.Now().Format("20060102_150405")
	skillName := fmt.Sprintf("macro %s", timestamp)
	
	skill := skills.DynamicSkill{
		SkillName: skillName,
		Actions:   recordedActions,
	}
	
	data, _ := json.MarshalIndent(skill, "", "  ")
	filename := filepath.Join("skills_db", fmt.Sprintf("learned_%s.json", timestamp))
	
	os.WriteFile(filename, data, 0644)
	fmt.Printf("[REC] Saved macro as '%s' to %s\n", skillName, filename)
	notifyUser("Forge Recorder", fmt.Sprintf("✅ Saved macro: %s", skillName))
	
	// Load it immediately
	skills.Register(&skill)
}

func StartHooks() {
	go func() {
		cbKeyboard := syscall.NewCallback(keyboardCallback)
		hKbd, _, _ := procSetWindowsHookEx.Call(
			WH_KEYBOARD_LL,
			cbKeyboard,
			0,
			0,
		)
		keyboardHook = hKbd

		cbMouse := syscall.NewCallback(mouseCallback)
		hMouse, _, _ := procSetWindowsHookEx.Call(
			WH_MOUSE_LL,
			cbMouse,
			0,
			0,
		)
		mouseHook = hMouse

		fmt.Println("Watch-and-Learn Macro Recorder active. Press Ctrl+Shift+R to record.")

		// Message loop to keep hooks alive
		type MSG struct {
			Hwnd    uintptr
			Message uint32
			WParam  uintptr
			LParam  uintptr
			Time    uint32
			Pt      POINT
		}
		var msg MSG
		for {
			ret, _, _ := procGetMessageW.Call(uintptr(unsafe.Pointer(&msg)), 0, 0, 0)
			if int32(ret) <= 0 {
				break
			}
		}
	}()
}
