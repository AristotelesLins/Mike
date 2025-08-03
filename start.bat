@echo off
title Sistema de Reconhecimento Facial
color 0A

echo.
echo  ╔═══════════════════════════════════════════════════════════╗
echo  ║           SISTEMA DE RECONHECIMENTO FACIAL               ║
echo  ║                   Projeto SDD                             ║
echo  ╚═══════════════════════════════════════════════════════════╝
echo.

REM Verifica se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado! Instale Python 3.8+ primeiro.
    echo 📥 Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Verifica se está no ambiente virtual
python -c "import sys; exit(0 if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) else 1)" 2>nul
if errorlevel 1 (
    echo ⚠️  Ambiente virtual não detectado
    echo 🔧 Tentando ativar ambiente virtual...
    
    if exist "venv\Scripts\activate.bat" (
        call venv\Scripts\activate.bat
        echo ✅ Ambiente virtual ativado
    ) else (
        echo ❌ Ambiente virtual não encontrado
        echo 💡 Execute: python -m venv venv
        echo 💡 Em seguida: venv\Scripts\activate
        echo 💡 E depois: pip install -r requirements.txt
        pause
        exit /b 1
    )
)

REM Verifica se o arquivo .env existe
if not exist ".env" (
    echo ❌ Arquivo .env não encontrado!
    if exist ".env.example" (
        echo 🔧 Copiando .env.example para .env...
        copy .env.example .env >nul
        echo ✅ Arquivo .env criado
        echo ⚠️  IMPORTANTE: Configure suas credenciais no arquivo .env
        echo.
        notepad .env
        echo.
        echo 🔄 Pressione qualquer tecla após configurar o .env...
        pause >nul
    ) else (
        echo ❌ Arquivo .env.example também não encontrado!
        pause
        exit /b 1
    )
)

echo 🧪 Executando testes do sistema...
python test_system.py
if errorlevel 1 (
    echo.
    echo ❌ Alguns testes falharam. Deseja continuar mesmo assim? (s/N)
    set /p continue="Resposta: "
    if /i not "%continue%"=="s" (
        echo 🛑 Execução cancelada
        pause
        exit /b 1
    )
)

echo.
echo 🚀 Iniciando Sistema de Reconhecimento Facial...
echo.
echo 📊 Dashboard: http://localhost:5000
echo 🛑 Pressione Ctrl+C para parar
echo.

REM Inicia o servidor
python app.py

pause
