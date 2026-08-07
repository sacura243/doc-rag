$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
if (-not $env:API_JWT_SECRET) { $env:API_JWT_SECRET = 'local-development-signing-secret-32-bytes' }
if (-not $env:API_ENV) { $env:API_ENV = 'development' }
$apiHost = if ($env:API_HOST) { $env:API_HOST } else { '127.0.0.1' }
& 'D:\tools\Python\python.exe' -m uvicorn api.main:create_app --factory --host $apiHost --port 8010
