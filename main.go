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
	
	handleSummon()
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
		return
	}

	intent = strings.TrimSpace(strings.ToLower(intent))
	fmt.Printf("User Intent: %s\n\n", intent)

	// Rule-based fallback for simple "open X" commands (max 3 words, no commas)
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

	// Self-Correction Loop (Max 3 steps to prevent runaway loops)
	for step := 1; step <= 3; step++ {
		fmt.Printf("\n--- Step %d ---\n", step)
		
		// 1. Capture Contexts
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

		// 2. Plan Actions
		fmt.Println("Planning actions...")
		actions, err := planner.PlanActions(intent, visionContext, uiaContext, history)
		if err != nil {
			fmt.Printf("Planner failed: %v\n", err)
			return
		}
		
		fmt.Printf("Generated Plan: %+v\n", actions)

		// 3. Execute
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
			
			// Update history for next iteration
			historyBytes, _ := json.Marshal(allActions)
			history = string(historyBytes)
		}

		if isDone {
			fmt.Println("Intent fully achieved. Exiting loop.")
			break
		}

		// Wait for UI to settle before next step
		time.Sleep(1 * time.Second)
	}
	
	fmt.Println("Done!")
}
