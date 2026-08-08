package main

import (
	"fmt"
	"os"
	"os/exec"
	"strings"

	"forge/pkg/executor"
	"forge/pkg/planner"
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

	// 2. Capture Vision Context (Moondream)
	fmt.Println("Capturing screen and analyzing via Moondream...")
	visionContext, err := vision.CaptureAndAnalyze()
	if err != nil {
		fmt.Printf("Vision failed: %v\n", err)
		// We can gracefully fallback to no context if vision fails, but let's pass empty for now.
		visionContext = "Screen context unavailable."
	}
	fmt.Println("Vision Context:", visionContext)

	// 3. Plan Actions (JSON LLM)
	fmt.Println("Planning actions...")
	actions, err := planner.PlanActions(text, visionContext)
	if err != nil {
		fmt.Printf("Planner failed: %v\n", err)
		return
	}
	fmt.Printf("Generated Plan: %+v\n", actions)

	// 4. Execute Actions
	fmt.Println("Executing...")
	executor.ExecutePlan(actions)
	fmt.Println("Done!")
}
