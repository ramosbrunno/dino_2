# Guia de Uso do Dino SDK em Notebooks Databricks

## 🚨 Problema Identificado

O comando `dino-config init` falha em notebooks Databricks porque o ambiente não suporta comandos CLI interativos via `%%bash` magic command.

## ✅ Soluções Disponíveis

### 1. 🐍 Configuração Programática (Recomendado para Notebooks)

Use as funções Python diretamente no código do notebook:

```python
# Instalar o SDK (se ainda não instalado)
%pip install /dbfs/FileStore/dino_sdk/dino_sdk-1.0.0-py3-none-any.whl

# Importar funções de configuração
from dino_sdk import configure_dino_sdk, validate_dino_config, show_dino_config

# Configuração básica (apenas Databricks)
result = configure_dino_sdk(
    workspace_url="https://adb-123456789.0.azuredatabricks.net",
    catalog_name="main"
)
print(result)

# Validar configuração
validate_dino_config()
```

### 2. 🔧 Configuração Completa com Azure SQL

```python
from dino_sdk import setup_with_azure_sql

# Configuração completa incluindo Azure SQL para logging
result = setup_with_azure_sql(
    workspace_url="https://adb-123456789.0.azuredatabricks.net",
    azure_sql_server="myserver.database.windows.net",
    azure_sql_username="dino_admin", 
    azure_sql_password="my_secure_password",
    catalog_name="production",
    azure_sql_database="dino_logging"
)

# Verificar se deu certo
if result['success']:
    print("✅ Configuração completa aplicada!")
else:
    print(f"❌ Erro: {result['message']}")
```

### 3. ⚡ Configuração Rápida

```python
from dino_sdk import quick_setup

# Configuração mínima para começar
quick_setup(
    workspace_url="https://adb-123456789.0.azuredatabricks.net",
    catalog_name="main"
)
```

### 4. 🔍 Verificar Configuração Atual

```python
from dino_sdk import show_dino_config, validate_dino_config

# Mostrar configuração atual
config = show_dino_config()

# Validar se está tudo OK
validation = validate_dino_config()
if validation['success']:
    print("🎉 Configuração válida!")
else:
    print("❌ Problemas encontrados:")
    for error in validation['errors']:
        print(f"  • {error}")
```

## 🔧 Comando CLI Não-Interativo (Alternativa)

Se preferir usar CLI, use o modo não-interativo:

```bash
%%bash
dino-config setup \
  --workspace-url "https://adb-123456789.0.azuredatabricks.net" \
  --catalog-name "main" \
  --azure-sql-server "myserver.database.windows.net" \
  --azure-sql-database "dino_logging" \
  --azure-sql-username "dino_admin" \
  --azure-sql-password "my_password"
```

Ou configuração mínima:

```bash
%%bash
dino-config init \
  --workspace-url "https://adb-123456789.0.azuredatabricks.net" \
  --no-interactive
```

## 📊 Usando o SDK Após Configuração

### Ingestão Básica

```python
# Importar engine de ingestão
IngestionEngine = get_ingestion_engine()

# Criar engine
engine = IngestionEngine(
    target_schema="bronze",
    table_name="clientes",
    file_path="/Volumes/main/raw/clientes.csv",
    delimiter=",",
    is_automated=False  # batch mode
)

# Executar ingestão (com logging automático)
result = engine.run_batch_ingestion()
print(f"✅ Processados: {result['records_processed']}")
```

### Ingestão Streaming

```python
# Streaming com Auto Loader
engine_streaming = IngestionEngine(
    target_schema="bronze", 
    table_name="pedidos",
    file_path="/Volumes/main/raw/pedidos/",
    delimiter=",",
    is_automated=True  # streaming mode
)

# Configurar streaming
result = engine_streaming.run_streaming_ingestion()
print(f"🔄 Checkpoint: {result['checkpoint_location']}")
```

### Verificar Logs (se Azure SQL configurado)

```python
# Importar CLI de logs
from dino_sdk.logs_cli import logs_cli

# Em notebooks, use as funções diretamente:
from dino_sdk.azure_sql_logger import get_sql_logger

logger = get_sql_logger()

# Obter histórico
history = logger.get_execution_history(limit=10)
for execution in history:
    print(f"{execution['status']} | {execution['table_name']} | {execution['created_at']}")

# Obter estatísticas  
stats = logger.get_execution_stats(days=7)
print(f"Execuções últimos 7 dias: {stats.get('total_executions', 0)}")
```

## 🔧 Variáveis de Ambiente no Cluster

Para configuração persistente, adicione nas **Environment Variables** do cluster:

```bash
DATABRICKS_WORKSPACE_URL=https://adb-123456789.0.azuredatabricks.net
DINO_CATALOG_NAME=main
DINO_CHECKPOINT_BASE_PATH=/tmp/checkpoints/dino_sdk
DINO_AZURE_SQL_SERVER=myserver.database.windows.net
DINO_AZURE_SQL_DATABASE=dino_logging
DINO_AZURE_SQL_USERNAME=dino_admin
DINO_AZURE_SQL_PASSWORD=my_password
```

## 🚀 Exemplo Completo de Notebook

```python
# === CÉLULA 1: Instalação e Configuração ===
%pip install /dbfs/FileStore/dino_sdk/dino_sdk-1.0.0-py3-none-any.whl

# === CÉLULA 2: Configuração Rápida ===
from dino_sdk import configure_dino_sdk, validate_dino_config

# Configurar SDK
configure_dino_sdk(
    workspace_url="https://adb-123456789.0.azuredatabricks.net",
    catalog_name="main",
    azure_sql_server="myserver.database.windows.net",
    azure_sql_database="dino_logging", 
    azure_sql_username="dino_admin",
    azure_sql_password="my_password"
)

# Validar
validate_dino_config()

# === CÉLULA 3: Ingestão de Dados ===
from dino_sdk import get_ingestion_engine

IngestionEngine = get_ingestion_engine()

# Criar e executar ingestão
engine = IngestionEngine(
    target_schema="bronze",
    table_name="sales_data", 
    file_path="/Volumes/main/raw/sales.csv",
    delimiter=",",
    is_automated=False
)

result = engine.run_batch_ingestion()
print(f"✅ Ingestão concluída! ID: {result['execution_id']}")

# === CÉLULA 4: Verificar Logs ===
from dino_sdk.azure_sql_logger import get_sql_logger

logger = get_sql_logger()
history = logger.get_execution_history(limit=5)

for exec in history:
    status_icon = "✅" if exec['status'] == 'concluido' else "❌" if exec['status'] == 'erro' else "🔄"
    print(f"{status_icon} {exec['table_name']} | {exec['records_written']:,} registros | {exec['created_at']}")
```

## 🚨 Troubleshooting

### Erro: "Command returned non-zero exit status 1"

**Causa**: Comando CLI interativo não funciona em notebooks

**Solução**: Use funções Python em vez de CLI:
```python
# ❌ Não funciona em notebooks  
%%bash
dino-config init

# ✅ Funciona em notebooks
from dino_sdk import configure_dino_sdk
configure_dino_sdk(workspace_url="https://...")
```

### Erro: "Module not found"

**Causa**: SDK não instalado ou importação incorreta

**Solução**:
```python
%pip install /dbfs/FileStore/dino_sdk/dino_sdk-1.0.0-py3-none-any.whl
dbutils.library.restartPython()  # Reiniciar Python
```

### Erro: "Configuration not found"

**Causa**: SDK não configurado

**Solução**:
```python
from dino_sdk import configure_dino_sdk
configure_dino_sdk(workspace_url="https://your-workspace-url")
```

## 💡 Dicas de Melhores Práticas

1. **Configure uma vez por cluster**: Use variáveis de ambiente do cluster
2. **Teste a configuração**: Sempre execute `validate_dino_config()`
3. **Use modo demo**: Para testes sem Azure SQL, defina `DINO_DEMO_MODE=true`
4. **Monitore logs**: Configure Azure SQL para rastreabilidade completa
5. **Organize por schemas**: Use schemas bronze/silver/gold para organização

O SDK agora funciona perfeitamente em notebooks Databricks! 🦕✨
