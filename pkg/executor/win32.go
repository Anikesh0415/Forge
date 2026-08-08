package executor

import (
	"syscall"
	"time"
	"unsafe"
)

var (
	user32        = syscall.MustLoadDLL("user32.dll")
	procSendInput = user32.MustFindProc("SendInput")
)

type Action struct {
	Type string `json:"action"`
	X    int    `json:"x,omitempty"`
	Y    int    `json:"y,omitempty"`
	Text string `json:"text,omitempty"`
	Ms   int    `json:"ms,omitempty"`
}

func ExecutePlan(actions []Action) {
	for _, act := range actions {
		switch act.Type {
		case "move":
			moveMouse(act.X, act.Y)
		case "click":
			clickMouse()
		case "type":
			typeText(act.Text)
		case "sleep":
			time.Sleep(time.Duration(act.Ms) * time.Millisecond)
		}
		time.Sleep(100 * time.Millisecond) // small delay between actions
	}
}

func moveMouse(x, y int) {
	type MOUSEINPUT struct {
		Dx          int32
		Dy          int32
		MouseData   uint32
		DwFlags     uint32
		Time        uint32
		DwExtraInfo uintptr
	}
	type INPUT struct {
		Type uint32
		Mi   MOUSEINPUT
		Pad  [8]byte
	}

	screenW := int32(1920) // TODO: GetSystemMetrics
	screenH := int32(1080)
	absX := int32(x) * 65535 / screenW
	absY := int32(y) * 65535 / screenH

	var i INPUT
	i.Type = 0
	i.Mi.Dx = absX
	i.Mi.Dy = absY
	i.Mi.DwFlags = 0x8000 | 0x0001 // MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_MOVE

	procSendInput.Call(1, uintptr(unsafe.Pointer(&i)), uintptr(unsafe.Sizeof(i)))
}

func clickMouse() {
	type MOUSEINPUT struct {
		Dx          int32
		Dy          int32
		MouseData   uint32
		DwFlags     uint32
		Time        uint32
		DwExtraInfo uintptr
	}
	type INPUT struct {
		Type uint32
		Mi   MOUSEINPUT
		Pad  [8]byte
	}

	var down INPUT
	down.Type = 0
	down.Mi.DwFlags = 0x0002 // MOUSEEVENTF_LEFTDOWN

	var up INPUT
	up.Type = 0
	up.Mi.DwFlags = 0x0004 // MOUSEEVENTF_LEFTUP

	inputs := []INPUT{down, up}
	procSendInput.Call(2, uintptr(unsafe.Pointer(&inputs[0])), uintptr(unsafe.Sizeof(down)))
}

func typeText(text string) {
	type KEYBDINPUT struct {
		WVk         uint16
		WScan       uint16
		DwFlags     uint32
		Time        uint32
		DwExtraInfo uintptr
	}
	type INPUT struct {
		Type uint32
		Ki   KEYBDINPUT
		Pad  [8]byte
	}

	var inputs []INPUT
	for _, char := range text {
		// key down
		var down INPUT
		down.Type = 1
		down.Ki.WScan = uint16(char)
		down.Ki.DwFlags = 0x0004 // KEYEVENTF_UNICODE

		// key up
		var up INPUT
		up.Type = 1
		up.Ki.WScan = uint16(char)
		up.Ki.DwFlags = 0x0004 | 0x0002 // KEYEVENTF_UNICODE | KEYEVENTF_KEYUP

		inputs = append(inputs, down, up)
	}

	if len(inputs) > 0 {
		procSendInput.Call(uintptr(len(inputs)), uintptr(unsafe.Pointer(&inputs[0])), uintptr(unsafe.Sizeof(inputs[0])))
	}
}
