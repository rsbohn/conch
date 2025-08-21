# Chasm.psm1 - Content Addressed Storage Module

# Path to the directory holding CAS files
$script:CasRoot = Join-Path $PSScriptRoot 'cas'
if (-not (Test-Path $script:CasRoot)) {
    New-Item -ItemType Directory -Path $script:CasRoot | Out-Null
}

function Store-ContentInCAS {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$Content
    )

    $bytes = [System.Text.Encoding]::UTF8.GetBytes($Content)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    $hashBytes = $sha.ComputeHash($bytes)
    $hash = ([System.BitConverter]::ToString($hashBytes)).Replace('-', '').ToLower()

    $path = Join-Path $script:CasRoot $hash
    Set-Content -Path $path -Value $Content -NoNewline
    return $hash
}

function Get-ContentFromCAS {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$Hash
    )

    $path = Join-Path $script:CasRoot $Hash
    if (-not (Test-Path $path)) {
        throw "Content with hash '$Hash' not found."
    }

    return Get-Content -Path $path -Raw
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
