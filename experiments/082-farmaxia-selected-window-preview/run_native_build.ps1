param([switch]$BuildOnly)

$ErrorActionPreference = 'Stop'
$experimentRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$nativeRoot = Join-Path $experimentRoot 'native'
$packageVersion = '2.0.221121.5'
$packageName = "Microsoft.Windows.CppWinRT.$packageVersion"
$packagePath = Join-Path $nativeRoot "packages\\$packageName"
$propsPath = Join-Path $packagePath 'build\\native\\Microsoft.Windows.CppWinRT.props'
if (-not (Test-Path -LiteralPath $propsPath)) {
    $archive = Join-Path $env:TEMP "$packageName.nupkg"
    $archiveZip = Join-Path $env:TEMP "$packageName.zip"
    if (-not (Test-Path -LiteralPath $archive)) {
        Invoke-WebRequest -Uri "https://api.nuget.org/v3-flatcontainer/microsoft.windows.cppwinrt/$packageVersion/microsoft.windows.cppwinrt.$packageVersion.nupkg" -OutFile $archive
    }
    Copy-Item -LiteralPath $archive -Destination $archiveZip -Force
    New-Item -ItemType Directory -Path (Split-Path -Parent $packagePath) -Force | Out-Null
    Expand-Archive -LiteralPath $archiveZip -DestinationPath $packagePath
}
$vsDev = 'C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\Tools\VsDevCmd.bat'
if (-not (Test-Path -LiteralPath $vsDev)) { throw 'Visual Studio 2022 Community build tools were not found.' }
$project = Join-Path $nativeRoot '082-selected-window-preview.vcxproj'
$compile = 'call "' + $vsDev + '" -arch=x64 -host_arch=x64 && msbuild "' + $project + '" /t:Build /p:Configuration=Release /p:Platform=x64 /p:RestorePackages=false /m:1 /v:minimal'
& $env:ComSpec /d /s /c $compile
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
$binary = Join-Path $nativeRoot 'x64\Release\082-selected-window-preview.exe'
if ($BuildOnly) {
    Write-Output "FARMAXIA_082_BUILD_VALID"
    exit 0
}
& $binary
exit $LASTEXITCODE
