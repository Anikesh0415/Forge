
Add-Type -AssemblyName PresentationFramework
$xaml = @"
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="Forge" Width="450" Height="46" 
        WindowStyle="None" AllowsTransparency="True" Background="Transparent"
        WindowStartupLocation="CenterScreen" Topmost="True">
    <Border CornerRadius="22" Background="#CC000000" BorderBrush="#33FFFFFF" BorderThickness="1" Margin="2">
        <Grid Margin="15,0,10,0">
            <Grid.ColumnDefinitions>
                <ColumnDefinition Width="*" />
                <ColumnDefinition Width="Auto" />
            </Grid.ColumnDefinitions>
            <TextBlock Name="Placeholder" Grid.Column="0" Text="What do you want to automate?" Foreground="#88FFFFFF" FontSize="16" 
                       VerticalAlignment="Center" Margin="5,0,0,0" IsHitTestVisible="False" FontFamily="Segoe UI" FontWeight="Light"/>
            <TextBox Name="InputBox" Grid.Column="0" Margin="3,0,5,0" Padding="0,0,0,0" Background="Transparent" Foreground="White" CaretBrush="White"
                     BorderThickness="0" FontSize="16" VerticalAlignment="Center" FontFamily="Segoe UI" FontWeight="Light"/>
            <StackPanel Grid.Column="1" Orientation="Horizontal" VerticalAlignment="Center">
                <Button Name="MinimizeBtn" Content=" _ " Foreground="White" Background="Transparent" BorderThickness="0" FontSize="12" Margin="0,0,8,0" Cursor="Hand" ToolTip="Minimize"/>
                <Button Name="CloseBtn" Content=" X " Foreground="White" Background="Transparent" BorderThickness="0" FontSize="12" Cursor="Hand" ToolTip="Close"/>
            </StackPanel>
        </Grid>
    </Border>
</Window>
"@
$reader = (New-Object System.Xml.XmlNodeReader ([xml]$xaml))
$win = [Windows.Markup.XamlReader]::Load($reader)
$inputBox = $win.FindName("InputBox")
$placeholder = $win.FindName("Placeholder")
$minBtn = $win.FindName("MinimizeBtn")
$closeBtn = $win.FindName("CloseBtn")

$win.Add_MouseLeftButtonDown({ $win.DragMove() })
$minBtn.Add_Click({ $win.WindowState = 'Minimized' })
$closeBtn.Add_Click({ $win.Close() })

$win.Add_Loaded({ 
    $win.Top = 15
    $inputBox.Focus() 
})
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
