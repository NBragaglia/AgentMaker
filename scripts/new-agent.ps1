param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[a-z0-9-]+$')]
    [string]$Name,

    [ValidateSet('python-cli-agent')]
    [string]$Template = 'python-cli-agent',

    [string]$AgentsRoot = 'agents'
)

$ErrorActionPreference = 'Stop'

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptRoot
$templateRoot = Join-Path $repoRoot (Join-Path 'templates' $Template)
$targetRoot = Join-Path $repoRoot $AgentsRoot
$targetDir = Join-Path $targetRoot $Name

if (-not (Test-Path $templateRoot)) {
    throw "Template not found: $templateRoot"
}

if (Test-Path $targetDir) {
    throw "Agent already exists: $targetDir"
}

New-Item -ItemType Directory -Force -Path $targetDir | Out-Null
Copy-Item -Path (Join-Path $templateRoot '*') -Destination $targetDir -Recurse -Force

$packageName = $Name -replace '-', '_'

Get-ChildItem -Path $targetDir -Recurse -File | ForEach-Object {
    $content = Get-Content -Path $_.FullName -Raw
    $updated = $content.Replace('__AGENT_NAME__', $Name).Replace('__AGENT_PACKAGE__', $packageName)
    if ($updated -ne $content) {
        Set-Content -Path $_.FullName -Value $updated -Encoding ASCII
    }
}

# Replace placeholder tokens in file and directory names.
Get-ChildItem -Path $targetDir -Recurse -Force |
    Sort-Object FullName -Descending |
    ForEach-Object {
        $newName = $_.Name.Replace('__AGENT_NAME__', $Name).Replace('__AGENT_PACKAGE__', $packageName)
        if ($newName -ne $_.Name) {
            Rename-Item -LiteralPath $_.FullName -NewName $newName
        }
    }

Write-Output "Created agent scaffold at: $targetDir"
Write-Output "Next: cd $targetDir"
