# 🦕 DINO SDK v1.2.0

**Data Integration & Operations - SDK para Databricks Unity Catalog**

## 🎯 Visão Geral

O DINO SDK é uma solução completa para ingestão de dados no Databricks Unity Catalog, oferecendo funcionalidades avançadas como AutoLoader, Liquid Clustering, criação automática de schemas com volumes gerenciados e gerenciamento de metadados.

### ✨ Características Principais

- ✅ **AutoLoader Integrado**: Ingestão automática com schema evolution
- ✅ **Liquid Clustering**: Otimização automática de performance
- ✅ **Unity Catalog**: Suporte completo para governança de dados
- ✅ **Volumes Gerenciados**: Criação automática de volumes para checkpoints, schemas e dados raw
- ✅ **Streaming & Batch**: Compatível com ambos os modos de processamento
- ✅ **CLI Integrada**: Comandos para configuração e gerenciamento
- ✅ **Notebook Ready**: Funcionalidades específicas para notebooks Databricks

## 🚀 Instalação Rápida

### Databricks Notebook
```python
%pip install /Volumes/main/default/system_files/wheels/dino_sdk-1.2.0-py3-none-any.whl --force-reinstall
```

### Ambiente Local
```bash
pip install dist/dino_sdk-1.2.0-py3-none-any.whl
```

## 💡 Uso Básico

### 1. Criar Schema com Volumes (Recomendado)
```python
from dino_sdk.schema_manager import ensure_schema_simple

# Cria schema + volumes automáticamente
result = ensure_schema_simple(spark, "main", "bronze")

if result['success']:
    print("✅ Schema e volumes criados!")
    print(f"Volumes: {result['volumes_created']}")
```

### 2. Ingestão de Dados
```python
from dino_sdk import IngestionEngine, IngestionConfig

# Configuração
config = IngestionConfig(
    source_path="/mnt/raw-data/sales/",
    catalog_name="main",
    schema_name="bronze", 
    table_name="sales",
    file_extension="csv",
    liquid_clustering=True,
    clustering_columns=["region", "date"]
)

# Ingestão
engine = IngestionEngine(config, spark)
result = engine.process_data()

if result['success']:
    print(f"✅ Dados ingeridos: {result['records_processed']} registros")
```

### 3. CLI - Configuração
```bash
# Ver configurações
dino-config show

# Criar schema com volumes
dino-config create-schema --catalog-name main --schema-name bronze
```

## 📚 Documentação

### Guias Essenciais
- 📖 [**Guia Completo de Uso**](GUIA_USO_COMPLETO.md) - Como usar todas as funcionalidades
- 🏗️ [**Implementação de Volumes**](IMPLEMENTACAO_VOLUMES_COMPLETA.md) - Criação automática de volumes
- 🔧 [**IngestionEngine**](INGESTION_ENGINE_SUMMARY.md) - Motor de ingestão de dados
- 💎 [**Liquid Clustering**](LIQUID_CLUSTERING_GUIDE.md) - Otimização de performance

### Configurações
- 🔐 [**Secret Scopes**](GUIA_SECRET_SCOPE.md) - Configuração de segurança
- 🎟️ [**Token Manager**](TOKEN_MANAGER_GUIDE.md) - Gerenciamento de tokens

### Releases
- 🆕 [**v1.2.0**](README_v1.2.0.md) - Funcionalidades da versão atual
- 📝 [**Correções Recentes**](CORRECAO_REMOCAO_SYSTEM_FILES.md) - Últimas correções

## 🧪 Testes

Execute o notebook de testes completo:
```python
# Abrir notebook
%run TESTE_DINO_CONFIG_VOLUMES_FIXED.ipynb
```

## 📦 Estrutura do Projeto

```
dino_sdk/
├── 📄 setup.py                    # Configuração do pacote
├── 📄 requirements.txt            # Dependências
├── 📄 README.md                   # Este arquivo
│
├── 🐍 src/                        # Código fonte
│   └── dino_sdk/                  # Módulo principal
│       ├── __init__.py
│       ├── cli.py                 # CLI commands
│       ├── ingestion_engine.py    # Motor de ingestão
│       ├── schema_manager.py      # Gerenciamento de schemas/volumes
│       ├── workflow_manager.py    # Gerenciamento de workflows
│       └── genie_assistant.py     # Assistente inteligente
│
├── 📦 dist/                       # Wheels de distribuição
├── 🧪 tests/                      # Testes unitários
├── 📝 examples/                   # Exemplos de uso
├── 📓 notebooks/                  # Notebooks de exemplo
└── 📚 [docs]/                     # Documentação detalhada
```

## 🎯 Funcionalidades Principais

### Schema & Volumes
- ✅ Criação automática de schemas Unity Catalog
- ✅ Volumes gerenciados (`_checkpoints`, `_schemas`, `raw`)
- ✅ Verificação de existência (idempotente)
- ✅ Suporte a localização gerenciada customizada

### Ingestão de Dados
- ✅ AutoLoader com CloudFiles format
- ✅ Schema evolution automática
- ✅ Suporte a CSV, JSON, Parquet
- ✅ Rescued data para dados problemáticos
- ✅ Streaming e batch processing

### Performance
- ✅ Liquid Clustering inteligente
- ✅ Validação automática de colunas de clustering
- ✅ Fallback para CLUSTER BY AUTO
- ✅ Otimizações de I/O

### Compatibilidade
- ✅ Databricks Runtime 13.x+
- ✅ Unity Catalog
- ✅ Notebooks e jobs
- ✅ Streaming e batch DataFrames

## 🔄 Workflow Típico

1. **Setup**: `ensure_schema_simple()` - Cria schema + volumes
2. **Configure**: `IngestionConfig()` - Define parâmetros
3. **Process**: `engine.process_data()` - Executa ingestão
4. **Monitor**: Logs automáticos e métricas
5. **Optimize**: Liquid Clustering automático

## 🛠️ Desenvolvimento

### Requisitos
- Python 3.8+
- PySpark 3.4+
- Databricks Runtime 13.x+

### Build
```bash
python setup.py bdist_wheel
```

### Testes
```bash
pytest tests/
```

## 📞 Suporte

Para dúvidas ou problemas:
1. Consulte a [documentação completa](GUIA_USO_COMPLETO.md)
2. Execute o [notebook de testes](TESTE_DINO_CONFIG_VOLUMES_FIXED.ipynb)
3. Verifique os [guias específicos](IMPLEMENTACAO_VOLUMES_COMPLETA.md)

## 🎉 Status

**DINO SDK v1.2.0** - ✅ **Estável e Pronto para Produção**

- ✅ Funcionalidades completas implementadas
- ✅ Testes abrangentes executados
- ✅ Documentação atualizada
- ✅ Projeto sanitizado e equalizado

---

**🦕 DINO SDK - Simplifique sua ingestão de dados no Databricks!**
