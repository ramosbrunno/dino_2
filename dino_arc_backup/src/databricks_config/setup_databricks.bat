@echo off
REM Script de configuração do Databricks Unity Catalog e Serverless para Windows
REM Este script configura o ambiente Databricks após o deploy do Terraform

setlocal enabledelayedexpansion

REM Função para log colorido (simulado)
:log_info
echo [INFO] %~1
goto :eof

:log_warn
echo [WARN] %~1
goto :eof

:log_error
echo [ERROR] %~1
goto :eof

REM Verificar se curl e jq estão disponíveis
:check_dependencies
call :log_info "Verificando dependências..."

where curl >nul 2>&1
if errorlevel 1 (
    call :log_error "curl não encontrado! Instale o curl para continuar."
    exit /b 1
)

where jq >nul 2>&1
if errorlevel 1 (
    call :log_error "jq não encontrado! Instale o jq para continuar."
    call :log_info "Download jq em: https://stedolan.github.io/jq/download/"
    exit /b 1
)

call :log_info "✅ Dependências verificadas"
goto :eof

REM Verificar variáveis de ambiente necessárias
:check_environment
call :log_info "Verificando variáveis de ambiente..."

if "%DATABRICKS_WORKSPACE_URL%"=="" (
    call :log_error "Variável DATABRICKS_WORKSPACE_URL não encontrada!"
    exit /b 1
)

if "%DATABRICKS_ACCESS_TOKEN%"=="" (
    call :log_error "Variável DATABRICKS_ACCESS_TOKEN não encontrada!"
    exit /b 1
)

if "%UNITY_CATALOG_STORAGE_ROOT%"=="" (
    call :log_error "Variável UNITY_CATALOG_STORAGE_ROOT não encontrada!"
    exit /b 1
)

if "%DATABRICKS_WORKSPACE_ID%"=="" (
    call :log_error "Variável DATABRICKS_WORKSPACE_ID não encontrada!"
    exit /b 1
)

if "%PROJETO%"=="" (
    call :log_error "Variável PROJETO não encontrada!"
    exit /b 1
)

if "%AMBIENTE%"=="" (
    call :log_error "Variável AMBIENTE não encontrada!"
    exit /b 1
)

if "%AZURE_REGION%"=="" (
    set AZURE_REGION=East US
    call :log_warn "AZURE_REGION não definida, usando padrão: East US"
)

call :log_info "✅ Todas as variáveis de ambiente estão configuradas"
goto :eof

REM Função para fazer requisições REST para Databricks
:databricks_api
set method=%~1
set endpoint=%~2
set data_file=%~3
set response_file=%TEMP%\databricks_response.json

set url=%DATABRICKS_WORKSPACE_URL%/api/2.1/%endpoint%

if "%data_file%"=="" (
    curl -s -X %method% ^
        -H "Authorization: Bearer %DATABRICKS_ACCESS_TOKEN%" ^
        -H "Content-Type: application/json" ^
        "%url%" > "%response_file%"
) else (
    curl -s -X %method% ^
        -H "Authorization: Bearer %DATABRICKS_ACCESS_TOKEN%" ^
        -H "Content-Type: application/json" ^
        -d @"%data_file%" ^
        "%url%" > "%response_file%"
)

goto :eof

REM Criar Unity Catalog Metastore
:create_metastore
call :log_info "🗄️  Criando Unity Catalog Metastore..."

set metastore_name=unity-catalog-%AZURE_REGION: =-%
set metastore_name=!metastore_name: =-!

REM Criar arquivo JSON temporário
set metastore_file=%TEMP%\metastore_data.json
(
echo {
echo     "name": "!metastore_name!",
echo     "storage_root": "%UNITY_CATALOG_STORAGE_ROOT%",
echo     "region": "%AZURE_REGION%"
echo }
) > "%metastore_file%"

call :databricks_api "POST" "unity-catalog/metastores" "%metastore_file%"

REM Extrair metastore_id da resposta
for /f %%i in ('jq -r ".metastore_id // empty" "%TEMP%\databricks_response.json"') do set metastore_id=%%i

if not "%metastore_id%"=="" if not "%metastore_id%"=="null" (
    call :log_info "✅ Unity Catalog Metastore criado: !metastore_name!"
    echo %metastore_id% > "%TEMP%\metastore_id.txt"
    del "%metastore_file%"
    goto :eof
) else (
    call :log_error "❌ Erro ao criar Metastore"
    type "%TEMP%\databricks_response.json"
    del "%metastore_file%"
    exit /b 1
)

REM Atribuir Metastore ao Workspace
:assign_metastore
call :log_info "🔗 Atribuindo Metastore ao Workspace..."

set /p metastore_id=<"%TEMP%\metastore_id.txt"

REM Criar arquivo JSON temporário
set assignment_file=%TEMP%\assignment_data.json
(
echo {
echo     "metastore_id": "%metastore_id%",
echo     "default_catalog_name": "main"
echo }
) > "%assignment_file%"

call :databricks_api "PUT" "unity-catalog/workspaces/%DATABRICKS_WORKSPACE_ID%/metastore" "%assignment_file%"

REM Verificar se houve erro
for /f %%i in ('jq -r ".error_code // empty" "%TEMP%\databricks_response.json"') do set error_code=%%i

if "%error_code%"=="" (
    call :log_info "✅ Metastore atribuído ao workspace com sucesso!"
    del "%assignment_file%"
    goto :eof
) else (
    call :log_error "❌ Erro ao atribuir Metastore"
    type "%TEMP%\databricks_response.json"
    del "%assignment_file%"
    exit /b 1
)

REM Criar Catalog
:create_catalog
set catalog_name=%PROJETO%_%AMBIENTE%
call :log_info "📚 Criando Catalog: %catalog_name%..."

REM Criar arquivo JSON temporário
set catalog_file=%TEMP%\catalog_data.json
(
echo {
echo     "name": "%catalog_name%",
echo     "comment": "Catalog principal para %PROJETO% em %AMBIENTE%"
echo }
) > "%catalog_file%"

call :databricks_api "POST" "unity-catalog/catalogs" "%catalog_file%"

REM Verificar se o catalog foi criado
for /f %%i in ('jq -r ".name // empty" "%TEMP%\databricks_response.json"') do set created_catalog=%%i

if "%created_catalog%"=="%catalog_name%" (
    call :log_info "✅ Catalog criado: %catalog_name%"
    echo %catalog_name% > "%TEMP%\catalog_name.txt"
    del "%catalog_file%"
    goto :eof
) else (
    call :log_error "❌ Erro ao criar Catalog"
    type "%TEMP%\databricks_response.json"
    del "%catalog_file%"
    exit /b 1
)

REM Criar Schemas
:create_schemas
set /p catalog_name=<"%TEMP%\catalog_name.txt"

for %%s in (bronze silver gold workspace) do (
    call :log_info "🗂️  Criando Schema: %catalog_name%.%%s..."
    
    REM Criar arquivo JSON temporário
    set schema_file=%TEMP%\schema_data_%%s.json
    (
    echo {
    echo     "name": "%%s",
    echo     "catalog_name": "%catalog_name%",
    echo     "comment": "Schema %%s para arquitetura medallion"
    echo }
    ) > "!schema_file!"
    
    call :databricks_api "POST" "unity-catalog/schemas" "!schema_file!"
    
    REM Verificar se o schema foi criado
    for /f %%i in ('jq -r ".name // empty" "%TEMP%\databricks_response.json"') do set created_schema=%%i
    
    if "!created_schema!"=="%%s" (
        call :log_info "✅ Schema criado: %catalog_name%.%%s"
    ) else (
        call :log_warn "⚠️  Schema %catalog_name%.%%s pode já existir ou houve erro"
    )
    
    del "!schema_file!"
)

goto :eof

REM Habilitar Serverless Compute
:enable_serverless
call :log_info "⚡ Habilitando Serverless Compute..."

REM Criar arquivo JSON temporário
set serverless_file=%TEMP%\serverless_config.json
(
echo {
echo     "enableServerlessCompute": "true",
echo     "enableAutomaticClusterUpdate": "true"
echo }
) > "%serverless_file%"

call :databricks_api "PATCH" "workspace-conf" "%serverless_file%"
call :log_info "✅ Configuração Serverless aplicada"
del "%serverless_file%"

goto :eof

REM Criar SQL Warehouse Serverless
:create_sql_warehouse
set warehouse_name=%PROJETO%-%AMBIENTE%-warehouse
call :log_info "🏭 Criando SQL Warehouse Serverless: %warehouse_name%..."

REM Criar arquivo JSON temporário
set warehouse_file=%TEMP%\warehouse_data.json
(
echo {
echo     "name": "%warehouse_name%",
echo     "cluster_size": "2X-Small",
echo     "min_num_clusters": 1,
echo     "max_num_clusters": 1,
echo     "auto_stop_mins": 10,
echo     "enable_photon": true,
echo     "enable_serverless_compute": true,
echo     "warehouse_type": "PRO",
echo     "spot_instance_policy": "COST_OPTIMIZED"
echo }
) > "%warehouse_file%"

call :databricks_api "POST" "sql/warehouses" "%warehouse_file%"

REM Extrair warehouse_id da resposta
for /f %%i in ('jq -r ".id // empty" "%TEMP%\databricks_response.json"') do set warehouse_id=%%i

if not "%warehouse_id%"=="" if not "%warehouse_id%"=="null" (
    call :log_info "✅ SQL Warehouse Serverless criado: %warehouse_name%"
    echo %warehouse_id% > "%TEMP%\warehouse_id.txt"
    del "%warehouse_file%"
    goto :eof
) else (
    call :log_error "❌ Erro ao criar SQL Warehouse"
    type "%TEMP%\databricks_response.json"
    del "%warehouse_file%"
    exit /b 1
)

REM Função principal
:main
call :log_info "🚀 Iniciando configuração do Databricks Unity Catalog e Serverless..."
call :log_info "Projeto: %PROJETO% | Ambiente: %AMBIENTE% | Região: %AZURE_REGION%"

REM Verificar dependências e ambiente
call :check_dependencies
if errorlevel 1 exit /b 1

call :check_environment
if errorlevel 1 exit /b 1

REM Executar configurações
call :create_metastore
if errorlevel 1 exit /b 1

call :log_info "⏳ Aguardando propagação da configuração do Metastore..."
timeout /t 30 /nobreak >nul

call :assign_metastore
if errorlevel 1 exit /b 1

call :log_info "⏳ Aguardando propagação da atribuição..."
timeout /t 30 /nobreak >nul

call :create_catalog
if errorlevel 1 exit /b 1

call :create_schemas

REM Configurar Serverless
call :enable_serverless
call :create_sql_warehouse

REM Resumo
call :log_info "🎉 Configuração do Databricks finalizada!"
call :log_info "📋 Resumo:"
call :log_info "   - Unity Catalog Metastore: Criado"
call :log_info "   - Catalog: %PROJETO%_%AMBIENTE%"
call :log_info "   - Schemas: bronze, silver, gold, workspace"
call :log_info "   - SQL Warehouse: %PROJETO%-%AMBIENTE%-warehouse"
call :log_info "   - Serverless Compute: Habilitado"

REM Limpeza de arquivos temporários
del "%TEMP%\metastore_id.txt" 2>nul
del "%TEMP%\catalog_name.txt" 2>nul
del "%TEMP%\warehouse_id.txt" 2>nul
del "%TEMP%\databricks_response.json" 2>nul

goto :eof

REM Executar função principal
call :main
