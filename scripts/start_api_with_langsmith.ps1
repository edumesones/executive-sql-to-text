# Load .env variables and start API
$envFile = "d:\executive_sql_to_text\.env"

if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim().Trim('"')
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
            Write-Host "Set $name"
        }
    }
}

# Start API
Write-Host "`nStarting API with LangSmith enabled...`n"
& "D:\gestoria_agentes\.venv\Scripts\python.exe" -m uvicorn src.api.main:app --host 0.0.0.0 --port 8001
