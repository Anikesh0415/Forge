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
You are a precise PC automation agent.
Output ONLY ONE VALID JSON action object for the NEXT step. No arrays. No explanations.
<|im_end|>
<|im_start|>user
Vision Context: %s

UIA Elements:
%s

History:
%s

User Intent: %s

Available Actions format:
{"type": "click_element", "name": "exact name from UIA Elements"}
{"type": "type", "text": "text to type"}
{"type": "key", "key": "enter"}
{"type": "sleep", "ms": 500}
{"type": "done"}

Example 1:
User Intent: search for cats
History: opened browser
UIA Elements: [{"name": "Search Box", "type": "Edit"}]
Assistant:
{"type": "click_element", "name": "Search Box"}
<|im_end|>
<|im_start|>assistant
`, visionContext, uiaContext, history, intent)

	os.WriteFile("temp_prompt.txt", []byte(prompt), 0644)

	llamaExe := `E:\AIF_Project\llama.cpp\build\bin\Release\llama-cli.exe`
	modelPath := `E:\AIF_Project\models\qwen2.5-0.5b-instruct-q4_k_m.gguf`

	cmd := exec.Command(llamaExe,
		"-m", modelPath,
		"-f", "temp_prompt.txt",
		"-c", "16384",
		"-n", "512",
		"--temp", "0.1",
		"--repeat-penalty", "1.2",
		"--no-conversation",
		"--simple-io",
		"--no-display-prompt",
	)
	cmd.SysProcAttr = &syscall.SysProcAttr{HideWindow: true}

	out, err := cmd.CombinedOutput()
	response := string(out)

	parts := strings.Split(response, "<|im_start|>assistant")
	assistantResp := response
	if len(parts) > 1 {
		assistantResp = parts[len(parts)-1]
	}

	// Extract ONE JSON object
	re := regexp.MustCompile(`(?s)\{.*?\}`)
	match := re.FindString(assistantResp)
	if match == "" {
		if err != nil {
			return nil, fmt.Errorf("llama execution failed: %v\nOutput: %s", err, response)
		}
		return nil, fmt.Errorf("no valid JSON object found in output:\n%s", response)
	}

	match = regexp.MustCompile(`(?i)([{,]\s*)x\s*:`).ReplaceAllString(match, `$1"x":`)
	match = regexp.MustCompile(`(?i)([{,]\s*)y\s*:`).ReplaceAllString(match, `$1"y":`)

	var action executor.Action
	if err := json.Unmarshal([]byte(match), &action); err != nil {
		return nil, fmt.Errorf("JSON parse error: %v\nJSON:\n%s", err, match)
	}

	// We return it as an array of 1 to keep compatibility with existing code
	return []executor.Action{action}, nil
}

