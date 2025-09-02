# 🦕 Dino SDK

**Data Ingestion SDK for Databricks** - SDK completo para ingestão híbrida (batch/streaming) de dados no Databricks com Auto Loader, File Arrival Trigger e integração com Genie Assistant.

## ✨ Características Principais

- ✅ **CLI Unificada**: Comando `dino-ingest` com parâmetros intuitivos
- ✅ **Modo Híbrido**: Suporte a batch e streaming com Auto Loader
- ✅ **File Arrival Trigger**: Execução automática quando arquivos chegam
- ✅ **Unity Catalog**: Integração completa com schemas existentes
- ✅ **Genie Assistant**: Configuração automática de salas para consultas inteligentes
- ✅ **Jobs Automatizados**: Criação de jobs do Databricks com triggers
- ✅ **Metadados de Auditoria**: Rastreamento completo de ingestões
- ✅ **Configuração Flexível**: Variáveis de ambiente e arquivos de configuração

## 🚀 Instalação Rápida

```bash
# No cluster Databricks
%pip install /path/to/dino_sdk

# Configuração inicial
dino-config init

# Validar configuração
dino-config validate
```

## 📝 Uso Básico

### Ingestão Batch Simples
```bash
dino-ingest \
  --target-schema vendas_db \
  --table-name clientes \
  --file-path /Volumes/main/landing/clientes.csv
```

### Ingestão Streaming com Auto Loader
```bash
dino-ingest \
  --target-schema vendas_db \
  --table-name pedidos \
  --file-path /Volumes/main/landing/pedidos/ \
  --delimiter ',' \
  --is-automated \
  --has-genie
```

### Job Automatizado com File Arrival Trigger
```bash
dino-ingest \
  --target-schema vendas_db \
  --table-name produtos \
  --file-path /Volumes/main/landing/produtos/ \
  --delimiter ',' \
  --is-automated \
  --has-genie \
  --create-job \
  --job-name "Ingestao_Produtos_Automatizada"
```

## �️ Configuração de Ambiente

### Variáveis de Ambiente Recomendadas

Configure no seu cluster Databricks:

```bash
# Obrigatórias
DATABRICKS_WORKSPACE_URL=https://your-workspace.cloud.databricks.com
DINO_CATALOG_NAME=main

# Opcionais
DINO_CHECKPOINT_BASE_PATH=/tmp/checkpoints/dino_sdk
DINO_VOLUME_BASE_PATH=/Volumes
DINO_DEFAULT_CLUSTER_ID=your-cluster-id
```

### Comandos de Configuração

```bash
# Configuração interativa
dino-config init

# Mostrar configuração atual
dino-config show

# Definir configuração específica
dino-config set --key catalog_name --value production

# Mostrar variáveis de ambiente necessárias
dino-config env

# Validar configuração
dino-config validate
```

## 📊 Funcionalidades Avançadas

### Auto Loader com Schema Evolution
- Detecção automática de novos arquivos
- Evolução automática de schema
- Checkpoint management
- File arrival triggers

### Metadados de Auditoria Automáticos
Todas as tabelas incluem:
- `_dino_ingestion_timestamp`: Timestamp da ingestão
- `_dino_source_file`: Arquivo de origem
- `_dino_batch_id`: ID único do batch
- `_dino_ingestion_mode`: Modo (batch/streaming)

### Integração com Genie
- Criação automática de salas Genie
- Instruções personalizadas
- Consultas de exemplo pré-configuradas
- Tags automáticas

## 🔄 Modos de Execução

| Modo | Parâmetro | Descrição | Uso |
|------|-----------|-----------|-----|
| **Batch** | (padrão) | Processamento único | Arquivos históricos |
| **Streaming** | `--is-automated` | Auto Loader contínuo | Monitoramento de diretórios |
| **Job Manual** | `--create-job` | Job sem trigger | Execução programada |
| **Job Automatizado** | `--create-job --is-automated` | Job com file arrival | Processamento automático |

## 📁 Formatos Suportados

| Formato | Extensões | Auto-detecção | Streaming |
|---------|-----------|---------------|-----------|
| CSV | `.csv` | ✅ | ✅ |
| JSON | `.json`, `.jsonl` | ✅ | ✅ |
| Parquet | `.parquet` | ✅ | ✅ |
| Delta | `.delta` | ✅ | ✅ |
| Avro | `.avro` | ✅ | ✅ |

## 🎯 Casos de Uso

### E-commerce
```bash
# Pedidos em tempo real
dino-ingest \
  --target-schema ecommerce \
  --table-name pedidos \
  --file-path /Volumes/main/ecommerce/pedidos/ \
  --is-automated \
  --has-genie \
  --create-job
```

### Logs de Sistema
```bash
# Logs JSON
dino-ingest \
  --target-schema logs \
  --table-name aplicacao \
  --file-path /Volumes/main/logs/app/ \
  --file-format json \
  --is-automated
```

### Dados Financeiros
```bash
# Transações com merge
dino-ingest \
  --target-schema financeiro \
  --table-name transacoes \
  --file-path /Volumes/main/financeiro/transacoes.parquet \
  --output-mode merge \
  --has-genie
```

## 📈 Monitoramento

### Consultas de Auditoria
```sql
-- Últimas ingestões
SELECT 
  _dino_batch_id,
  _dino_ingestion_timestamp,
  COUNT(*) as records,
  _dino_source_file
FROM schema.tabela
WHERE _dino_ingestion_timestamp >= CURRENT_DATE - INTERVAL 7 DAY
GROUP BY ALL
ORDER BY _dino_ingestion_timestamp DESC;

-- Volume por dia
SELECT 
  DATE(_dino_ingestion_timestamp) as data,
  COUNT(*) as registros,
  COUNT(DISTINCT _dino_batch_id) as batches
FROM schema.tabela
GROUP BY DATE(_dino_ingestion_timestamp)
ORDER BY data DESC;
```
├── __init__.py           # Módulo principal
├── requirements.txt      # Dependências
├── setup.py             # Configuração de instalação
├── README.md            # Documentação
└── tests/               # Testes unitários
```

## 🎯 Parâmetros da CLI

| Parâmetro | Obrigatório | Descrição |
|-----------|-------------|-----------|
| `--target-schema` | ✅ | Schema de destino (deve existir) |
| `--table-name` | ✅ | Nome da tabela a ser criada |
| `--file-path` | ✅ | Caminho dos arquivos |
| `--delimiter` | ❌ | Delimitador CSV (padrão: `,`) |
| `--is-automated` | ❌ | Ativa modo streaming |
| `--has-genie` | ❌ | Configura Genie Assistant |

## 🔄 Modo Streaming

Quando `--is-automated` é usado:
- Ativa **Auto Loader** com notificações de arquivo
- Monitora diretório continuamente
- Processa novos arquivos automaticamente
- Gera workflow JSON para Databricks

## 📊 Arquivos Gerados

- `workflow_dino_auto_ingestion_[schema]_[table].json` - Workflow para Databricks
- `[table]_batch_ingestion.py` ou `[table]_streaming_ingestion.py` - Código Databricks
- `genie_config_[table].json` - Configuração Genie (se `--has-genie`)

## 🛠️ Desenvolvimento

```bash
# Instalar em modo desenvolvimento
pip install -e .

# Executar testes
python -m pytest tests/

# Verificar estrutura
dino-ingest --help
```

## 📋 Requisitos

- Python 3.8+
- Databricks CLI configurado
- Acesso ao Unity Catalog
- Schema de destino pré-existente

---

🦕 **Dino SDK** - Simplificando a ingestão de dados no Databricks!
