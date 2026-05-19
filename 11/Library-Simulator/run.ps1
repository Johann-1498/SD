param(
    [string]$JavaFxLib = $env:JAVAFX_LIB
)

$ErrorActionPreference = "Stop"

if (-not $JavaFxLib) {
    Write-Host "Uso:"
    Write-Host "  .\run.ps1 -JavaFxLib ""C:\ruta\javafx-sdk\lib"""
    Write-Host "O define variable de entorno:"
    Write-Host "  setx JAVAFX_LIB ""C:\ruta\javafx-sdk\lib"""
    exit 1
}

if (-not (Test-Path -LiteralPath $JavaFxLib)) {
    Write-Error "No existe la ruta JavaFX lib: $JavaFxLib"
}

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$srcDir = Join-Path $projectRoot "src"
$classesDir = Join-Path $projectRoot "build\classes"
$resSourceDir = Join-Path $srcDir "res"
$resTargetDir = Join-Path $classesDir "res"

New-Item -ItemType Directory -Force -Path $classesDir | Out-Null

$javaFiles = Get-ChildItem -Path $srcDir -Recurse -Filter *.java | ForEach-Object { $_.FullName }
if (-not $javaFiles -or $javaFiles.Count -eq 0) {
    Write-Error "No se encontraron archivos .java en $srcDir"
}

Write-Host "Compilando..."
javac `
  --module-path "$JavaFxLib" `
  --add-modules javafx.controls,javafx.fxml,javafx.graphics `
  -d "$classesDir" `
  $javaFiles

Write-Host "Copiando recursos..."
if (Test-Path -LiteralPath $resTargetDir) {
    Remove-Item -LiteralPath $resTargetDir -Recurse -Force
}
Copy-Item -Path $resSourceDir -Destination $resTargetDir -Recurse -Force

Write-Host "Ejecutando..."
java `
  --module-path "$JavaFxLib" `
  --add-modules javafx.controls,javafx.fxml,javafx.graphics `
  -cp "$classesDir" `
  com.librarysimulator.Application.Main
