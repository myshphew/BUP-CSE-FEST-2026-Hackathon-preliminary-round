param([Parameter(Mandatory=$true)][string]$Manifest)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$voice = New-Object System.Speech.Synthesis.SpeechSynthesizer
try {
    $voice.SelectVoice('Microsoft David Desktop')
    $voice.Rate = 3
    $items = Get-Content -LiteralPath $Manifest -Raw | ConvertFrom-Json
    foreach ($item in $items) {
        $voice.SetOutputToWaveFile($item.audio)
        $voice.Speak($item.narration)
        $voice.SetOutputToNull()
    }
} finally {
    $voice.Dispose()
}
