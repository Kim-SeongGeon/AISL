$ErrorActionPreference = 'Stop'
$experimentScript = Join-Path $PSScriptRoot 'experiment.py'
$experimentRuntime = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
if (Test-Path -LiteralPath $experimentRuntime) {
    & $experimentRuntime $experimentScript @args
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 $experimentScript @args
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    & python $experimentScript @args
} else {
    throw 'Python 3 is required. Install Python 3 and run: python experiment.py'
}
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
