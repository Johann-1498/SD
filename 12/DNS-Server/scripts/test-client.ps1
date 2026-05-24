param(
    [string]$ServerIp = "127.0.0.1",
    [int]$Port = 5053,
    [string]$Domain = "xyz.com"
)

$ErrorActionPreference = "Stop"

function Show-Header {
    Clear-Host
    Write-Host "==============================================" -ForegroundColor DarkBlue
    Write-Host "               DNS CLIENT TEST               " -ForegroundColor Blue
    Write-Host "==============================================" -ForegroundColor DarkBlue
    Write-Host ("Servidor: {0}:{1}" -f $ServerIp, $Port) -ForegroundColor Green
    Write-Host ("Dominio : {0}" -f $Domain) -ForegroundColor Green
    Write-Host "----------------------------------------------" -ForegroundColor DarkBlue
}

Show-Header

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "No se encontro python en tu sistema." -ForegroundColor Red
    exit 1
}

Write-Host "Lanzando consulta DNS UDP..." -ForegroundColor Cyan

$pyScript = @'
import json
import socket
import sys

server_ip = sys.argv[1]
port = int(sys.argv[2])
domain = sys.argv[3].strip(".")

def build_query(name):
    tid = b"\x12\x34"
    flags = b"\x01\x00"
    qdcount = b"\x00\x01"
    ancount = b"\x00\x00"
    nscount = b"\x00\x00"
    arcount = b"\x00\x00"
    qname = b""
    for part in name.split("."):
        qname += bytes([len(part)]) + part.encode("ascii")
    qname += b"\x00"
    qtype = b"\x00\x01"
    qclass = b"\x00\x01"
    return tid + flags + qdcount + ancount + nscount + arcount + qname + qtype + qclass

def parse_response(resp):
    if len(resp) < 12:
        return {"ok": False, "error": "Respuesta demasiado corta"}
    rcode = resp[3] & 0x0F
    ancount = int.from_bytes(resp[6:8], "big")
    idx = 12
    while idx < len(resp) and resp[idx] != 0:
        idx += resp[idx] + 1
    idx += 5
    ips = []
    for _ in range(ancount):
        if idx + 12 > len(resp):
            break
        idx += 2
        rtype = int.from_bytes(resp[idx:idx+2], "big"); idx += 2
        idx += 2
        idx += 4
        rdlen = int.from_bytes(resp[idx:idx+2], "big"); idx += 2
        rdata = resp[idx:idx+rdlen]; idx += rdlen
        if rtype == 1 and rdlen == 4:
            ips.append(".".join(str(b) for b in rdata))
    return {"ok": True, "rcode": rcode, "ancount": ancount, "ips": ips}

query = build_query(domain)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(3)
try:
    sock.sendto(query, (server_ip, port))
    resp, _ = sock.recvfrom(1024)
    print(json.dumps(parse_response(resp)))
except Exception as e:
    print(json.dumps({"ok": False, "error": str(e)}))
finally:
    sock.close()
'@

$tempPy = Join-Path $env:TEMP "dns_client_probe.py"
Set-Content -LiteralPath $tempPy -Value $pyScript -Encoding UTF8
try {
    $json = & python $tempPy $ServerIp $Port $Domain
}
finally {
    Remove-Item -LiteralPath $tempPy -Force -ErrorAction SilentlyContinue
}

$result = $json | ConvertFrom-Json

Write-Host ""
Write-Host "Respuesta del servidor:" -ForegroundColor DarkCyan
Write-Host "----------------------------------------------" -ForegroundColor DarkCyan
if ($result.ok) {
    Write-Host ("rcode   : {0}" -f $result.rcode) -ForegroundColor Gray
    Write-Host ("answers : {0}" -f $result.ancount) -ForegroundColor Gray
}
else {
    Write-Host ("error   : {0}" -f $result.error) -ForegroundColor Gray
}
Write-Host "----------------------------------------------" -ForegroundColor DarkCyan

Write-Host ""
if ($result.ok -and $result.ips.Count -gt 0) {
    Write-Host "Resultado: OK - El servidor respondio." -ForegroundColor Green
    Write-Host "IPs devueltas:" -ForegroundColor Green
    foreach ($ip in $result.ips | Select-Object -Unique) {
        Write-Host ("  - {0}" -f $ip) -ForegroundColor White
    }
    exit 0
}
else {
    if ($result.ok -and $result.rcode -eq 3) {
        Write-Host "Resultado: NXDOMAIN (dominio no encontrado)." -ForegroundColor Yellow
    }
    else {
        Write-Host "Resultado: SIN RESPUESTA O SIN REGISTROS A." -ForegroundColor Yellow
    }
    Write-Host "Verifica que el servidor este activo y que el dominio exista en Zones/*.zone." -ForegroundColor Yellow
    exit 2
}
