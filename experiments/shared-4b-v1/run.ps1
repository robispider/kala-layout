[CmdletBinding()]
param(
    [switch]$Resume,
    [switch]$CheckOnly
)

$ErrorActionPreference = 'Stop'
$experimentDirectory = [System.IO.Path]::GetFullPath($PSScriptRoot)
$repositoryDirectory = [System.IO.Path]::GetFullPath((Join-Path $experimentDirectory '..\..'))
$setupPath = Join-Path $experimentDirectory 'setup-manifest.json'
$presetPath = Join-Path $experimentDirectory 'preset.json'
$setup = Get-Content -LiteralPath $setupPath -Raw -Encoding UTF8 | ConvertFrom-Json

function Assert-ExpectedHash {
    param([string]$RelativePath, [string]$Expected)
    $checkedPath = [System.IO.Path]::GetFullPath((Join-Path $repositoryDirectory $RelativePath))
    $repositoryPrefix = $repositoryDirectory.TrimEnd('\') + '\'
    if (-not $checkedPath.StartsWith($repositoryPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Manifest path is outside this repository: $RelativePath"
    }
    if (-not (Test-Path -LiteralPath $checkedPath -PathType Leaf)) {
        throw "Required file is missing: $RelativePath"
    }
    $observed = (Get-FileHash -LiteralPath $checkedPath -Algorithm SHA256).Hash
    if ($observed -ne $Expected) {
        throw "File changed since experiment setup: $RelativePath. Keep the frozen setup or prepare a new experiment."
    }
}

foreach ($entry in $setup.setup_file_sha256.PSObject.Properties) {
    Assert-ExpectedHash -RelativePath $entry.Name -Expected $entry.Value
}
foreach ($entry in $setup.engine_input_sha256.PSObject.Properties) {
    Assert-ExpectedHash -RelativePath $entry.Name -Expected $entry.Value
}

$preset = Get-Content -LiteralPath $presetPath -Raw -Encoding UTF8 | ConvertFrom-Json
$proposalCount = [int64]$preset.track_count * [int64]$preset.seeds_per_track * [int64]$preset.steps_per_seed
if ($proposalCount -ne [int64]4000000000 -or $proposalCount -ne [int64]$preset.proposal_total) {
    throw 'Preset does not specify exactly four billion annealing proposals.'
}
if ($preset.workers -ne 32 -or $preset.track_count -ne 2) {
    throw 'This preset requires 32 workers and two tracks.'
}
$outputDirectory = [System.IO.Path]::GetFullPath((Join-Path $repositoryDirectory $preset.output))
$allowedPrefix = (Join-Path $repositoryDirectory 'results\shared-layout-relaxed-v1').TrimEnd('\') + '\'
if (-not $outputDirectory.StartsWith($allowedPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw 'Unexpected output directory in preset.'
}

$pythonCommand = Get-Command python -CommandType Application -ErrorAction Stop | Select-Object -First 1
$previousPythonPath = $env:PYTHONPATH
$previousUnbuffered = $env:PYTHONUNBUFFERED
Push-Location -LiteralPath $repositoryDirectory
try {
    $env:PYTHONPATH = Join-Path $repositoryDirectory 'src'
    $env:PYTHONUNBUFFERED = '1'
    & $pythonCommand.Source -c "import sys; assert sys.version_info >= (3,10); from bangla_dh.experimental.shared_relaxed import EFFORT_ALLOWANCE, WITHIN_ALLOWANCE; assert str(EFFORT_ALLOWANCE) == '3/400' and WITHIN_ALLOWANCE == .075"
    if ($LASTEXITCODE -ne 0) {
        throw 'Python or experiment-limit preflight failed.'
    }

    Write-Host 'Verified frozen setup, code and data inputs.'
    Write-Host 'Budget: 4,000,000,000 annealing proposals, plus local search.'
    Write-Host 'Tracks: 10,000 starts each; 200,000 proposals per start; 32 workers.'
    Write-Host 'Limits: +0.75% effort and +7.5% within-word movement per mode.'
    Write-Host "Output: $outputDirectory"
    if ($CheckOnly) {
        Write-Host 'Check complete. No search started.'
        return
    }

    if (Test-Path -LiteralPath (Join-Path $outputDirectory 'run-manifest.json')) {
        throw 'This run is already complete. Its results will not be overwritten.'
    }
    if ($Resume) {
        if (-not (Test-Path -LiteralPath (Join-Path $outputDirectory 'search-plan.json'))) {
            throw 'No existing search plan to resume. Run without -Resume first.'
        }
    }
    elseif (Test-Path -LiteralPath $outputDirectory) {
        throw 'Output already exists. Use -Resume to continue the same run.'
    }

    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss-fff'
    $logPath = Join-Path $repositoryDirectory "work\shared-4b-v1-logs\run-$stamp-$PID.log"
    & $pythonCommand.Source -c "import sys; from bangla_dh.paths import output_path; output_path(sys.argv[1])" $logPath
    if ($LASTEXITCODE -ne 0) {
        throw 'Could not validate the log output path.'
    }
    $engineArguments = @(
        '-u', '-m', [string]$preset.engine,
        '--out', [string]$preset.output,
        '--seeds', [string]$preset.seeds_per_track,
        '--steps', [string]$preset.steps_per_seed,
        '--ils-iterations', [string]$preset.ils_iterations,
        '--workers', [string]$preset.workers,
        '--first-seed', [string]$preset.first_seed,
        '--archive-limit', [string]$preset.archive_limit,
        '--frontier-limit', [string]$preset.frontier_limit,
        '--balance-refine-steps', [string]$preset.balance_refine_steps
    )
    if ($Resume) { $engineArguments += '--resume' }
    Write-Host "Terminal log: $logPath"
    Write-Host 'Completed starts are checkpointed. After interruption, repeat this runner with -Resume.'

    # Native stderr is included in the log. The Python exit code decides success.
    $previousErrorPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        & $pythonCommand.Source @engineArguments 2>&1 | Tee-Object -FilePath $logPath
        $engineExitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousErrorPreference
    }
    if ($engineExitCode -ne 0) {
        throw "Search exited with code $engineExitCode. Completed checkpoints and the terminal log are preserved."
    }
}
finally {
    Pop-Location
    $env:PYTHONPATH = $previousPythonPath
    $env:PYTHONUNBUFFERED = $previousUnbuffered
}
