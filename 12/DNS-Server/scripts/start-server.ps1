param(
    [string]$Ip = "127.0.0.1",
    [int]$Port = 5053
)

$ErrorActionPreference = "Stop"

function Show-Banner {
    Clear-Host
    Write-Host "==============================================" -ForegroundColor DarkCyan
    Write-Host "              DNS SERVER RUNNER              " -ForegroundColor Cyan
    Write-Host "==============================================" -ForegroundColor DarkCyan
    Write-Host ("IP   : {0}" -f $Ip) -ForegroundColor Green
    Write-Host ("PORT : {0}" -f $Port) -ForegroundColor Green
    Write-Host "----------------------------------------------" -ForegroundColor DarkCyan
}

function Test-PortAvailable {
    param(
        [string]$TargetIp,
        [int]$TargetPort
    )
    try {
        $udpClient = New-Object System.Net.Sockets.UdpClient($TargetPort)
        $udpClient.Close()
        return $true
    }
    catch {
        return $false
    }
}

Show-Banner

if (-not (Test-Path ".\Server.py")) {
    Write-Host "No se encontro Server.py en el directorio actual." -ForegroundColor Red
    Write-Host "Ejecuta este script desde la raiz del proyecto DNS-Server." -ForegroundColor Yellow
    exit 1
}

if (-not (Test-PortAvailable -TargetIp $Ip -TargetPort $Port)) {
    Write-Host ("El puerto {0} ya esta en uso." -f $Port) -ForegroundColor Red
    Write-Host "Prueba otro puerto. Ejemplo: .\scripts\start-server.ps1 -Port 5054" -ForegroundColor Yellow
    exit 1
}

$env:DNS_IP = $Ip
$env:DNS_PORT = "$Port"

Write-Host "Iniciando servidor DNS..." -ForegroundColor Cyan
Write-Host "Presiona Ctrl + C para detenerlo." -ForegroundColor Yellow
Write-Host "==============================================" -ForegroundColor DarkCyan

python .\Server.py
