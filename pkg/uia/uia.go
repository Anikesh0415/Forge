package uia

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"syscall"
)

const csSource = `
using System;
using System.Text;
using System.Windows.Automation;
using System.Collections.Generic;

public class UIADumper {
    public static void Main() {
        var desktop = AutomationElement.RootElement;
        var cond = new PropertyCondition(AutomationElement.IsOffscreenProperty, false);
        var elements = desktop.FindAll(TreeScope.Subtree, cond);
        
        StringBuilder sb = new StringBuilder();
        sb.Append("[");
        bool first = true;
        foreach (AutomationElement e in elements) {
            try {
                if (e.Current.BoundingRectangle.Width > 0 && e.Current.BoundingRectangle.Height > 0) {
                    if (!string.IsNullOrEmpty(e.Current.Name) || e.Current.ControlType != ControlType.Pane) {
                        if (!first) sb.Append(",");
                        first = false;
                        
                        string name = e.Current.Name.Replace("\"", "\\\"").Replace("\n", " ");
                        string ctype = e.Current.ControlType.ProgrammaticName.Replace("ControlType.", "");
                        var rect = e.Current.BoundingRectangle;
                        int centerX = (int)(rect.Left + (rect.Width / 2));
                        int centerY = (int)(rect.Top + (rect.Height / 2));
                        
                        sb.Append("{\"name\":\"" + name + "\",");
                        sb.Append("\"type\":\"" + ctype + "\",");
                        sb.Append(string.Format("\"x\":{0},\"y\":{1}", centerX, centerY));
                        sb.Append("}");
                    }
                }
            } catch {}
        }
        sb.Append("]");
        Console.WriteLine(sb.ToString());
    }
}
`

func DumpUI() (string, error) {
	exePath := "uia_dumper.exe"

	if _, err := os.Stat(exePath); os.IsNotExist(err) {
		// Compile it
		csPath := "uia_dumper.cs"
		if err := os.WriteFile(csPath, []byte(csSource), 0644); err != nil {
			return "", err
		}
		defer os.Remove(csPath)

		cscPath := filepath.Join(os.Getenv("WINDIR"), `Microsoft.NET\Framework64\v4.0.30319\csc.exe`)
		wpfPath := filepath.Join(os.Getenv("WINDIR"), `Microsoft.NET\Framework64\v4.0.30319\WPF`)
		refStr := fmt.Sprintf("/reference:%s,%s,%s", filepath.Join(wpfPath, "UIAutomationClient.dll"), filepath.Join(wpfPath, "UIAutomationTypes.dll"), filepath.Join(wpfPath, "WindowsBase.dll"))
		cmd := exec.Command(cscPath, "/target:exe", "/out:"+exePath, refStr, csPath)
		cmd.SysProcAttr = &syscall.SysProcAttr{HideWindow: true}
		if out, err := cmd.CombinedOutput(); err != nil {
			return "", fmt.Errorf("compile error: %v, output: %s", err, string(out))
		}
	}

	// Execute it
	cmd := exec.Command("cmd", "/c", exePath)
	cmd.SysProcAttr = &syscall.SysProcAttr{HideWindow: true}
	out, err := cmd.Output()
	if err != nil {
		return "", fmt.Errorf("uia dumper execution failed: %v", err)
	}

	// Truncate output if it's too large, but keeping it raw JSON for the LLM
	jsonStr := string(out)
	if len(jsonStr) > 4000 {
		// Just to prevent context explosion, though Qwen 2.5 has 32k context
		// We'll trust the model for now
	}

	return jsonStr, nil
}
