param(
    [int]$Fixtures = 5
)

$ErrorActionPreference = "Stop"
$Package = Split-Path -Parent $MyInvocation.MyCommand.Path
$Farmaxia = (Resolve-Path (Join-Path $Package "..\..")).Path
$Runner = Join-Path $Farmaxia "experiments\obras-experimental-rehearsal\run_rehearsal.py"
$Fixture = Join-Path $Farmaxia "experiments\obras-experimental-rehearsal\fixture-synthetic-audio.json"
$Output = Join-Path $Package "run-output"

python $Runner `
    --fixture $Fixture `
    --output $Output `
    --xio-root "C:\IA\XIO" `
    --mosaik-root "C:\IA\VJ" `
    --fixtures $Fixtures

Write-Host "Evidence written to: $Output"
Write-Host "Open manually: $(Join-Path $Output 'visualization.html')"
