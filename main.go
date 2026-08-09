package main

import (
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"strings"
	"syscall"
	"time"

	"forge/pkg/executor"
	"forge/pkg/planner"
	"forge/pkg/skills"
	"forge/pkg/uia"
	"forge/pkg/vision"
)

func main() {
	logFile, err := os.OpenFile("forge.log", os.O_CREATE|os.O_WRONLY|os.O_TRUNC, 0666)
	if err == nil {
		os.Stdout = logFile
		os.Stderr = logFile
		defer logFile.Close()
	}
	
	for {
		handleSummon()
	}
}

func handleSummon() {
	// 1. Pop up native VBS input box
	os.Remove("intent.txt")
	cmd := exec.Command("wscript", "//nologo", "input.vbs")
	cmd.SysProcAttr = &syscall.SysProcAttr{HideWindow: true}
	err := cmd.Run()
	if err != nil {
		return
	}

	out, err := os.ReadFile("intent.txt")
	intent := strings.TrimSpace(string(out))
	if err != nil || intent == "" {
		os.Exit(0)
	}

	intent = strings.TrimSpace(strings.ToLower(intent))
	if intent == "exit" || intent == "quit" {
		os.Exit(0)
	}
	fmt.Printf("User Intent: %s\n\n", intent)

	// HYBRID ORCHESTRATOR: Check if intent matches any advanced Skills
	matchedSkill := skills.MatchIntent(intent)
	if matchedSkill != nil {
		fmt.Printf("Orchestrator: Routing to Advanced Skill '%s'\n", matchedSkill.Name())
		matchedSkill.Execute(intent)
		return
	}

	// Legacy simple fallback for "open X" (under 3 words, no commas)
	words := strings.Fields(intent)
	if strings.HasPrefix(intent, "open ") && len(words) <= 3 && !strings.Contains(intent, ",") {
		appName := strings.TrimPrefix(intent, "open ")
		fmt.Printf("Rule-based fallback: opening '%s'\n", appName)
		actions := []executor.Action{
			{Type: "key", Key: "win"},
			{Type: "sleep", Ms: 800},
			{Type: "type", Text: appName},
			{Type: "sleep", Ms: 800},
			{Type: "key", Key: "enter"},
		}
		executor.ExecutePlan(actions)
		return
	}

	history := "[]"
	var allActions []executor.Action

	// DYNAMIC AI ORCHESTRATOR (Fallback)
	for step := 1; step <= 3; step++ {
		fmt.Printf("\n--- Step %d ---\n", step)
		
		fmt.Println("Capturing screen and analyzing via Moondream...")
		visionContext, err := vision.CaptureAndAnalyze()
		if err != nil {
			fmt.Printf("Vision failed: %v\n", err)
			visionContext = "Screen context unavailable."
		}

		fmt.Println("Extracting UI Automation Elements...")
		uiaContext, err := uia.DumpUI()
		if err != nil {
			fmt.Printf("UIA failed: %v\n", err)
			uiaContext = "[]"
		}

		fmt.Println("Planning actions...")
		actions, err := planner.PlanActions(intent, visionContext, uiaContext, history)
		if err != nil {
			fmt.Printf("Planner failed: %v\n", err)
			return
		}
		
		fmt.Printf("Generated Plan: %+v\n", actions)

		// SAFEGUARD CHECK
		if !checkSafeguards(actions) {
			fmt.Println("Safeguard triggered: User denied permission for high-risk action. Aborting.")
			return
		}

		isDone := false
		var executedThisStep []executor.Action
		for _, act := range actions {
			if act.Type == "done" {
				isDone = true
				break
			}
			executedThisStep = append(executedThisStep, act)
		}

		if len(executedThisStep) > 0 {
			fmt.Println("Executing...")
			executor.ExecutePlan(executedThisStep)
			allActions = append(allActions, executedThisStep...)
			
			historyBytes, _ := json.Marshal(allActions)
			history = string(historyBytes)
		}

		if isDone {
			fmt.Println("Intent fully achieved. Exiting loop.")
			break
		}

		time.Sleep(1 * time.Second)
	}
	
	fmt.Println("Done!")
}

// checkSafeguards scans for high-risk words and prompts the user natively via VBS.
func checkSafeguards(actions []executor.Action) bool {
	dangerousKeywords := []string{"delete", "remove", "pay", "buy", "transfer"}
	
	for _, act := range actions {
		if act.Type == "type" {
			lowerText := strings.ToLower(act.Text)
			for _, kw := range dangerousKeywords {
				if strings.Contains(lowerText, kw) {
					return askUserPermission(fmt.Sprintf("Forge is about to type a high-risk phrase containing '%s'. Proceed?", kw))
				}
			}
		} else if act.Type == "click_element" {
			lowerName := strings.ToLower(act.Name)
			for _, kw := range dangerousKeywords {
				if strings.Contains(lowerName, kw) {
					return askUserPermission(fmt.Sprintf("Forge is about to click a high-risk button: '%s'. Proceed?", act.Name))
				}
			}
		}
	}
	return true
}

func askUserPermission(msg string) bool {
	vbsScript := fmt.Sprintf(`
Dim result
result = MsgBox("%s", vbYesNo + vbExclamation + vbSystemModal, "Forge Safeguard")
If result = vbYes Then
    WScript.Quit 0
Else
    WScript.Quit 1
End If
`, msg)

	os.WriteFile("safeguard.vbs", []byte(vbsScript), 0644)
	defer os.Remove("safeguard.vbs")

	cmd := exec.Command("wscript", "//nologo", "safeguard.vbs")
	cmd.SysProcAttr = &syscall.SysProcAttr{HideWindow: true}
	err := cmd.Run()
	
	// Exit code 0 means Yes, 1 means No
	if exitErr, ok := err.(*exec.ExitError); ok {
		return exitErr.ExitCode() == 0
	}
	return err == nil
}
