# Read-only environment inventory. Compatible with Windows PowerShell 5.1+.
[CmdletBinding()]
param(
    [string]$Python,
    [switch]$SkipPythonPackages
)

$ErrorActionPreference = 'Stop'
$missingCLI = @()
$pythonExe = $null
$pythonArgs = @()
$pythonFound = $false
$wingetIds = @{
    jq = 'jqlang.jq'; gh = 'GitHub.cli'; rg = 'BurntSushi.ripgrep.MSVC'
    fd = 'sharkdp.fd'; ffmpeg = 'Gyan.FFmpeg'; bat = 'sharkdp.bat'; uv = 'astral-sh.uv'
}

function Find-Application([string]$Name) {
    Get-Command $Name -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
}

function Check-CLI([string]$Name, [string[]]$Candidates, [string]$VersionArg = '--version') {
    $found = $null
    foreach ($candidate in $Candidates) {
        $found = Find-Application $candidate
        if ($found) { break }
    }
    if (-not $found) {
        Write-Output "[MISSING] $Name"
        $script:missingCLI += $Name
        return
    }
    try {
        $result = & $found.Source $VersionArg 2>$null
        if ($LASTEXITCODE -eq 0) {
            $first = $result | Select-Object -First 1
            Write-Output "[OK] $Name $first ($($found.Source))"
        } else {
            Write-Output "[UNKNOWN] $Name found, version probe failed: exit $LASTEXITCODE ($($found.Source))"
        }
    } catch {
        Write-Output "[UNKNOWN] $Name found, version probe failed ($($found.Source))"
    }
}

Write-Output '=== CLI tools (inventory, not mandatory dependencies) ==='
$pythonCandidates = if ($Python) { @($Python) } else { @('python', 'python3', 'py') }
foreach ($candidate in $pythonCandidates) {
    $found = Find-Application $candidate
    if (-not $found) { continue }
    $pythonFound = $true
    $prefix = if (([IO.Path]::GetFileNameWithoutExtension($found.Source)) -eq 'py') { @('-3') } else { @() }
    try {
        $result = & $found.Source @prefix --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            $pythonExe = $found.Source
            $pythonArgs = $prefix
            Write-Output "[OK] python $($result | Select-Object -First 1) ($pythonExe)"
            break
        }
        Write-Output "[UNKNOWN] python candidate found, version probe failed: $($found.Source)"
    } catch {
        Write-Output "[UNKNOWN] python candidate found, version probe failed: $($found.Source)"
    }
}
if (-not $pythonExe) {
    if ($pythonFound) { Write-Output '[UNKNOWN] No usable Python selected; its probe failed.' }
    else { Write-Output '[MISSING] Python executable not found.' }
}

foreach ($name in @('node', 'git', 'curl', 'jq', 'gh', 'rg', 'fd', 'ffmpeg', 'bat', 'uv')) {
    $versionArg = if ($name -eq 'ffmpeg') { '-version' } else { '--version' }
    Check-CLI $name @($name) $versionArg
}

if (-not $SkipPythonPackages) {
    Write-Output "`n=== Python distributions (selected interpreter only) ==="
    if ($pythonExe) {
        try {
            & $pythonExe @pythonArgs (Join-Path $PSScriptRoot 'check-python-packages.py')
            if ($LASTEXITCODE -ne 0) { Write-Output '[UNKNOWN] Python metadata check did not complete.' }
        } catch {
            Write-Output '[UNKNOWN] Could not run the Python metadata check.'
        }
    } else {
        Write-Output '[UNKNOWN] Python packages were not checked; no usable interpreter.'
    }
}

if ($missingCLI.Count) {
    Write-Output "`n=== Suggestions only; install only what the task needs ==="
    $winget = Find-Application 'winget'
    foreach ($name in $missingCLI) {
        if ($winget -and $wingetIds.ContainsKey($name)) {
            Write-Output "winget install --id $($wingetIds[$name]) --exact"
        } else {
            Write-Output "Use the project setup instructions or your package manager for: $name"
        }
    }
}
exit 0
