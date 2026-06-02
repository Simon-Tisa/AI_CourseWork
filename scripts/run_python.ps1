param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Args
)

$TorchPython = "C:\ProgramData\Anaconda\envs\torch\python.exe"
$EnvRoot = "C:\ProgramData\Anaconda\envs\torch"
$FallbackPython = "python"
$CodexPython = "C:\Users\蔡雪峰\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

if (Test-Path -LiteralPath $TorchPython) {
    $env:PATH = "$EnvRoot;$EnvRoot\Library\mingw-w64\bin;$EnvRoot\Library\usr\bin;$EnvRoot\Library\bin;$EnvRoot\Scripts;" + $env:PATH
    & $TorchPython @Args
    if ($LASTEXITCODE -eq 0) {
        exit 0
    }
    Write-Warning "Preferred torch interpreter exited with code $LASTEXITCODE. Falling back to another Python interpreter."
}

if (Test-Path -LiteralPath $CodexPython) {
    & $CodexPython @Args
    exit $LASTEXITCODE
}

& $FallbackPython @Args
exit $LASTEXITCODE
