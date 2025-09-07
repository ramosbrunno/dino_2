# 🦕 DINO SDK v2.3.0 - Instalação no Databricks

## 📦 Arquivo Wheel Gerado

✅ **dino_sdk-2.3.0-py3-none-any.whl** (30.048 bytes)

**Localização:** `c:\Users\User\OneDrive\Documentos\Projetos\Data_Master_2025\GIT\dino_2\dino_sdk\dist\dino_sdk-2.3.0-py3-none-any.whl`

## 🚀 Novidades da Versão 2.3.0

### ✅ Base Parameters Atualizados
- **source_path**: Formato `/Volumes/{catalog}/{schema}/raw`
- **type_run**: Sempre `"batch"` (fixo)
- **Ordem correta**: Parâmetros obrigatórios no topo
- **Compatibilidade**: Mantém parâmetros extras para retrocompatibilidade

### 📋 Base Parameters Incluídos
```python
"base_parameters": {
    "source_path": "/Volumes/{catalog}/{schema}/raw",  # ✅ Novo formato
    "table_name": "{table_name}",                       # ✅ 
    "catalog_name": "{catalog_name}",                   # ✅
    "schema_name": "{schema_name}",                     # ✅
    "type_run": "batch",                               # ✅ Sempre batch
    
    # Parâmetros adicionais (compatibilidade)
    "liquid_clustering": "true",
    "schema_evolution_mode": "strict", 
    "dino_version": "2.3.0"
}
```

## 📥 Como Instalar no Databricks

### Método 1: Upload via Interface Web

1. **Acesse o Databricks Workspace**
2. **Vá para Compute → Seu Cluster**
3. **Clique em "Libraries"**
4. **"Install New" → "Upload"**
5. **Selecione o arquivo:** `dino_sdk-2.3.0-py3-none-any.whl`
6. **Clique "Install"**

### Método 2: Via Notebook
```python
%pip install /FileStore/wheels/dino_sdk-2.3.0-py3-none-any.whl --force-reinstall
```

### Método 3: Biblioteca do Cluster
```python
# No campo "Library Source" da configuração do cluster:
# Upload: dino_sdk-2.3.0-py3-none-any.whl
```

## 🧪 Validação da Instalação

### Teste Básico
```python
# Testar importação
from dino_sdk import create_dino_job
from dino_sdk.schema_manager import SchemaManager

print("✅ DINO SDK v2.3.0 importado com sucesso!")

# Verificar versão
import dino_sdk
print(f"📦 Versão instalada: {dino_sdk.__version__}")
```

### Teste de Base Parameters
```python
from dino_sdk import create_dino_job

# Criar job de teste
result = create_dino_job(
    catalog_name="test_catalog",
    schema_name="test_schema", 
    table_name="test_table",
    is_automated=True
)

# Verificar base_parameters
if 'job_config' in result:
    task = result['job_config']['tasks'][0]
    params = task['notebook_task']['base_parameters']
    
    print("📦 Base Parameters:")
    print(f"   source_path: {params['source_path']}")
    print(f"   table_name: {params['table_name']}")
    print(f"   catalog_name: {params['catalog_name']}")
    print(f"   schema_name: {params['schema_name']}")
    print(f"   type_run: {params['type_run']}")
    
    # Validar formato
    expected_path = "/Volumes/test_catalog/test_schema/raw"
    if params['source_path'] == expected_path:
        print("✅ Source path está no formato correto!")
    
    if params['type_run'] == 'batch':
        print("✅ Type run está correto (batch)!")
```

## 🎯 Casos de Uso

### 1. Setup de Schema + Job
```python
from dino_sdk.schema_manager import ensure_schema_simple
from dino_sdk import create_dino_job

# 1. Criar schema e volumes
ensure_schema_simple(spark, "data_master_dev", "bronze")

# 2. Criar job de ingestão
result = create_dino_job(
    catalog_name="data_master_dev",
    schema_name="bronze",
    table_name="vendas_2024",
    is_automated=True
)

print(f"✅ Job criado: {result['job_name']}")
```

### 2. Ingestão de Dados
```python
from dino_sdk.ingestion_engine import IngestionEngine, IngestionConfig

config = IngestionConfig(
    catalog_name="data_master_dev",
    schema_name="bronze", 
    table_name="produtos",
    source_path="/Volumes/data_master_dev/bronze/raw",
    file_format="csv"
)

engine = IngestionEngine()
result = engine.ingest(config)

print(f"✅ Dados ingeridos: {result['records_processed']}")
```

## 📋 Dependências

### Já Disponíveis no Databricks Runtime
- ✅ `pyspark>=3.4.0`
- ✅ `pandas>=1.5.0` 
- ✅ `numpy>=1.21.0`

### Podem Precisar de Instalação
- `databricks-sdk>=0.18.0` (instalado automaticamente)
- `pyarrow>=10.0.0` (normalmente já disponível)

## 🔍 Troubleshooting

### Erro de Importação
```python
# Se der erro de importação, reinstale:
%pip uninstall dino-sdk -y
%pip install /FileStore/wheels/dino_sdk-2.3.0-py3-none-any.whl --force-reinstall
%restart_python
```

### Verificar Instalação
```python
%pip list | grep dino
# Output esperado: dino-sdk 2.3.0
```

### Limpar Cache
```python
# Se necessário, limpar cache do Python:
import importlib
import sys
if 'dino_sdk' in sys.modules:
    importlib.reload(sys.modules['dino_sdk'])
```

## 📝 Changelog v2.3.0

### ✅ Novas Funcionalidades
- **Base Parameters Padronizados**: Todos os jobs agora seguem o formato especificado
- **Source Path Automático**: `/Volumes/{catalog}/{schema}/raw` gerado automaticamente
- **Type Run Fixo**: Sempre `"batch"` conforme especificação

### 🔧 Melhorias
- **Compatibilidade**: Mantém parâmetros extras para retrocompatibilidade
- **Documentação**: Notebooks de teste e validação incluídos
- **Estrutura**: Organização melhorada dos base_parameters

### 📊 Comparação de Versões
| Parâmetro | v2.0.0 | v2.3.0 |
|-----------|--------|--------|
| source_path | `temp/{table}` | `/Volumes/{catalog}/{schema}/raw` |
| type_run | Dinâmico | `"batch"` (fixo) |
| Ordem | Aleatória | Base parameters no topo |
| Compatibilidade | Parcial | Total |

## 🎉 Pronto para Uso!

O DINO SDK v2.3.0 está pronto para instalação no seu cluster Databricks com os base_parameters atualizados conforme especificação!
