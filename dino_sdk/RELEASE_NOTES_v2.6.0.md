# DINO SDK v2.6.0 - Melhorias no Sistema de Logging

## 🎯 Objetivo da Release
Implementar as melhorias solicitadas no sistema de logging para torná-lo mais preciso e informativo, com foco nas necessidades específicas de monitoramento e auditoria.

## 🆕 Melhorias Implementadas

### 1. ❌ Removido Campo `destination_path`
**Motivação**: O destino é a tabela, tornando esse campo redundante
**Implementação**:
- Removido da estrutura da tabela de logs
- Removido da classe `IngestionLogEntry`
- Atualizado todos os métodos de inserção e atualização

### 2. ✅ Campo `execution_status` Garantido
**Problema**: Status não sendo atualizado corretamente no final
**Solução**:
- Garantido que `update_ingestion_log_success()` define status como `'concluido_sucesso'`
- Garantido que `update_ingestion_log_error()` define status como `'concluido_erro'`
- Status inicial sempre `'iniciado'`

### 3. ⏰ Campos de Horário Claros
**Implementado**:
- `start_time`: Timestamp de início da execução
- `end_time`: Timestamp de fim da execução (atualizado no sucesso/erro)
- `execution_duration_seconds`: Duração calculada automaticamente

### 4. 💬 Campo `message` Adicionado
**Funcionalidade**:
- **Sucesso**: `"Ingestão concluída com sucesso. X registros lidos, Y registros gravados."`
- **Erro**: `"Ingestão falhou com erro: [primeiros 200 chars do erro]"`
- **Início**: `"Ingestão iniciada com sucesso"`

### 5. 📊 Campos de Volume de Dados
**Implementado**:
- `records_read`: Total de linhas lidas da origem
- `records_written`: Total de linhas gravadas na tabela
- Contagem automática para modo batch
- Métricas aproximadas para modo streaming

### 6. 📁 Campo `files_ingested`
**Funcionalidade**:
- Lista dos nomes dos arquivos lidos na ingestão
- Limitado a 10 arquivos (para não ficar muito longo)
- Indica se há mais arquivos: `"arquivo1.csv, arquivo2.csv, ... (+ 5 mais)"`
- Suporta wildcards e múltiplos arquivos

### 7. 💾 Campo `file_size_bytes`
**Implementado**:
- Tamanho total dos arquivos lidos em bytes
- Obtido via `dbutils.fs.ls()` quando possível
- Fallback gracioso quando não disponível

## 🔧 Nova Estrutura da Tabela

```sql
CREATE TABLE IF NOT EXISTS catalog.schema.ingestion_logs (
    execution_id STRING NOT NULL,           -- ID único da execução
    table_name STRING NOT NULL,             -- Nome da tabela de destino
    schema_name STRING NOT NULL,            -- Schema da tabela
    catalog_name STRING NOT NULL,           -- Catalog da tabela
    source_path STRING NOT NULL,            -- Path da origem dos dados
    execution_status STRING NOT NULL,       -- iniciado | concluido_sucesso | concluido_erro
    start_time TIMESTAMP NOT NULL,          -- Horário de início
    end_time TIMESTAMP,                     -- Horário de fim
    execution_duration_seconds DOUBLE,      -- Duração em segundos
    records_read BIGINT,                    -- Total de registros lidos
    records_written BIGINT,                 -- Total de registros gravados
    file_format STRING,                     -- Formato do arquivo (csv, parquet, etc.)
    ingestion_type STRING,                  -- Tipo de ingestão (batch, streaming)
    message STRING,                         -- Mensagem descritiva
    error_message STRING,                   -- Mensagem de erro (se houver)
    error_stack_trace STRING,               -- Stack trace do erro (se houver)
    files_ingested STRING,                  -- Nomes dos arquivos ingeridos
    file_size_bytes BIGINT,                 -- Tamanho total dos arquivos
    additional_metadata STRING,             -- Metadados adicionais (JSON-like)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()  -- Timestamp de criação
)
USING DELTA
```

## 📊 Exemplos de Logs

### Log de Sucesso
```json
{
    "execution_id": "550e8400-e29b-41d4-a716-446655440000",
    "table_name": "vendas",
    "schema_name": "bronze",
    "catalog_name": "dev",
    "source_path": "/mnt/data/vendas/*.csv",
    "execution_status": "concluido_sucesso",
    "start_time": "2025-09-08T10:00:00Z",
    "end_time": "2025-09-08T10:02:30Z",
    "execution_duration_seconds": 150.5,
    "records_read": 10000,
    "records_written": 9850,
    "file_format": "csv",
    "ingestion_type": "batch",
    "message": "Ingestão concluída com sucesso. 10000 registros lidos, 9850 registros gravados.",
    "files_ingested": "vendas_2024_01.csv, vendas_2024_02.csv, vendas_2024_03.csv",
    "file_size_bytes": 52428800,
    "error_message": null,
    "error_stack_trace": null
}
```

### Log de Erro
```json
{
    "execution_id": "550e8400-e29b-41d4-a716-446655440001",
    "execution_status": "concluido_erro",
    "start_time": "2025-09-08T10:05:00Z",
    "end_time": "2025-09-08T10:05:45Z",
    "execution_duration_seconds": 45.2,
    "message": "Ingestão falhou com erro: Schema validation failed - column 'data_venda' not found",
    "error_message": "Schema validation failed - column 'data_venda' not found in source data",
    "error_stack_trace": "Traceback (most recent call last):\n  File ...",
    "files_ingested": "dados_incorretos.csv",
    "file_size_bytes": 1048576
}
```

## 🔍 Funcionalidades Inteligentes

### Detecção de Arquivos
```python
def _get_file_info(self, source_path: str) -> Dict[str, Any]:
    # 1. Tenta usar dbutils.fs.ls() para obter informações completas
    # 2. Fallback para análise com Spark quando wildcards
    # 3. Fallback final para extrair nome do path
    return {
        "files": "arquivo1.csv, arquivo2.csv",
        "file_count": 2,
        "total_size": 10485760,
        "has_more_files": False
    }
```

### Cálculo de Métricas
```python
# Para batch: contagem real
records_read = df.count()

# Para streaming: aproximado
records_read = None  # Será preenchido conforme dados chegam
```

## 🚀 Como Usar

### 1. Instalar Nova Versão
```bash
pip install dist/dino_sdk-2.6.0-py3-none-any.whl --force-reinstall
```

### 2. Uso Automático
```python
from dino_sdk import IngestionEngine

engine = IngestionEngine()
result = engine.ingest(config)
# Logs são salvos automaticamente com todas as informações
```

### 3. Consultar Logs
```sql
-- Logs de sucesso nas últimas 24 horas
SELECT execution_id, table_name, message, records_read, records_written,
       execution_duration_seconds, files_ingested, file_size_bytes
FROM dev.bronze.ingestion_logs 
WHERE execution_status = 'concluido_sucesso'
  AND start_time >= current_timestamp() - INTERVAL '24 HOURS'
ORDER BY start_time DESC;

-- Logs de erro
SELECT execution_id, table_name, message, error_message, 
       files_ingested, execution_duration_seconds
FROM dev.bronze.ingestion_logs 
WHERE execution_status = 'concluido_erro'
ORDER BY start_time DESC
LIMIT 10;
```

## ⚡ Melhorias de Performance

- **Contagem Inteligente**: Para batch, conta registros apenas quando necessário
- **Limitação de Strings**: Mensagens de erro limitadas para evitar logs gigantes
- **Fallback Gracioso**: Continua funcionando mesmo se algumas métricas falharem
- **Cache de Informações**: Reutiliza informações de arquivos quando possível

## 🎯 Compatibilidade

- ✅ **Totalmente compatível** com versões anteriores (novos campos opcionais)
- ✅ **Unity Catalog**: Logs salvos em tabela Delta
- ✅ **Sem Unity Catalog**: Logs estruturados no console
- ✅ **Batch e Streaming**: Métricas adequadas para cada modo

---

**Versão**: 2.6.0  
**Data**: September 8, 2025  
**Autor**: DINO SDK Team  
**Status**: ✅ Pronto para Produção

## 🔄 Migration Notes

Se você tem logs da v2.5.x, a tabela será automaticamente atualizada com os novos campos na primeira execução. Logs antigos terão valores `NULL` nos novos campos, o que é normal e esperado.
