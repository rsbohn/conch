# Chasm.psm1 - Content Addressed Storage Module

function Get-CASRoot {
    $root = $env:CONCH_CAS_ROOT
    if (-not $root) {
        $home = $env:HOME
        if (-not $home) {
            $home = [Environment]::GetFolderPath('UserProfile')
        }
        $root = Join-Path $home '.conch' 'cas'
    }
    if (-not (Test-Path $root)) {
        New-Item -ItemType Directory -Path $root | Out-Null
    }
    $store = Join-Path $root 'store'
    if (-not (Test-Path $store)) {
        New-Item -ItemType Directory -Path $store | Out-Null
    }
    return $root
}

$script:CasRoot = Get-CASRoot
$script:StoreDir = Join-Path $script:CasRoot 'store'

function Get-CASPath {
    param(
        [Parameter(Mandatory=$true)][string]$Hash
    )
    $prefix = $Hash.Substring(0,2)
    $dir = Join-Path $script:StoreDir $prefix
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
    }
    return Join-Path $dir $Hash
}

function Store-ContentInCAS {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$Content
    )

    $bytes = [System.Text.Encoding]::UTF8.GetBytes($Content)
    if ($bytes.Length -gt 4MB) {
        throw "Content too large (>4MB)"
    }
    $sha = [System.Security.Cryptography.SHA256]::Create()
    $hashBytes = $sha.ComputeHash($bytes)
    $hash = ([System.BitConverter]::ToString($hashBytes)).Replace('-', '').ToLower()

    $path = Get-CASPath -Hash $hash
    if (-not (Test-Path $path)) {
        $utf8 = New-Object System.Text.UTF8Encoding($false)
        [System.IO.File]::WriteAllText($path, $Content, $utf8)
    }
    return $hash
}

function Get-ContentFromCAS {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$Hash
    )

    $path = Get-CASPath -Hash $Hash
    if (-not (Test-Path $path)) {
        return $null
    }
    $utf8 = New-Object System.Text.UTF8Encoding($false)
    return [System.IO.File]::ReadAllText($path, $utf8)
}

function Set-CASContent {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true, ValueFromPipeline=$true)]
        [string]$Content
    )
    process {
        $hash = Store-ContentInCAS -Content $Content
        Write-Output $hash
    }
}

function Get-CASContent {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$Hash
    )
    process {
        $content = Get-ContentFromCAS -Hash $Hash
        Write-Output $content
    }
}

Export-ModuleMember -Function Get-CASContent, Set-CASContent
