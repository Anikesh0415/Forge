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

Example 1 (Opening an app):
User Intent: open notepad
History: 
UIA Elements: [{"name": "Start", "type": "Button"}]
Assistant:
{"type": "key", "key": "win"}

Example 2 (Typing an app name):
User Intent: open notepad
History: pressed win
UIA Elements: [{"name": "Search Box", "type": "Edit"}]
Assistant:
{"type": "type", "text": "notepad"}

Example 3 (Clicking a web element):
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
		"--grammar-file", `pkg\planner\action.gbnf`,
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

	if err != nil {
		return nil, fmt.Errorf("llama execution failed: %v\nOutput: %s", err, response)
	}

	// Because of GBNF, the response should be exactly the valid JSON action.
	// We just need to extract everything after <|im_start|>assistant if present,
	// though GBNF on completion might just return the raw JSON.
	parts := strings.Split(response, "<|im_start|>assistant")
	assistantResp := strings.TrimSpace(parts[len(parts)-1])

	var action executor.Action
	if err := json.Unmarshal([]byte(assistantResp), &action); err != nil {
		// Fallback clean if there are minor artifacts (though GBNF should prevent this)
		re := regexp.MustCompile(`(?s)\{.*?\}`)
		match := re.FindString(assistantResp)
		if match != "" {
			if parseErr := json.Unmarshal([]byte(match), &action); parseErr == nil {
				return []executor.Action{action}, nil
			}
		}
		return nil, fmt.Errorf("JSON parse error: %v\nResponse:\n%s", err, assistantResp)
	}

	return []executor.Action{action}, nil
}


