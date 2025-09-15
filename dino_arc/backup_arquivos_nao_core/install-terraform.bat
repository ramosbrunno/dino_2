@echo off
echo ========================================
echo DINO ARC - Instalacao Manual do Terraform
echo ========================================
echo.

echo Este script vai tentar instalar o Terraform usando diferentes metodos
echo.

echo Metodo 1: Tentando winget...
winget install HashiCorp.Terraform --silent
if %errorlevel% equ 0 (
    echo Terraform instalado com sucesso via winget!
    goto :test_installation
)

echo.
echo Metodo 2: Tentando Chocolatey...
where choco >nul 2>&1
if %errorlevel% equ 0 (
    choco install terraform -y
    if %errorlevel% equ 0 (
        echo Terraform instalado com sucesso via Chocolatey!
        goto :test_installation
    )
) else (
    echo Chocolatey nao encontrado, pulando...
)

echo.
echo Metodo 3: Download manual via PowerShell...
echo Criando pasta C:\terraform...
if not exist "C:\terraform" mkdir "C:\terraform"

echo Baixando Terraform...
powershell -Command "try { Invoke-WebRequest -Uri 'https://releases.hashicorp.com/terraform/1.6.6/terraform_1.6.6_windows_amd64.zip' -OutFile 'C:\terraform\terraform.zip' -UseBasicParsing } catch { exit 1 }"
if %errorlevel% neq 0 (
    echo Erro ao baixar Terraform
    goto :manual_instructions
)

echo Extraindo arquivo...
powershell -Command "try { Expand-Archive -Path 'C:\terraform\terraform.zip' -DestinationPath 'C:\terraform' -Force } catch { exit 1 }"
if %errorlevel% neq 0 (
    echo Erro ao extrair Terraform
    goto :manual_instructions
)

echo Removendo arquivo zip...
del "C:\terraform\terraform.zip" >nul 2>&1

echo Adicionando ao PATH do usuario...
powershell -Command "try { $currentPath = [Environment]::GetEnvironmentVariable('PATH', [EnvironmentVariableTarget]::User); if ($currentPath -notlike '*C:\terraform*') { [Environment]::SetEnvironmentVariable('PATH', $currentPath + ';C:\terraform', [EnvironmentVariableTarget]::User) } } catch { exit 1 }"

echo Terraform baixado e instalado em C:\terraform
echo.

:test_installation
echo.
echo Testando instalacao...
echo Aguarde 2 segundos para atualizar PATH...
timeout /t 2 /nobreak >nul

rem Teste simples primeiro
"C:\terraform\terraform.exe" version >nul 2>&1
if %errorlevel% equ 0 (
    echo.
    echo SUCCESS: Terraform instalado e funcionando!
    "C:\terraform\terraform.exe" version
    echo.
    echo Terraform esta disponivel em: C:\terraform\terraform.exe
    goto :success
)

rem Teste via PATH
terraform version >nul 2>&1
if %errorlevel% equ 0 (
    echo.
    echo SUCCESS: Terraform instalado e funcionando!
    terraform version
    goto :success
)

echo.
echo AVISO: Terraform foi instalado mas pode nao estar no PATH ainda
echo.
echo Para usar o Terraform:
echo 1. Reinicie este terminal/prompt
echo 2. Ou reinicie o computador
echo 3. Ou use o caminho completo: C:\terraform\terraform.exe
echo.
goto :end

:manual_instructions
echo.
echo ========================================
echo INSTALACAO MANUAL NECESSARIA
echo ========================================
echo.
echo Por favor, instale o Terraform manualmente:
echo.
echo 1. Acesse: https://www.terraform.io/downloads.html
echo 2. Baixe "Windows AMD64" 
echo 3. Extraia o terraform.exe em uma pasta (ex: C:\terraform)
echo 4. Adicione a pasta ao PATH do Windows:
echo    - Windows + R ^> sysdm.cpl
echo    - Aba "Avancado" ^> "Variaveis de Ambiente"
echo    - Editar PATH do usuario
echo    - Adicionar: C:\terraform
echo 5. Reiniciar o terminal
echo.
goto :end

:success
echo.
echo ========================================
echo INSTALACAO CONCLUIDA!
echo ========================================
echo.
echo Agora voce pode usar:
echo - terraform version
echo - dino_arc (se ja foi instalado)
echo.
echo Se ainda nao instalou o DINO ARC, execute: setup-env.bat
echo.

:end
pause
