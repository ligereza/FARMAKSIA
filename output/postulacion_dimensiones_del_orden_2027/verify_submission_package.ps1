[CmdletBinding()]
param(
    [string]$PackageDir = '',
    [switch]$DocumentsOnly
)

$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($PackageDir)) {
    $PackageDir = Split-Path -Parent $MyInvocation.MyCommand.Path
}
$failures = New-Object System.Collections.Generic.List[string]

function Require-File([string]$Name) {
    $path = Join-Path $PackageDir $Name
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        $failures.Add("missing file: $Name")
    }
    return $path
}

$required = @(
    '01_project_proposal.md',
    '02_experimental_method.md',
    '03_evidence_register.md',
    '05_admissibility_gate.md',
    '06_treatment_rewrite.md',
    '10_scientific_references.md',
    '15_fup_copy_blocks.md',
    '16_budget_form_reconciled_draft.md',
    '19_final_submission_sequence.md',
    '20_curriculum_evidence_map.md',
    '21_applicant_closure_sheet.md'
)
if (-not $DocumentsOnly) {
    $required += @(
    'submission_treatment.pdf',
    'submission_experimental_method.pdf',
    'submission_budget_reconciled.pdf',
    'submission_complementary_1920x1080.mp4'
    )
}

$paths = @{}
foreach ($name in $required) {
    $paths[$name] = Require-File $name
}

$maxBytes = 100MB
foreach ($name in @('submission_treatment.pdf', 'submission_experimental_method.pdf', 'submission_budget_reconciled.pdf', 'submission_complementary_1920x1080.mp4')) {
    if ($DocumentsOnly) { continue }
    if (Test-Path -LiteralPath $paths[$name]) {
        if ((Get-Item -LiteralPath $paths[$name]).Length -ge $maxBytes) {
            $failures.Add("file exceeds 100 MB: $name")
        }
    }
}

$coreNames = @('01_project_proposal.md', '02_experimental_method.md', '06_treatment_rewrite.md', '15_fup_copy_blocks.md', '16_budget_form_reconciled_draft.md', '19_final_submission_sequence.md')
$forbidden = @(
    'miracles_star_web\.py.{0,80}989 lines',
    '989 lines.{0,80}miracles_star_web\.py',
    'four or six.{0,80}synchron',
    'already synchronized'
)
foreach ($name in $coreNames) {
    $path = $paths[$name]
    if (Test-Path -LiteralPath $path) {
        $lines = Get-Content -LiteralPath $path
        foreach ($line in $lines) {
            $isWarning = $line -match '(?i)stale|earlier|must not|do not|not be|not demonstrate|not completed'
            if (-not $isWarning) {
                foreach ($pattern in $forbidden) {
                    if ($line -match $pattern) {
                        $failures.Add("stale or overstated claim in $name matching: $pattern")
                    }
                }
            }
        }
    }
}

$ffprobe = Get-Command ffprobe -ErrorAction SilentlyContinue
if (-not $DocumentsOnly -and $ffprobe -and (Test-Path -LiteralPath $paths['submission_complementary_1920x1080.mp4'])) {
    $probeJson = & $ffprobe.Source -v error -show_entries 'stream=width,height,nb_frames,r_frame_rate:format=duration' -of json -- $paths['submission_complementary_1920x1080.mp4']
    if ($LASTEXITCODE -ne 0) { throw 'ffprobe failed to read the complementary video' }
    $probe = $probeJson | ConvertFrom-Json
    $video = @($probe.streams | Where-Object { $_.width -and $_.height } | Select-Object -First 1)
    if (-not $video -or $video.width -ne 1920 -or $video.height -ne 1080) {
        $failures.Add('complementary video is not 1920x1080')
    }
    $duration = [double]$probe.format.duration
    if ($duration -le 0 -or $duration -gt 300) {
        $failures.Add("complementary video exceeds 5 minutes: $duration seconds")
    }
} elseif (-not $DocumentsOnly) {
    $failures.Add('video inspection unavailable; ffprobe and a readable video are required')
}

$pdfinfo = Get-Command pdfinfo -ErrorAction SilentlyContinue
if (-not $DocumentsOnly -and $pdfinfo -and (Test-Path -LiteralPath $paths['submission_treatment.pdf'])) {
    $pdfOutput = & $pdfinfo.Source -- $paths['submission_treatment.pdf']
    if ($LASTEXITCODE -ne 0) { throw 'pdfinfo failed to read the treatment' }
    $pageMatch = [regex]::Match(($pdfOutput -join "`n"), '(?m)^Pages:\s+(\d+)')
    if (-not $pageMatch.Success) {
        $failures.Add('pdfinfo did not return the treatment page count')
    } elseif ([int]$pageMatch.Groups[1].Value -gt 20) {
        $failures.Add("treatment exceeds 20 pages: $($pageMatch.Groups[1].Value)")
    }
} elseif (-not $DocumentsOnly) {
    $failures.Add('PDF inspection unavailable; pdfinfo and a readable treatment are required')
}

if ($failures.Count -gt 0) {
    Write-Output 'SUBMISSION_PACKAGE_FAIL'
    $failures | ForEach-Object { Write-Output "- $_" }
    exit 1
}

if ($DocumentsOnly) {
    Write-Output 'SUBMISSION_DOCUMENTS_PASS'
    Write-Output 'Text files only. Private media and rendered PDFs were not verified.'
} else {
    Write-Output 'SUBMISSION_PACKAGE_PASS'
}
Write-Output 'Local file checks only; not an eligibility, rights or official submission certification.'
exit 0
