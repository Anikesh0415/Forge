
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
%!(EXTRA string=Failed to plan action., string=Forge Error)