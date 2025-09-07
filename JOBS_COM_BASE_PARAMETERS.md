# 🦕 DINO SDK - Jobs com Base Parameters Atualizados

## ✅ Ajustes Implementados

A função `create_dino_job` foi ajustada para incluir os **base_parameters** conforme especificação:

### 📦 Base Parameters Obrigatórios

| Parâmetro | Descrição | Formato | Exemplo |
|-----------|-----------|---------|---------|
| `source_path` | Caminho do volume RAW | `/Volumes/{catalog}/{schema}/raw` | `/Volumes/data_master_dev/bronze/raw` |
| `table_name` | Nome da tabela | `string` | `"pedidos_2024"` |
| `catalog_name` | Nome do catálogo | `string` | `"data_master_dev"` |
| `schema_name` | Nome do schema | `string` | `"bronze"` |
| `type_run` | Tipo de execução | `"batch"` (fixo) | `"batch"` |

## 🔧 Como Usar

### Exemplo Básico (Job Scheduled)

```python
from dino_sdk import create_dino_job

# Criar job básico
result = create_dino_job(
    catalog_name="data_master_dev",
    schema_name="bronze", 
    table_name="pedidos_2024",
    is_automated=False  # Job scheduled
)

print(f"Job criado: {result['job_name']}")
```

### Exemplo Automatizado (File Arrival Trigger)

```python
from dino_sdk import create_dino_job

# Criar job com file arrival trigger
result = create_dino_job(
    catalog_name="data_master_dev",
    schema_name="bronze",
    table_name="pedidos_2024", 
    is_automated=True  # File arrival trigger
)

print(f"Job automatizado criado: {result['job_name']}")
```

## 📊 Estrutura Resultante

A função `create_dino_job` agora gera jobs com esta estrutura:

```python
{
    "name": "dino_ingestion_data_master_dev_bronze_pedidos_2024",
    "trigger": {
        "pause_status": "UNPAUSED",
        "file_arrival": {
            "url": "/Volumes/data_master_dev/bronze/raw/pedidos_2024/"
        }
    },
    "tasks": [
        {
            "task_key": "dino_ingestion_task",
            "notebook_task": {
                "notebook_path": "/Workspace/dino/dino_ingestion_core",
                "base_parameters": {
                    "source_path": "/Volumes/data_master_dev/bronze/raw",
                    "table_name": "pedidos_2024",
                    "catalog_name": "data_master_dev", 
                    "schema_name": "bronze",
                    "type_run": "batch"
                },
                "source": "WORKSPACE"
            },
            "new_cluster": {
                "cluster_name": "",
                "spark_version": "17.1.x-scala2.13",
                "spark_conf": {
                    "spark.databricks.cluster.profile": "singleNode",
                    "spark.master": "local[*]"
                },
                "azure_attributes": {
                    "availability": "ON_DEMAND_AZURE"
                },
                "node_type_id": "Standard_F4",
                "custom_tags": {
                    "ResourceClass": "SingleNode",
                    "CreatedBy": "dino-sdk",
                    "Purpose": "JobCluster"
                },
                "enable_elastic_disk": True,
                "num_workers": 0
            }
        }
    ]
}
```

## ⚡ Comparação: Antes vs. Depois

### ❌ Antes (Parâmetros Genéricos)
```python
"base_parameters": {
    "catalog_name": "data_master_dev",
    "schema_name": "bronze", 
    "table_name": "pedidos_2024",
    "source_path": "temp/pedidos_2024",  # ❌ Path genérico
    "liquid_clustering": "true",
    "schema_evolution_mode": "strict",
    "type_run": "automated",  # ❌ Dinâmico
    "dino_version": "1.2.0"
}
```

### ✅ Depois (Base Parameters Específicos)
```python
"base_parameters": {
    "source_path": "/Volumes/data_master_dev/bronze/raw",  # ✅ Path correto
    "table_name": "pedidos_2024",
    "catalog_name": "data_master_dev",
    "schema_name": "bronze", 
    "type_run": "batch",  # ✅ Sempre "batch"
    # Parâmetros adicionais mantidos para compatibilidade
    "liquid_clustering": "true",
    "schema_evolution_mode": "strict",
    "dino_version": "2.3.0"
}
```

## 🎯 Casos de Uso

### 1. Ingestão de Vendas
```python
result = create_dino_job(
    catalog_name="ecommerce_prod",
    schema_name="bronze",
    table_name="vendas_2024",
    is_automated=True
)
# Resultado: source_path = "/Volumes/ecommerce_prod/bronze/raw"
```

### 2. Processamento de Logs
```python
result = create_dino_job(
    catalog_name="analytics_dev", 
    schema_name="logs",
    table_name="aplicacao_logs",
    is_automated=True
)
# Resultado: source_path = "/Volumes/analytics_dev/logs/raw"
```

### 3. ETL de Dados Históricos
```python
result = create_dino_job(
    catalog_name="datawarehouse",
    schema_name="staging", 
    table_name="clientes_historico",
    is_automated=False  # Job scheduled
)
# Resultado: source_path = "/Volumes/datawarehouse/staging/raw"
```

## 🔍 Verificação dos Base Parameters

Para verificar se os base_parameters foram configurados corretamente:

```python
from dino_sdk import create_dino_job

result = create_dino_job("meu_catalog", "meu_schema", "minha_tabela")

# Extrair base_parameters
if 'job_config' in result:
    task = result['job_config']['tasks'][0]
    params = task['notebook_task']['base_parameters']
    
    print("📦 Base Parameters:")
    for key, value in params.items():
        print(f"   {key}: {value}")
```

## 🚀 Deploy em Produção

### Setup Completo de Ambiente

```python
from dino_sdk import create_dino_job
from dino_sdk.schema_manager import ensure_schema_simple

# 1. Criar schema e volumes
ensure_schema_simple(spark, "data_master_prod", "bronze")

# 2. Criar job de ingestão  
result = create_dino_job(
    catalog_name="data_master_prod",
    schema_name="bronze",
    table_name="transacoes_pix",
    is_automated=True
)

print(f"✅ Job criado: {result['job_name']}")
print(f"📍 Source Path: /Volumes/data_master_prod/bronze/raw")
```

## 📝 Notas Importantes

1. **Source Path**: Sempre no formato `/Volumes/{catalog}/{schema}/raw`
2. **Type Run**: Sempre `"batch"` (fixo na especificação)
3. **Job Name**: Formato `dino_ingestion_{catalog}_{schema}_{table}`
4. **Compatibilidade**: Parâmetros adicionais mantidos para retrocompatibilidade
5. **Volumes**: O volume `raw` deve existir no schema (use `ensure_schema_simple`)

## ✅ Validação

Use o notebook `Teste_Create_Job_Com_Base_Parameters.ipynb` para validar que:

- ✅ Todos os 5 base_parameters obrigatórios estão presentes
- ✅ Source path está no formato correto
- ✅ Type run é sempre "batch"
- ✅ Estrutura do job está conforme especificação
- ✅ File arrival trigger funciona corretamente
