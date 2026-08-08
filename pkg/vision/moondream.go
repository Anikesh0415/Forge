package vision

import (
	"fmt"
	"image/png"
	"os"
	"os/exec"
	"strings"
	"syscall"

	"github.com/kbinani/screenshot"
)

func CaptureAndAnalyze() (string, error) {
	// 1. Take Screenshot
	bounds := screenshot.GetDisplayBounds(0)
	img, err := screenshot.CaptureRect(bounds)
	if err != nil {
		return "", fmt.Errorf("failed to capture screen: %w", err)
	}

	file, err := os.Create("temp_screenshot.png")
	if err != nil {
		return "", fmt.Errorf("failed to create screenshot file: %w", err)
	}
	defer file.Close()
	defer os.Remove("temp_screenshot.png")

	if err := png.Encode(file, img); err != nil {
		return "", fmt.Errorf("failed to encode png: %w", err)
	}

	// 2. Call Moondream via llama-mtmd-cli
	// Assuming it runs from root E:\AIF_Project
	llavaExe := `E:\AIF_Project\llama.cpp\build\bin\Release\llama-mtmd-cli.exe`
	modelPath := `E:\AIF_Project\models\moondream2-text-model-f16.gguf`
	mmprojPath := `E:\AIF_Project\models\moondream2-mmproj-f16.gguf`

	// Fast execution parameters
	prompt := `Describe the screen layout and give coordinate hints for interactive elements.`
	cmd := exec.Command(llavaExe,
		"-m", modelPath,
		"--mmproj", mmprojPath,
		"--image", "temp_screenshot.png",
		"-p", prompt,
		"--chat-template", "chatml",
		"-c", "4096",
		"--temp", "0.1",
	)
	cmd.SysProcAttr = &syscall.SysProcAttr{HideWindow: true}

	out, err := cmd.CombinedOutput()
	if err != nil {
		return "", fmt.Errorf("llava execution failed: %v\noutput: %s", err, string(out))
	}

	return strings.TrimSpace(string(out)), nil
}
