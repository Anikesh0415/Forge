param(
    [string]$Title = "Forge",
    [string]$Message = "",
    [string]$Step = "",
    [int]$TotalSteps = 0,
    [int]$CurrentStep = 0,
    [switch]$Persistent
)

Add-Type -AssemblyName PresentationFramework
Add-Type -AssemblyName PresentationCore
Add-Type -AssemblyName WindowsBase

# Build display text
$displayTitle = if ($Step -ne "") { $Step } else { $Title }
$displayBody  = $Message

# Show progress fraction if steps are given
$progressText = ""
if ($TotalSteps -gt 0) {
    $progressText = "[$CurrentStep/$TotalSteps]"
    $displayBody  = "$progressText $Message"
}

$xaml = @"
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="ForgeHUD"
        Width="420" SizeToContent="Height"
        WindowStyle="None"
        AllowsTransparency="True"
        Background="Transparent"
        Topmost="True"
        ShowInTaskbar="False"
        WindowStartupLocation="Manual">
  <Window.Resources>
    <Style x:Key="FadeIn" TargetType="Window">
      <Style.Triggers>
        <EventTrigger RoutedEvent="Window.Loaded">
          <BeginStoryboard>
            <Storyboard>
              <DoubleAnimation Storyboard.TargetProperty="Opacity"
                               From="0" To="1" Duration="0:0:0.25"/>
            </Storyboard>
          </BeginStoryboard>
        </EventTrigger>
      </Style.Triggers>
    </Style>
  </Window.Resources>
  <Border CornerRadius="14"
          Background="#E0111111"
          BorderBrush="#44FFFFFF"
          BorderThickness="1"
          Margin="12,12,12,12">
    <Border.Effect>
      <DropShadowEffect Color="Black" BlurRadius="22" ShadowDepth="4" Opacity="0.55"/>
    </Border.Effect>
    <StackPanel Margin="18,14,18,14">
      <!-- Header row -->
      <DockPanel LastChildFill="False" Margin="0,0,0,6">
        <Ellipse Width="8" Height="8" Fill="#00D4AA" VerticalAlignment="Center" Margin="0,0,8,0"/>
        <TextBlock Name="TitleBlock"
                   Text=""
                   Foreground="#00D4AA"
                   FontFamily="Segoe UI"
                   FontSize="12"
                   FontWeight="SemiBold"
                   VerticalAlignment="Center"/>
        <TextBlock Name="StepBadge"
                   Text=""
                   Foreground="#88FFFFFF"
                   FontFamily="Segoe UI"
                   FontSize="11"
                   VerticalAlignment="Center"
                   DockPanel.Dock="Right"/>
      </DockPanel>
      <!-- Message -->
      <TextBlock Name="MsgBlock"
                 Text=""
                 Foreground="#DDFFFFFF"
                 FontFamily="Segoe UI"
                 FontSize="14"
                 FontWeight="Light"
                 TextWrapping="Wrap"
                 Margin="0,2,0,0"/>
      <!-- Progress bar (hidden when TotalSteps == 0) -->
      <ProgressBar Name="ProgBar"
                   Height="3"
                   Margin="0,10,0,0"
                   Background="#33FFFFFF"
                   Foreground="#00D4AA"
                   BorderThickness="0"
                   Minimum="0"
                   Maximum="100"
                   Value="0"
                   Visibility="Collapsed"/>
    </StackPanel>
  </Border>
</Window>
"@

$reader = [System.Xml.XmlNodeReader]::new([xml]$xaml)
$win    = [Windows.Markup.XamlReader]::Load($reader)

$win.FindName("TitleBlock").Text = $displayTitle
$win.FindName("MsgBlock").Text   = $displayBody

# Show progress bar when steps are given
if ($TotalSteps -gt 0) {
    $bar = $win.FindName("ProgBar")
    $bar.Visibility = "Visible"
    $pct = if ($TotalSteps -gt 0) { [int](($CurrentStep / $TotalSteps) * 100) } else { 0 }
    $bar.Value = $pct
    $win.FindName("StepBadge").Text = "$CurrentStep / $TotalSteps"
}

# Position: bottom-right corner with margin
$win.Add_Loaded({
    $screen = [System.Windows.SystemParameters]::WorkArea
    $win.Left = $screen.Right  - $win.ActualWidth  - 24
    $win.Top  = $screen.Bottom - $win.ActualHeight - 24
})

if ($Persistent) {
    $win.ShowDialog() | Out-Null
} else {
    # Auto-dismiss after 3 seconds with fade-out
    $timer = [System.Windows.Threading.DispatcherTimer]::new()
    $timer.Interval = [TimeSpan]::FromMilliseconds(2500)
    $timer.Add_Tick({
        $timer.Stop()
        # Fade out
        $anim = [System.Windows.Media.Animation.DoubleAnimation]::new()
        $anim.From     = 1.0
        $anim.To       = 0.0
        $anim.Duration = [System.Windows.Duration]::new([TimeSpan]::FromMilliseconds(300))
        $anim.Add_Completed({ $win.Close() })
        $win.BeginAnimation([System.Windows.Window]::OpacityProperty, $anim)
    })
    $win.Add_Loaded({ $timer.Start() })
    $win.ShowDialog() | Out-Null
}
