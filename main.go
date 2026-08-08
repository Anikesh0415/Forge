package main

import (
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"strings"
	"time"

	"forge/pkg/executor"
	"forge/pkg/planner"
	"forge/pkg/uia"
	"forge/pkg/vision"
)

func main() {
	handleSummon()
}

func handleSummon() {
	// 1. Pop up native VBS input box
	os.Remove("intent.txt")
	cmd := exec.Command("wscript", "//nologo", "input.vbs")
	err := cmd.Run()
	if err != nil {
		return
	}

	out, err := os.ReadFile("intent.txt")
	text := strings.TrimSpace(string(out))
	if err != nil || text == "" {
		return
	}

	fmt.Println("User Intent:", text)

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
		actions, err := planner.PlanActions(text, visionContext, uiaContext, history)
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
