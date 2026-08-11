
Add-Type -AssemblyName System.Windows.Forms
$balloon = New-Object System.Windows.Forms.NotifyIcon
$balloon.Icon = [System.Drawing.SystemIcons]::Information
$balloon.BalloonTipIcon = "Info"
$balloon.BalloonTipText = "✅ Saved macro: opening brave and searching for NCERT chapter , downloading chapter attaching it to gemini,asing gemini to summarize it copying the generated text and opening notepad and pasting the text and saving the document"
$balloon.BalloonTipTitle = "Forge Recorder"
$balloon.Visible = $true
$balloon.ShowBalloonTip(2000)
Start-Sleep -Seconds 3
$balloon.Dispose()
