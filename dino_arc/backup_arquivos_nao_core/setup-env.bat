@echo off
echo ========================================
echo DINO ARC - Setup Environment
echo ========================================
echo.

echo 1. Criando ambiente virtual...
python -m venv dino_env
if %errorlevel% neq 0 (
    echo ERRO ao criar ambiente virtual
    exit /b 1
)

echo.
echo 2. Ativando ambiente virtual...
call dino_env\Scripts\activate.bat

echo.
echo 3. Instalando dependencias Python...
pip install -e .
if %errorlevel% neq 0 (
    echo ERRO ao instalar dependencias Python
    exit /b 1
)

echo.
echo 4. Verificando se Terraform esta instalado...
terraform version >nul 2>&1
if %errorlevel% neq 0 (
    echo Terraform nao encontrado. Tentando instalar via winget...
    winget install HashiCorp.Terraform --silent
    if %errorlevel% neq 0 (
        echo.
        echo AVISO: Instalacao automatica do Terraform falhou
        echo.
        echo Por favor, instale o Terraform manualmente usando uma das opcoes:
        echo.
        echo OPCAO 1 - winget ^(Windows 10/11^):
        echo   winget install HashiCorp.Terraform
        echo.
        echo OPCAO 2 - Chocolatey:
        echo   choco install terraform
        echo.
        echo OPCAO 3 - Download manual:
        echo   1. Acesse: https://www.terraform.io/downloads.html
        echo   2. Baixe a versao para Windows
        echo   3. Extraia o terraform.exe em uma pasta
        echo   4. Adicione a pasta ao PATH do sistema
        echo.
        echo OPCAO 4 - PowerShell automatico:
        echo   Execute os comandos do README secao "Opcao D"
        echo.
        echo Apos instalar, execute novamente: setup-env.bat
        echo.
        pause
        exit /b 1
    )
    echo.
    echo Terraform instalado! Reiniciando terminal para atualizar PATH...
    echo Aguarde 3 segundos...
    timeout /t 3 /nobreak >nul
    echo.
) else (
    echo Terraform ja esta instalado
)

echo.
echo 5. Testando instalacao...
echo.
echo Versao do Python:
python --version

echo.
echo Testando Terraform...
terraform version >nul 2>&1
if %errorlevel% neq 0 (
    echo AVISO: Terraform nao esta disponivel no PATH
    echo Isso pode acontecer apos instalacao via winget
    echo.
    echo Solucoes:
    echo 1. Reinicie o terminal/prompt de comando
    echo 2. Reinicie o computador
    echo 3. Adicione manualmente ao PATH
    echo.
    echo Para testar novamente: terraform version
) else (
    echo Versao do Terraform:
    terraform version
)

echo.
echo Testando DINO ARC...
dino_arc --version
if %errorlevel% neq 0 (
    echo ERRO: DINO ARC nao foi instalado corretamente
    exit /b 1
)

echo.
echo ========================================
echo Setup concluido!
echo ========================================
echo.
echo Proximos passos:
echo 1. Se o Terraform nao funcionou, siga as instrucoes acima
echo 2. Configure seu Service Principal no Azure
echo 3. Execute: dino_arc --help para ver as opcoes
echo 4. Consulte o README.md para exemplos completos
echo.
echo Para testar a criacao de recursos:
echo dino_arc --client-id "SEU-CLIENT-ID" --client-secret "SEU-SECRET" ^
echo          --tenant-id "SEU-TENANT" --subscription-id "SUA-SUBSCRIPTION" ^
echo          --action apply --projeto teste --ambiente dev
echo.
echo Para usar o DINO ARC:
echo 1. Ative o ambiente: dino_env\Scripts\activate.bat
echo 2. Execute: dino_arc --action apply [parametros]
echo.
