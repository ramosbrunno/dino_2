# 🦕 Dino SDK - Guia de Instalação e Configuração

## Visão Geral

O Dino SDK é uma ferramenta Python para ingestão híbrida (batch/streaming) de dados no Databricks, com suporte completo ao Auto Loader, File Arrival Trigger e integração com Genie Assistant.

## 🚀 Instalação

### 1. Instalação no Cluster Databricks

```bash
# Método 1: Instalar via pip (recomendado)
%pip install /path/to/dino_sdk

# Método 2: Instalar em modo desenvolvimento
cd /dbfs/dino_sdk
%pip install -e .
```

### 2. Configuração de Variáveis de Ambiente

Configure as seguintes variáveis no seu cluster Databricks:

```bash
# Configurações obrigatórias
DATABRICKS_WORKSPACE_URL=https://your-workspace.cloud.databricks.com
DINO_CATALOG_NAME=main

# Configurações opcionais
DINO_CHECKPOINT_BASE_PATH=/tmp/checkpoints/dino_sdk
DINO_VOLUME_BASE_PATH=/Volumes
DINO_DEFAULT_CLUSTER_ID=your-cluster-id
DINO_JOB_CLUSTER_POLICY_ID=your-policy-id
```

### 3. Configuração Inicial

```bash
# Executar configuração inicial
dino-config init

# Validar configuração
dino-config validate

# Ver configuração atual
dino-config show
```

## 📝 Uso Básico

### Comando Principal: `dino-ingest`

```bash
dino-ingest \
  --target-schema vendas_db \
  --table-name pedidos \
  --file-path /Volumes/main/landing/pedidos/ \
  --delimiter ',' \
  --is-automated \
  --has-genie
```

### Parâmetros

| Parâmetro | Obrigatório | Descrição |
|-----------|-------------|-----------|
| `--target-schema` | ✅ | Schema destino (deve existir) |
| `--table-name` | ✅ | Nome da tabela destino |
| `--file-path` | ✅ | Caminho do arquivo/diretório no Volume |
| `--delimiter` | ❌ | Delimitador do arquivo (padrão: ',') |
| `--is-automated` | ❌ | Usar Auto Loader com streaming |
| `--has-genie` | ❌ | Criar sala Genie |
| `--catalog-name` | ❌ | Nome do catálogo (usa configuração) |
| `--output-mode` | ❌ | Modo de escrita (append/overwrite/merge) |
| `--file-format` | ❌ | Formato (csv/json/parquet/delta/avro) |
| `--create-job` | ❌ | Criar job do Databricks |
| `--job-name` | ❌ | Nome do job (usado com --create-job) |

## 🔄 Modos de Execução

### 1. Ingestão Batch

Para arquivos únicos ou processamento manual:

```bash
dino-ingest \
  --target-schema vendas_db \
  --table-name clientes \
  --file-path /Volumes/main/landing/clientes.csv \
  --delimiter ','
```

### 2. Ingestão Streaming com Auto Loader

Para monitoramento contínuo de diretórios:

```bash
dino-ingest \
  --target-schema vendas_db \
  --table-name pedidos \
  --file-path /Volumes/main/landing/pedidos/ \
  --delimiter ',' \
  --is-automated
```

### 3. Criação de Job Automatizado

Para execução via Databricks Jobs com File Arrival Trigger:

```bash
dino-ingest \
  --target-schema vendas_db \
  --table-name produtos \
  --file-path /Volumes/main/landing/produtos/ \
  --delimiter ',' \
  --is-automated \
  --create-job \
  --job-name "Ingestao_Produtos_Automatizada"
```

### 4. Integração com Genie

Para criar sala Genie automaticamente:

```bash
dino-ingest \
  --target-schema vendas_db \
  --table-name vendas \
  --file-path /Volumes/main/landing/vendas/ \
  --delimiter ',' \
  --is-automated \
  --has-genie
```

## 🧞 Funcionalidades do Genie

Quando `--has-genie` é usado, o SDK:

1. **Cria sala Genie** com configuração otimizada
2. **Adiciona instruções** específicas para a tabela
3. **Configura consultas de exemplo** 
4. **Aplica tags** automáticas

### Consultas Automáticas Disponíveis

- Visão geral dos dados
- Últimas ingestões
- Distribuição por arquivo fonte
- Ingestões por período
- Schema da tabela

## 🏗️ Jobs Automatizados

### File Arrival Trigger

Quando `--is-automated` é usado:

```json
{
  "trigger": {
    "file_arrival": {
      "url": "/Volumes/main/landing/pedidos/",
      "min_time_between_triggers_seconds": 60,
      "wait_after_last_change_seconds": 300
    }
  }
}
```

### Configuração do Cluster

```json
{
  "spark_version": "13.3.x-scala2.12",
  "node_type_id": "i3.xlarge",
  "num_workers": 2,
  "spark_conf": {
    "spark.databricks.delta.autoCompact.enabled": "true",
    "spark.databricks.delta.optimizeWrite.enabled": "true"
  }
}
```

## 📊 Metadados de Auditoria

Todas as tabelas criadas incluem colunas automáticas:

| Coluna | Descrição |
|--------|-----------|
| `_dino_ingestion_timestamp` | Timestamp da ingestão |
| `_dino_source_file` | Arquivo de origem |
| `_dino_batch_id` | Identificador único do batch |
| `_dino_ingestion_mode` | Modo (batch/streaming) |

## ⚙️ Comandos de Configuração

### `dino-config`

```bash
# Configuração inicial
dino-config init

# Mostrar configuração
dino-config show

# Definir configuração específica
dino-config set --key catalog_name --value production

# Obter configuração específica
dino-config get --key catalog_name

# Mostrar variáveis de ambiente
dino-config env

# Validar configuração
dino-config validate

# Gerar exemplo de configuração
dino-config example --output config.json
```

## 🔍 Formatos Suportados

| Formato | Extensão | Auto-detecção |
|---------|----------|---------------|
| CSV | `.csv` | ✅ |
| JSON | `.json`, `.jsonl` | ✅ |
| Parquet | `.parquet` | ✅ |
| Delta | `.delta` | ✅ |
| Avro | `.avro` | ✅ |

## 📁 Estrutura de Arquivos

```
/Volumes/
├── main/                    # Catálogo
│   ├── landing/            # Schema de landing
│   │   ├── vendas/         # Diretório da tabela
│   │   │   ├── file1.csv
│   │   │   └── file2.csv
│   │   └── clientes/
│   │       └── clientes.csv
│   └── processed/          # Schema processado
└── schemas/                # Schemas do Auto Loader
    └── dino_sdk/
        ├── vendas_db/
        └── marketing_db/
```

## 🚨 Pré-requisitos

1. **Schema destino deve existir**
   ```sql
   CREATE SCHEMA IF NOT EXISTS vendas_db;
   ```

2. **Permissões Unity Catalog**
   - SELECT/CREATE TABLE no schema
   - USE CATALOG no catálogo
   - READ/WRITE nos Volumes

3. **Volumes configurados**
   ```sql
   CREATE VOLUME main.landing.volume_name
   LOCATION 's3://your-bucket/landing/';
   ```

## 🔧 Solução de Problemas

### Erro: Schema não existe
```bash
# Criar schema antes da ingestão
CREATE SCHEMA IF NOT EXISTS your_schema;
```

### Erro: Permissões
```bash
# Verificar permissões do usuário
SHOW GRANTS ON SCHEMA your_schema;
```

### Erro: Configuração
```bash
# Validar configuração
dino-config validate

# Reconfigurar
dino-config init
```

## 📈 Monitoramento

### Logs de Execução
- Logs detalhados com timestamps
- Rastreamento de batch IDs
- Métricas de performance

### Consultas de Monitoramento
```sql
-- Últimas ingestões
SELECT 
  _dino_batch_id,
  _dino_ingestion_timestamp,
  COUNT(*) as records,
  _dino_source_file
FROM your_schema.your_table
WHERE _dino_ingestion_timestamp >= CURRENT_DATE - INTERVAL 7 DAY
GROUP BY ALL
ORDER BY _dino_ingestion_timestamp DESC;
```

## 🎯 Exemplos Práticos

### Exemplo 1: E-commerce
```bash
# Ingestão de pedidos com monitoramento automático
dino-ingest \
  --target-schema ecommerce \
  --table-name pedidos \
  --file-path /Volumes/main/landing/pedidos/ \
  --delimiter ',' \
  --is-automated \
  --has-genie \
  --create-job \
  --job-name "Ingestao_Pedidos_Ecommerce"
```

### Exemplo 2: Logs de Sistema
```bash
# Ingestão de logs JSON
dino-ingest \
  --target-schema logs \
  --table-name aplicacao \
  --file-path /Volumes/main/logs/app/ \
  --file-format json \
  --is-automated
```

### Exemplo 3: Dados Financeiros
```bash
# Ingestão batch com merge
dino-ingest \
  --target-schema financeiro \
  --table-name transacoes \
  --file-path /Volumes/main/financeiro/transacoes.parquet \
  --output-mode merge \
  --has-genie
```

## 🆘 Suporte

Para problemas ou dúvidas:

1. **Verificar logs** com `--debug`
2. **Validar configuração** com `dino-config validate`
3. **Consultar documentação** do Databricks Auto Loader
4. **Verificar permissões** Unity Catalog
