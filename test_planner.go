package main

import (
	"fmt"
	"forge/pkg/planner"
)

func main() {
	prompts := []string{
		"click the login button",
		"type mypassword in the password field",
		"open notepad",
		"search for dogs on google",
		"play the video on screen",
		"close the current window",
		"scroll down",
		"click the send button",
		"minimize chrome",
		"type 'hello world' in search bar",
	}

	successCount := 0
	totalTests := 59

	for i := 0; i < totalTests; i++ {
		// Cycle through our base prompts
		p := prompts[i%len(prompts)] + fmt.Sprintf(" (iteration %d)", i)
		
		fmt.Printf("Test %d/%d: %s\n", i+1, totalTests, p)
		
		// Mock Vision and UIA context to simulate what Moondream/Windows sees
		mockVision := "A browser window showing a login screen."
		mockUIA := `[{"name": "login button", "type": "button", "x": 500, "y": 600}, {"name": "password field", "type": "edit", "x": 500, "y": 500}]`
		
		actions, err := planner.PlanActions(p, mockVision, mockUIA, "[]")
		if err != nil {
			fmt.Printf("  [FAILED] Error: %v\n", err)
		} else {
			fmt.Printf("  [SUCCESS] Generated %d actions: %+v\n", len(actions), actions)
			successCount++
		}
	}
	
	fmt.Printf("\n--- TEST COMPLETE ---\n")
	fmt.Printf("Total Success: %d / %d (%.2f%%)\n", successCount, totalTests, float64(successCount)/float64(totalTests)*100)
}
