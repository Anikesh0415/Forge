
Add-Type -AssemblyName PresentationFramework
$xaml = @"
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="Forge 2.5" Width="800" Height="80" 
        WindowStyle="None" AllowsTransparency="True" Background="#D9000000"
        WindowStartupLocation="CenterScreen" Topmost="True">
    <Grid>
        <TextBox Name="InputBox" Margin="20,10" Background="Transparent" Foreground="White" 
                 BorderThickness="0" FontSize="32" HorizontalAlignment="Stretch" VerticalAlignment="Center" />
    </Grid>
</Window>
"@
$reader = (New-Object System.Xml.XmlNodeReader ([xml]$xaml))
$win = [Windows.Markup.XamlReader]::Load($reader)
$inputBox = $win.FindName("InputBox")
$win.Add_Loaded({ $inputBox.Focus() })
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
