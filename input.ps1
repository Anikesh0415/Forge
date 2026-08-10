
Add-Type -AssemblyName PresentationFramework
$xaml = @"
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="Forge" Width="600" Height="60" 
        WindowStyle="None" AllowsTransparency="True" Background="Transparent"
        WindowStartupLocation="CenterScreen" Topmost="True">
    <Border CornerRadius="15" Background="#CC111111" BorderBrush="#33FFFFFF" BorderThickness="1" Margin="5">
        <Grid Margin="10,0,10,0">
            <Grid.ColumnDefinitions>
                <ColumnDefinition Width="*" />
                <ColumnDefinition Width="Auto" />
            </Grid.ColumnDefinitions>
            <TextBlock Name="Placeholder" Grid.Column="0" Text="What do you want to automate?" Foreground="#66FFFFFF" FontSize="22" 
                       VerticalAlignment="Center" Margin="10,0,0,0" IsHitTestVisible="False" FontFamily="Segoe UI" FontWeight="Light"/>
            <TextBox Name="InputBox" Grid.Column="0" Margin="5,0,5,0" Background="Transparent" Foreground="White" CaretBrush="White"
                     BorderThickness="0" FontSize="22" VerticalAlignment="Center" FontFamily="Segoe UI" FontWeight="Light"/>
            <StackPanel Grid.Column="1" Orientation="Horizontal" VerticalAlignment="Center">
                <Button Name="MinimizeBtn" Content=" _ " Foreground="White" Background="Transparent" BorderThickness="0" FontSize="16" Margin="0,0,10,0" Cursor="Hand" ToolTip="Minimize"/>
                <Button Name="CloseBtn" Content=" X " Foreground="White" Background="Transparent" BorderThickness="0" FontSize="14" Cursor="Hand" ToolTip="Close"/>
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
