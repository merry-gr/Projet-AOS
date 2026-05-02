$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$data = Join-Path $root "data.json"

function Get-PythonForService($servicePath) {
  $venvPython = Join-Path $servicePath ".venv\Scripts\python.exe"
  if (-not (Test-Path $venvPython)) {
    Write-Host "Creating venv in $servicePath ..."
    python -m venv (Join-Path $servicePath ".venv")
  }

  return $venvPython
}

function Ensure-Requirements($py, $servicePath) {
  $req = Join-Path $servicePath "requirements.txt"
  if (Test-Path $req) {
    & $py -m pip install -r $req
  }
}

Write-Host "Seeding users-service..."
Push-Location (Join-Path $root "users-services")
$py = Get-PythonForService (Get-Location)
Ensure-Requirements $py (Get-Location)
& $py manage.py migrate
& $py manage.py seed_from_data_json --path $data
Pop-Location

Write-Host "Seeding product_service..."
Push-Location (Join-Path $root "product_service")
$py = Get-PythonForService (Get-Location)
Ensure-Requirements $py (Get-Location)
& $py manage.py migrate
& $py manage.py seed_from_data_json --path $data
Pop-Location

Write-Host "Seeding orders_service..."
Push-Location (Join-Path $root "orders_service")
$py = Get-PythonForService (Get-Location)
Ensure-Requirements $py (Get-Location)
& $py manage.py migrate
& $py manage.py seed_from_data_json --path $data
Pop-Location

Write-Host "Done."

