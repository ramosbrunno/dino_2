@echo off
REM Script de instalação do Dino ARC CLI para Windows
REM Execute este script para instalar o Dino ARC como comando global

echo 🚀 Instalando Dino ARC CLI...

REM Verificar se Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado. Por favor, instale Python 3.8+ primeiro.
    echo Baixe em: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Verificar se pip está instalado
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip não encontrado. Por favor, instale pip primeiro.
    pause
    exit /b 1
)

REM Atualizar pip
echo 📦 Atualizando pip...
pip install --upgrade pip

REM Instalar o pacote em modo desenvolvimento
echo 📦 Instalando Dino ARC...
pip install -e .

REM Verificar instalação
echo ✅ Verificando instalação...
dino-arc --help >nul 2>&1
if %errorlevel% equ 0 (
    echo 🎉 Dino ARC CLI instalado com sucesso!
    echo.
    echo 📋 Comandos disponíveis:
    echo   dino-arc --help                      # Ver ajuda
    echo   dino-arc --action init --projeto test   # Inicializar
    echo   dino-arc --action plan --projeto test   # Planejar
    echo   dino-arc --action apply --projeto test  # Criar recursos
    echo.
    echo 📚 Para mais exemplos, veja: EXEMPLOS_CLI.md
) else (
    echo ❌ Falha na instalação. Verifique os logs acima.
    pause
    exit /b 1
)

echo 🎯 Instalação concluída!
pause
