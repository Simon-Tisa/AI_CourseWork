param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$PythonArgs
)

$TorchPython = "C:\ProgramData\Anaconda\envs\torch\python.exe"
$EnvRoot = "C:\ProgramData\Anaconda\envs\torch"
$FallbackPython = "python"
$OriginalPath = $env:PATH

if (Test-Path -LiteralPath $TorchPython) {
    $env:PATH = "$EnvRoot;$EnvRoot\Library\mingw-w64\bin;$EnvRoot\Library\usr\bin;$EnvRoot\Library\bin;$EnvRoot\Scripts;" + $env:PATH
    & $TorchPython @PythonArgs
    if ($LASTEXITCODE -eq 0) {
        exit 0
    }
    Write-Warning "Preferred torch interpreter exited with code $LASTEXITCODE. Falling back to another Python interpreter."
    $env:PATH = $OriginalPath
}

& $FallbackPython @PythonArgs
exit $LASTEXITCODE
