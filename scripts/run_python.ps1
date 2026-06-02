param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Args
)

$TorchPython = "C:\ProgramData\Anaconda\envs\torch\python.exe"
$EnvRoot = "C:\ProgramData\Anaconda\envs\torch"
$FallbackPython = "python"

if (Test-Path -LiteralPath $TorchPython) {
    $env:PATH = "$EnvRoot;$EnvRoot\Library\mingw-w64\bin;$EnvRoot\Library\usr\bin;$EnvRoot\Library\bin;$EnvRoot\Scripts;" + $env:PATH
    & $TorchPython @Args
    exit $LASTEXITCODE
}

& $FallbackPython @Args
exit $LASTEXITCODE
