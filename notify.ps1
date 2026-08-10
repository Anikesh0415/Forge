
Add-Type -AssemblyName System.Windows.Forms
$balloon = New-Object System.Windows.Forms.NotifyIcon
$balloon.Icon = [System.Drawing.SystemIcons]::Information
$balloon.BalloonTipIcon = "Info"
$balloon.BalloonTipText = "🔴 Started recording macro... Press Ctrl+Shift+R to stop."
$balloon.BalloonTipTitle = "Forge Recorder"
$balloon.Visible = $true
$balloon.ShowBalloonTip(2000)
Start-Sleep -Seconds 3
$balloon.Dispose()
