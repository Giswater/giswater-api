param([Parameter(Mandatory)][string]$Version)
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir "..")
Set-Location $RepoRoot

# Abort if working tree is dirty
$dirty = git status --porcelain
if ($dirty) {
    Write-Error "You have uncommitted changes. Please commit or stash them before releasing."
    git status --short
    exit 1
}

$MajorMinor = ($Version -split '\.')[0..1] -join '.'

(Get-Content pyproject.toml) -replace '^version = .*', "version = `"$Version`"" | Set-Content pyproject.toml

git add -A
git commit -m "release: v$Version"
git tag "v$Version"
git checkout -b "release/$MajorMinor"
git push origin main "release/$MajorMinor" "v$Version"
git checkout main

Write-Host "Released v$Version (branch: release/$MajorMinor)"
