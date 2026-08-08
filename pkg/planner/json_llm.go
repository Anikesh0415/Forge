package planner

import (
	"encoding/json"
	"fmt"
	"os/exec"
	"regexp"
	"syscall"

	"forge/pkg/executor"
)

func PlanActions(intent string, visionContext string, uiaContext string, history string) ([]executor.Action, error) {
	prompt := fmt.Sprintf(`You are a PC automation agent with zero hallucinations. 
You are given Vision Context, EXACT UI Element Coordinates (UIA), and a History of previous actions.
If the intent is fully accomplished, output ONLY [{"action": "done"}].

Vision Context:
%s

UIA Elements (Use exact X,Y coordinates from here!):
%s

History of Previous Actions (Avoid repeating failures):
%s

User Intent: %s

Respond ONLY with a JSON array of actions to execute right now.
Actions format:
[{"action": "click"}, {"action": "move", "x": 100, "y": 200}, {"action": "type", "text": "hello"}, {"action": "sleep", "ms": 500}, {"action": "done"}]

JSON:`, visionContext, uiaContext, history, intent)

	llamaExe := `E:\AIF_Project\llama.cpp\build\bin\Release\llama-cli.exe`
	modelPath := `E:\AIF_Project\models\qwen2.5-0.5b-instruct-q4_k_m.gguf`

	cmd := exec.Command(llamaExe,
		"-m", modelPath,
		"-p", prompt,
		"-c", "16384",
		"-n", "256",
		"--temp", "0.1",
	)
	cmd.SysProcAttr = &syscall.SysProcAttr{HideWindow: true}

	out, err := cmd.CombinedOutput()
	if err != nil {
		return nil, fmt.Errorf("llama execution failed: %v", err)
	}

	response := string(out)

	// Extract JSON array
	re := regexp.MustCompile(`(?s)\[\s*\{.*?\}\s*\]`)
	match := re.FindString(response)
	if match == "" {
		return nil, fmt.Errorf("no valid JSON array found in output:\n%s", response)
	}

	var actions []executor.Action
	if err := json.Unmarshal([]byte(match), &actions); err != nil {
		return nil, fmt.Errorf("JSON parse error: %v\nJSON:\n%s", err, match)
	}

	return actions, nil
}
