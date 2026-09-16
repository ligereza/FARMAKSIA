$ErrorActionPreference = "Stop"

$repo = "C:\IA\FARMAXIA"
$blender = "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"
$blendFile = Join-Path $repo "experiments\085-vizz-blender-focus-distance\output\vizz_focus_distance.blend"
$bridgeFile = Join-Path $repo "experiments\086-vizz-blender-live-distance-bridge\blender_live_bridge.py"
$runnerFile = Join-Path $repo "experiments\086-vizz-blender-live-distance-bridge\run_live_distance.py"
$python = Join-Path $repo ".venv\Scripts\python.exe"

foreach ($required in @($blender, $blendFile, $bridgeFile, $runnerFile, $python)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "No se encontró: $required"
    }
}

$blenderProcess = $null
$workerProcess = $null
try {
    $blenderProcess = Start-Process -FilePath $blender `
        -ArgumentList @($blendFile, "--python", $bridgeFile) `
        -WorkingDirectory $repo `
        -PassThru

    Start-Sleep -Seconds 5

    $workerProcess = Start-Process -FilePath $python `
        -ArgumentList @($runnerFile, "--sample-hz", "5", "--focus-mode", "locked", "--no-trace") `
        -WorkingDirectory $repo `
        -WindowStyle Hidden `
        -PassThru

    Write-Host "VIZZ activo: Blender + tracker CUDA a 5 Hz, sin limite de tiempo."
    Write-Host "En la ventana de camara, espera ROSTRO + 2 OJOS OK y pulsa ESPACIO."
    Write-Host "Cierra Blender para detener tambien el tracker."

    Wait-Process -Id $blenderProcess.Id
}
finally {
    if ($workerProcess -and -not $workerProcess.HasExited) {
        Stop-Process -Id $workerProcess.Id -Force -ErrorAction SilentlyContinue
    }
}
