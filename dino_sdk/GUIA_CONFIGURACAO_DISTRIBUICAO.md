# Guia Completo: Configuração e Distribuição do Dino SDK

## 📋 Índice
1. [Como usar o dino-config](#como-usar-o-dino-config)
2. [Configuração do Azure SQL Database](#configuração-do-azure-sql-database)
3. [Gerando o arquivo .whl](#gerando-o-arquivo-whl)
4. [Instalação no Cluster Databricks](#instalação-no-cluster-databricks)
5. [Comandos de Log](#comandos-de-log)

## 🔧 Como usar o dino-config

O `dino-config` é o utilitário de configuração do Dino SDK que facilita a configuração inicial e gerenciamento das variáveis de ambiente.

### Comandos Disponíveis

```bash
# Inicialização interativa (recomendado para primeira configuração)
dino-config init

# Mostrar configuração atual
dino-config show

# Validar configuração
dino-config validate

# Ajuda
dino-config --help
```

### Configuração Inicial

```bash
# 1. Execute a configuração interativa
dino-config init

# O comando irá solicitar as seguintes informações:
# - Workspace URL do Databricks
# - Nome do catálogo Unity Catalog (opcional)
# - Base path para checkpoints (opcional)
# - Configurações do Azure SQL Database
```

### Exemplo de Configuração Interativa

```bash
$ dino-config init

🦕 Dino SDK - Configuração Inicial
==================================

🏢 Configuração do Databricks:

Databricks Workspace URL (ex: https://adb-123456789.0.azuredatabricks.net): 
https://adb-987654321.0.azuredatabricks.net

Nome do Catálogo Unity Catalog [main]: 
production

Base path para checkpoints [/Volumes/main/checkpoints]: 
/Volumes/production/dino_checkpoints

💾 Configuração do Azure SQL Database:

Servidor Azure SQL (ex: myserver.database.windows.net): 
dino-logs.database.windows.net

Nome da Database: 
dino_logging

Username: 
dino_admin

Password: 
********

✅ Configuração salva com sucesso!
🔧 Variáveis configuradas:
   - DATABRICKS_WORKSPACE_URL
   - DINO_CATALOG_NAME
   - DINO_CHECKPOINT_BASE_PATH
   - DINO_AZURE_SQL_SERVER
   - DINO_AZURE_SQL_DATABASE
   - DINO_AZURE_SQL_USERNAME
   - DINO_AZURE_SQL_PASSWORD

💡 Para aplicar no cluster Databricks, adicione estas variáveis nas configurações do cluster.
```

### Configuração Manual via Variáveis de Ambiente

Você também pode configurar manualmente as variáveis de ambiente:

```bash
# Databricks (obrigatório)
export DATABRICKS_WORKSPACE_URL="https://adb-123456789.0.azuredatabricks.net"

# Unity Catalog (opcional, padrão: main)
export DINO_CATALOG_NAME="main"

# Checkpoints (opcional, padrão: /Volumes/main/checkpoints)
export DINO_CHECKPOINT_BASE_PATH="/Volumes/main/checkpoints"

# Azure SQL Database (obrigatório para logging)
export DINO_AZURE_SQL_SERVER="your-server.database.windows.net"
export DINO_AZURE_SQL_DATABASE="dino_logging"
export DINO_AZURE_SQL_USERNAME="dino_admin"
export DINO_AZURE_SQL_PASSWORD="your-password"

# Ou string de conexão completa
export DINO_AZURE_SQL_CONNECTION_STRING="Driver={ODBC Driver 18 for SQL Server};Server=tcp:server.database.windows.net,1433;Database=database;Uid=username;Pwd=password;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
```

## 🗃️ Configuração do Azure SQL Database

### Criando o Azure SQL Database

1. **No Portal Azure:**
   - Crie um Azure SQL Database
   - Configure um servidor SQL se necessário
   - Anote as informações de conexão

2. **Configurar Firewall:**
   - Adicione os IPs dos clusters Databricks
   - Ou configure "Allow Azure Services"

3. **Criar Database:**
   ```sql
   CREATE DATABASE dino_logging;
   ```

4. **Criar Usuário (opcional):**
   ```sql
   CREATE LOGIN dino_admin WITH PASSWORD = 'StrongPassword123!';
   USE dino_logging;
   CREATE USER dino_admin FOR LOGIN dino_admin;
   ALTER ROLE db_datareader ADD MEMBER dino_admin;
   ALTER ROLE db_datawriter ADD MEMBER dino_admin;
   ALTER ROLE db_ddladmin ADD MEMBER dino_admin;
   ```

### Testando a Conexão

```bash
# Teste a conexão com Azure SQL
dino-logs test-connection
```

## 📦 Gerando o arquivo .whl

### Método 1: Setup.py

```bash
# 1. Navegue até o diretório do dino_sdk
cd c:\Users\User\OneDrive\Documentos\Projetos\Data_Master_2025\GIT\dino_2\dino_sdk

# 2. Gere o arquivo wheel
python setup.py bdist_wheel

# 3. O arquivo .whl será criado em dist/
# Exemplo: dist/dino_sdk-2.0.0-py3-none-any.whl
```

### Método 2: Build (Recomendado)

```bash
# 1. Instale o build se não tiver
pip install build

# 2. Navegue até o diretório do projeto
cd c:\Users\User\OneDrive\Documentos\Projetos\Data_Master_2025\GIT\dino_2\dino_sdk

# 3. Execute o build
python -m build

# 4. Arquivos gerados em dist/:
# - dino_sdk-2.0.0-py3-none-any.whl (wheel)
# - dino_sdk-2.0.0.tar.gz (source)
```

### Estrutura do setup.py

O arquivo `setup.py` está configurado com:

```python
setup(
    name="dino-sdk",
    version="2.0.0",
    description="SDK para ingestão híbrida de dados no Databricks",
    author="Data Master Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pyspark>=3.4.0",
        "databricks-connect>=13.0.0",
        "databricks-sdk>=0.18.0",
        "pyodbc>=4.0.0",
        "pandas>=1.5.0",
        "click>=8.0.0",
        # ... outras dependências
    ],
    entry_points={
        "console_scripts": [
            "dino-ingest=dino_sdk.cli:main",
            "dino-config=dino_sdk.config_cli:config_cli",
            "dino-logs=dino_sdk.logs_cli:logs_cli",
        ],
    },
    python_requires=">=3.8",
)
```

## 🚀 Instalação no Cluster Databricks

### Método 1: Upload via Interface

1. **Upload do arquivo .whl:**
   - Vá para Workspace → Upload
   - Faça upload do arquivo `dino_sdk-2.0.0-py3-none-any.whl`

2. **Instalação no cluster:**
   - Clusters → Seu Cluster → Libraries
   - Install New → Upload → Python Whl
   - Selecione o arquivo .whl uploaded

### Método 2: DBFS CLI

```bash
# 1. Upload para DBFS
databricks fs cp dist/dino_sdk-2.0.0-py3-none-any.whl dbfs:/FileStore/dino_sdk/

# 2. Instale no cluster via notebook
%pip install /dbfs/FileStore/dino_sdk/dino_sdk-2.0.0-py3-none-any.whl
```

### Método 3: Cluster Init Script

Crie um script de inicialização:

```bash
#!/bin/bash

# init-script.sh
pip install /dbfs/FileStore/dino_sdk/dino_sdk-2.0.0-py3-none-any.whl

# Configure variáveis de ambiente do cluster
export DATABRICKS_WORKSPACE_URL="https://adb-123456789.0.azuredatabricks.net"
export DINO_CATALOG_NAME="main"
export DINO_AZURE_SQL_SERVER="your-server.database.windows.net"
export DINO_AZURE_SQL_DATABASE="dino_logging"
export DINO_AZURE_SQL_USERNAME="dino_admin"
export DINO_AZURE_SQL_PASSWORD="your-password"
```

### Configuração das Variáveis no Cluster

No Databricks, configure as variáveis de ambiente:

1. **Cluster Configuration → Advanced Options → Environment Variables:**

```
DATABRICKS_WORKSPACE_URL=https://adb-123456789.0.azuredatabricks.net
DINO_CATALOG_NAME=main
DINO_CHECKPOINT_BASE_PATH=/Volumes/main/checkpoints
DINO_AZURE_SQL_SERVER=your-server.database.windows.net
DINO_AZURE_SQL_DATABASE=dino_logging
DINO_AZURE_SQL_USERNAME=dino_admin
DINO_AZURE_SQL_PASSWORD=your-password
```

## 📊 Comandos de Log

Após a instalação, você terá acesso aos comandos de logging:

### Verificar Conexão

```bash
# Teste a conexão com Azure SQL
dino-logs test-connection
```

### Histórico de Execuções

```bash
# Últimas 20 execuções
dino-logs history

# Filtrar por status
dino-logs history --status concluido

# Filtrar por tabela
dino-logs history --table pedidos

# Saída em JSON
dino-logs history --json
```

### Estatísticas

```bash
# Estatísticas dos últimos 30 dias
dino-logs stats

# Estatísticas dos últimos 7 dias
dino-logs stats --days 7

# Saída em JSON
dino-logs stats --json
```

### Limpeza de Logs

```bash
# Remover logs com mais de 90 dias
dino-logs cleanup --days 90
```

## 🧪 Testando a Instalação

Após a instalação, teste o SDK:

```python
# Em um notebook Databricks
from dino_sdk import IngestionEngine

# Teste básico
engine = IngestionEngine(
    target_schema="default",
    table_name="test_table",
    file_path="/Volumes/main/test/data.csv"
)

print("✅ Dino SDK instalado com sucesso!")
```

## 📝 Exemplo Completo de Uso

```bash
# 1. Configure o ambiente
dino-config init

# 2. Execute ingestão batch
dino-ingest --target-schema bronze --table-name customers --file-path /Volumes/main/raw/customers.csv

# 3. Execute ingestão streaming
dino-ingest --target-schema bronze --table-name orders --file-path /Volumes/main/raw/orders/ --is-automated

# 4. Crie job automatizado
dino-ingest --target-schema bronze --table-name products --file-path /Volumes/main/raw/products/ --is-automated --create-job --job-name "Products_Ingestion"

# 5. Verifique logs
dino-logs history
dino-logs stats
```

## 🚨 Troubleshooting

### Problemas Comuns

1. **Erro de conexão com Azure SQL:**
   ```bash
   dino-logs test-connection
   # Verifique firewall e credenciais
   ```

2. **Dependências não encontradas:**
   ```bash
   pip install --upgrade pyodbc
   # No Databricks, use %pip install
   ```

3. **Permissões no Unity Catalog:**
   - Verifique se o usuário tem permissões no schema
   - Verifique permissões nos Volumes

4. **Variáveis de ambiente:**
   ```bash
   dino-config show
   # Verifique se todas as variáveis estão configuradas
   ```

## 📈 Monitoramento

O Dino SDK registra automaticamente:

- ✅ Status da execução (iniciado, concluído, erro)
- 📊 Volume de dados (registros lidos/escritos)
- 📁 Paths utilizados (origem/destino)
- ⏱️ Tempo total de execução
- 💥 Detalhes de erros com stack trace

Todos os logs ficam disponíveis no Azure SQL Database para análise e auditoria.
