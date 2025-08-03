@echo off
title Cliente de Câmera - Sistema RF
color 0E

echo.
echo  ╔═══════════════════════════════════════════════════════════╗
echo  ║              CLIENTE DE CÂMERA - Sistema RF               ║
echo  ╚═══════════════════════════════════════════════════════════╝
echo.

if "%1"=="" (
    echo 📹 Configuração de Câmera
    echo.
    echo Opções de fonte:
    echo   0 = Webcam padrão
    echo   1 = Segunda webcam  
    echo   URL = Câmera IP ^(ex: http://192.168.1.100:8080/video^)
    echo.
    set /p camera_id="🆔 Digite o ID da câmera no sistema: "
    set /p source="📡 Digite a fonte da câmera: "
) else (
    set camera_id=%1
    set source=%2
)

if "%camera_id%"=="" (
    echo ❌ ID da câmera é obrigatório!
    pause
    exit /b 1
)

if "%source%"=="" (
    echo ❌ Fonte da câmera é obrigatória!
    pause
    exit /b 1
)

echo.
echo 🔧 Configuração:
echo   📹 Câmera ID: %camera_id%
echo   📡 Fonte: %source%
echo   🌐 Servidor: http://localhost:5000
echo.

echo 🚀 Iniciando cliente de câmera...
echo 🛑 Pressione Ctrl+C para parar
echo.

python camera_client.py --camera-id %camera_id% --source %source%

pause
