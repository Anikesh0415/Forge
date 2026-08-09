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
	
	skills.LoadLearnedSkills()

	for {
		handleSummon()
	}
}

func handleSummon() {
	// 1. Pop up native WPF Input Box
	ps1Script := `
Add-Type -AssemblyName PresentationFramework
$xaml = @"
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="Forge" Width="600" Height="60" 
        WindowStyle="None" AllowsTransparency="True" Background="Transparent"
        WindowStartupLocation="CenterScreen" Topmost="True">
    <Border CornerRadius="15" Background="#CC111111" BorderBrush="#33FFFFFF" BorderThickness="1" Margin="5">
        <Grid Margin="10,0,10,0">
            <TextBlock Name="Placeholder" Text="What do you want to automate?" Foreground="#66FFFFFF" FontSize="22" 
                       VerticalAlignment="Center" Margin="10,0,0,0" IsHitTestVisible="False" FontFamily="Segoe UI" FontWeight="Light"/>
            <TextBox Name="InputBox" Margin="5,0,5,0" Background="Transparent" Foreground="White" CaretBrush="White"
                     BorderThickness="0" FontSize="22" VerticalAlignment="Center" FontFamily="Segoe UI" FontWeight="Light"/>
        </Grid>
    </Border>
</Window>
"@
$reader = (New-Object System.Xml.XmlNodeReader ([xml]$xaml))
$win = [Windows.Markup.XamlReader]::Load($reader)
$inputBox = $win.FindName("InputBox")
$placeholder = $win.FindName("Placeholder")

$win.Add_Loaded({ $inputBox.Focus() })
$inputBox.Add_TextChanged({
    if ($inputBox.Text -eq "") {
        $placeholder.Visibility = 'Visible'
    } else {
        $placeholder.Visibility = 'Hidden'
    }
})
$inputBox.Add_KeyDown({
    if ($_.Key -eq 'Enter') {
        [Console]::Out.WriteLine($inputBox.Text)
        $win.Close()
    }
    if ($_.Key -eq 'Escape') {
        $win.Close()
    }
})
$win.ShowDialog() | Out-Null
`
	os.WriteFile("input.ps1", []byte(ps1Script), 0644)
	cmd := exec.Command("powershell", "-ExecutionPolicy", "Bypass", "-File", "input.ps1")
	cmd.SysProcAttr = &syscall.SysProcAttr{HideWindow: true}
	out, err := cmd.Output()
	if err != nil {
		return
	}

	intent := strings.TrimSpace(string(out))
	if intent == "" {
		os.Exit(0)
	}

	intent = strings.TrimSpace(strings.ToLower(intent))
	if intent == "exit" || intent == "quit" {
		os.Exit(0)
	}
	
	isLearningMode := false
	if strings.HasPrefix(intent, "learn ") {
		isLearningMode = true
		intent = strings.TrimSpace(strings.TrimPrefix(intent, "learn "))
		if strings.HasPrefix(intent, "how to ") {
			intent = strings.TrimSpace(strings.TrimPrefix(intent, "how to "))
		}
		fmt.Printf("Learning Mode activated for: '%s'\n", intent)
	}
	fmt.Printf("User Intent: %s\n\n", intent)

	if !isLearningMode {
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
	}

	history := "[]"
	var allActions []executor.Action
	var lastUiaContext string

	// DYNAMIC AI ORCHESTRATOR (Fallback)
	for step := 1; step <= 15; step++ {
		fmt.Printf("\n--- Step %d ---\n", step)
		
		notifyUser("Forge Orchestrator", fmt.Sprintf("Step %d: Analyzing screen...", step))
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
		
		// Context Memory: Check if the screen actually changed after the last action
		if step > 1 && uiaContext == lastUiaContext {
			history += "\nFAILED: Screen unchanged. The last action did not work. Try a different element."
			notifyUser("Forge Error", "Action failed, retrying...")
		}
		lastUiaContext = uiaContext

		fmt.Println("Planning actions...")
		actions, err := planner.PlanActions(intent, visionContext, uiaContext, history)
		if err != nil {
			fmt.Printf("Planner failed: %v\n", err)
			notifyUser("Forge Error", "Failed to plan action.")
			return
		}
		
		fmt.Printf("Generated Plan: %+v\n", actions)

		// SAFEGUARD CHECK
		if !checkSafeguards(actions) {
			fmt.Println("Safeguard triggered: User denied permission for high-risk action. Aborting.")
			notifyUser("Forge Security", "Action aborted by user.")
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
			notifyUser("Forge Executor", fmt.Sprintf("Step %d: Executing %s", step, executedThisStep[0].Type))
			fmt.Println("Executing...")
			executor.ExecutePlan(executedThisStep)
			allActions = append(allActions, executedThisStep...)
			
			historyBytes, _ := json.Marshal(allActions)
			history = string(historyBytes)
		}

		if isDone {
			fmt.Println("Intent fully achieved. Exiting loop.")
			notifyUser("Forge Complete", "Task achieved successfully!")
			if isLearningMode {
				saveLearnedSkill(intent, allActions)
			}
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

func notifyUser(title, message string) {
	ps1 := fmt.Sprintf(`
Add-Type -AssemblyName System.Windows.Forms
$balloon = New-Object System.Windows.Forms.NotifyIcon
$balloon.Icon = [System.Drawing.SystemIcons]::Information
$balloon.BalloonTipIcon = "Info"
$balloon.BalloonTipText = "%s"
$balloon.BalloonTipTitle = "%s"
$balloon.Visible = $true
$balloon.ShowBalloonTip(2000)
Start-Sleep -Seconds 3
$balloon.Dispose()
`, message, title)
	os.WriteFile("notify.ps1", []byte(ps1), 0644)
	cmd := exec.Command("powershell", "-ExecutionPolicy", "Bypass", "-File", "notify.ps1")
	cmd.SysProcAttr = &syscall.SysProcAttr{HideWindow: true}
	cmd.Start() // run asynchronously
}

func saveLearnedSkill(intent string, actions []executor.Action) {
	os.Mkdir("skills_db", 0755)
	safeName := strings.ReplaceAll(intent, " ", "_")
	
	skill := skills.DynamicSkill{
		SkillName: intent,
		Actions:   actions,
	}
	
	data, _ := json.MarshalIndent(skill, "", "  ")
	os.WriteFile(fmt.Sprintf("skills_db/learned_%s.json", safeName), data, 0644)
	fmt.Printf("Successfully learned and saved skill: %s\n", intent)
	notifyUser("Forge Learn", fmt.Sprintf("Learned new skill: %s", intent))
}
