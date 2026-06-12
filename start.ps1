# PitchIQ - Script de inicialização
# Executa backend e frontend em paralelo

Write-Host "Iniciando PitchIQ..." -ForegroundColor Cyan
Write-Host ""

# Verifica .env do backend
if (-not (Test-Path "backend\.env")) {
    Write-Host "AVISO: backend\.env não encontrado." -ForegroundColor Yellow
    Write-Host "Copie backend\.env.example para backend\.env e adicione suas chaves de API." -ForegroundColor Yellow
    Write-Host ""
}

# Backend
Write-Host "Iniciando backend (FastAPI na porta 8000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\backend'; python -m uvicorn main:app --reload --port 8000"

Start-Sleep -Seconds 2

# Frontend
Write-Host "Iniciando frontend (Next.js na porta 3000)..." -ForegroundColor Blue
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; npm run dev"

Write-Host ""
Write-Host "PitchIQ rodando!" -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Backend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
