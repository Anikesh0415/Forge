package planner

import (
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"regexp"
	"strings"
	"syscall"

	"forge/pkg/executor"
)

func PlanActions(intent string, visionContext string, uiaContext string, history string) ([]executor.Action, error) {
	prompt := fmt.Sprintf(`<|im_start|>system
You are a highly precise PC automation agent.
Output ONLY a VALID JSON array of action objects. No explanations. No markdown.
<|im_end|>
<|im_start|>user
Vision Context: %s

UIA Elements:
%s

History:
%s

User Intent: %s

Available Actions MUST follow this exact JSON format:
[
  {"type": "click_element", "name": "exact name from UIA Elements"},
  {"type": "move", "x": 100, "y": 200},
  {"type": "click"},
  {"type": "type", "text": "text to type"},
  {"type": "key", "key": "enter"},
  {"type": "sleep", "ms": 500},
  {"type": "done"}
]
<|im_end|>
<|im_start|>assistant
`, visionContext, uiaContext, history, intent)

	os.WriteFile("temp_prompt.txt", []byte(prompt), 0644)

	llamaExe := `E:\AIF_Project\llama.cpp\build\bin\Release\llama-cli.exe`
	modelPath := `E:\AIF_Project\models\qwen2.5-0.5b-instruct-q4_k_m.gguf`

	cmd := exec.Command(llamaExe,
		"-m", modelPath,
		"-f", "temp_prompt.txt",
		"-c", "4096",
		"-n", "1024",
		"--temp", "0.1",
		"--repeat-penalty", "1.2",
		"--no-conversation",
		"--simple-io",
		"--no-display-prompt",
	)
	cmd.SysProcAttr = &syscall.SysProcAttr{HideWindow: true}

	out, err := cmd.CombinedOutput()
	response := string(out)

	// Only look at what the assistant generated (ignore echoed prompt)
	parts := strings.Split(response, "<|im_start|>assistant")
	assistantResp := response
	if len(parts) > 1 {
		assistantResp = parts[len(parts)-1]
	}

	// Extract JSON array
	re := regexp.MustCompile(`(?s)\[\s*\{.*?\}\s*\]`)
	match := re.FindString(assistantResp)
	if match == "" {
		if err != nil {
			return nil, fmt.Errorf("llama execution failed: %v\nOutput: %s", err, response)
		}
		return nil, fmt.Errorf("no valid JSON array found in output:\n%s", response)
	}

	var actions []executor.Action
	if err := json.Unmarshal([]byte(match), &actions); err != nil {
		return nil, fmt.Errorf("JSON parse error: %v\nJSON:\n%s", err, match)
	}

	return actions, nil
}

