using System;
using System.Text;
using System.Windows.Automation;
using System.Collections.Generic;

public class UIADumper {
    [STAThread]
    public static void Main() {
        var desktop = AutomationElement.RootElement;
        var cond = new PropertyCondition(AutomationElement.IsOffscreenProperty, false);
        var elements = desktop.FindAll(TreeScope.Subtree, cond);
        
        StringBuilder sb = new StringBuilder();
        foreach (AutomationElement e in elements) {
            try {
                if (e.Current.BoundingRectangle.Width > 0 && e.Current.BoundingRectangle.Height > 0) {
                    if (!string.IsNullOrEmpty(e.Current.Name)) {
                        Console.WriteLine(e.Current.Name);
                    }
                }
            } catch {}
        }
    }
}
