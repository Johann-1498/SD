@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%"
set "SRC_DIR=%PROJECT_ROOT%src"
set "CLASSES_DIR=%PROJECT_ROOT%build\classes"
set "RES_SRC=%SRC_DIR%\res"
set "RES_DST=%CLASSES_DIR%\res"

if not "%~1"=="" (
  set "JAVAFX_LIB=%~1"
)

if "%JAVAFX_LIB%"=="" (
  echo Uso:
  echo   run.bat "C:\ruta\javafx-sdk\lib"
  echo o define variable de entorno JAVAFX_LIB.
  exit /b 1
)

if not exist "%JAVAFX_LIB%" (
  echo No existe la ruta JavaFX lib: "%JAVAFX_LIB%"
  exit /b 1
)

if not exist "%CLASSES_DIR%" mkdir "%CLASSES_DIR%"

set "SOURCES_FILE=%PROJECT_ROOT%build\sources.txt"
if not exist "%PROJECT_ROOT%build" mkdir "%PROJECT_ROOT%build"
dir /s /b "%SRC_DIR%\*.java" > "%SOURCES_FILE%"

echo Compilando...
javac --module-path "%JAVAFX_LIB%" --add-modules javafx.controls,javafx.fxml,javafx.graphics -d "%CLASSES_DIR%" @"%SOURCES_FILE%"
if errorlevel 1 exit /b 1

echo Copiando recursos...
if exist "%RES_DST%" rmdir /s /q "%RES_DST%"
xcopy "%RES_SRC%" "%RES_DST%\" /e /i /y > nul
if errorlevel 1 exit /b 1

echo Ejecutando...
java --module-path "%JAVAFX_LIB%" --add-modules javafx.controls,javafx.fxml,javafx.graphics -cp "%CLASSES_DIR%" com.librarysimulator.Application.Main

endlocal
