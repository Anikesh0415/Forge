
Add-Type -AssemblyName System.Windows.Forms
$balloon = New-Object System.Windows.Forms.NotifyIcon
$balloon.Icon = [System.Drawing.SystemIcons]::Information
$balloon.BalloonTipIcon = "Info"
$balloon.BalloonTipText = "Task achieved successfully!"
$balloon.BalloonTipTitle = "Forge Complete"
$balloon.Visible = $true
$balloon.ShowBalloonTip(2000)
Start-Sleep -Seconds 3
$balloon.Dispose()
