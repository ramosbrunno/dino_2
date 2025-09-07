# 🦕 DINO SDK - Guia Completo do IngestionEngine

## 📋 Como Executar o IngestionEngine

O **IngestionEngine** é o componente principal do DINO SDK para ingestão de dados usando AutoLoader do Databricks. Este guia mostra como usá-lo de diferentes formas.

## 🚀 1. Uso Básico - Ingestão Simples

### 📝 Exemplo Mínimo
```python
from dino_sdk.ingestion_engine import IngestionEngine, IngestionConfig

# 1. Criar configuração
config = IngestionConfig(
    source_path="/mnt/data/vendas/",          # Caminho dos arquivos
    catalog_name="data_master_dev_dbw",       # Catálogo Unity Catalog
    schema_name="bronze",                     # Schema de destino
    table_name="vendas_2024",                 # Tabela de destino
    file_extension="csv"                      # Formato dos arquivos
)

# 2. Inicializar engine
engine = IngestionEngine()

# 3. Executar ingestão
result = engine.ingest(config)
print(f"✅ Ingestão concluída: {result}")
```

## 🔧 2. Configuração Avançada

### 📊 Exemplo com Todas as Opções
```python
from dino_sdk.ingestion_engine import IngestionEngine, IngestionConfig

# Configuração completa
config = IngestionConfig(
    # === ORIGEM ===
    source_path="/Volumes/data_master_dev_dbw/bronze/raw/vendas/",
    file_extension="csv",
    file_header=True,
    file_delimiter=",",
    
    # === DESTINO ===
    catalog_name="data_master_dev_dbw",
    schema_name="bronze",
    table_name="vendas_detalhadas",
    
    # === EXECUÇÃO ===
    type_run="batch",  # ou "streaming"
    trigger_processing_time="30 seconds",
    
    # === AUTOLOADER ===
    schema_evolution_mode="rescue",  # ou "addNewColumns", "failOnNewColumns"
    multiline=False,
    rescue_data_column="_rescued",
    
    # === METADADOS ===
    add_metadata=True,
    metadata_columns=["_file_path", "_file_modification_time"]
)

# Executar ingestão
engine = IngestionEngine()
result = engine.ingest(config)
```

## 📊 3. Ingestão de Diferentes Formatos

### 🗃️ CSV com Configurações Específicas
```python
config_csv = IngestionConfig(
    source_path="/data/csv_files/",
    catalog_name="meu_catalogo",
    schema_name="bronze",
    table_name="dados_csv",
    file_extension="csv",
    file_header=True,
    file_delimiter=";",  # Delimitador personalizado
    multiline=True       # Para CSVs com quebras de linha
)

engine = IngestionEngine()
result = engine.ingest(config_csv)
```

### 📄 JSON
```python
config_json = IngestionConfig(
    source_path="/data/json_files/",
    catalog_name="meu_catalogo", 
    schema_name="bronze",
    table_name="dados_json",
    file_extension="json",
    schema_evolution_mode="addNewColumns"  # Adicionar colunas automaticamente
)

result = engine.ingest(config_json)
```

### 🗂️ Parquet
```python
config_parquet = IngestionConfig(
    source_path="/data/parquet_files/",
    catalog_name="meu_catalogo",
    schema_name="bronze", 
    table_name="dados_parquet",
    file_extension="parquet"
)

result = engine.ingest(config_parquet)
```

## 🔄 4. Ingestão Streaming

### ⚡ Processamento em Tempo Real
```python
# Configuração para streaming
config_streaming = IngestionConfig(
    source_path="/data/streaming/",
    catalog_name="data_master_dev_dbw",
    schema_name="bronze",
    table_name="eventos_tempo_real",
    file_extension="json",
    type_run="streaming",           # Modo streaming
    trigger_processing_time="5 seconds"  # Processar a cada 5 segundos
)

engine = IngestionEngine()
result = engine.ingest(config_streaming)

# Para streaming, você obtém informações do stream
print(f"Stream ID: {result['stream_id']}")
print(f"Status: {result['status']}")
```

## 🛠️ 5. Uso em Notebooks Databricks

### 📓 Exemplo Completo para Notebook
```python
# Célula 1: Configuração
from dino_sdk.ingestion_engine import IngestionEngine, IngestionConfig

# Parâmetros do notebook (podem ser widgets)
catalog_name = "data_master_dev_dbw"
schema_name = "bronze_test_volumes" 
table_name = "vendas_2024"
source_path = "/Volumes/data_master_dev_dbw/bronze_test_volumes/raw/vendas_2024/"

# Célula 2: Criar configuração
config = IngestionConfig(
    source_path=source_path,
    catalog_name=catalog_name,
    schema_name=schema_name,
    table_name=table_name,
    file_extension="parquet",
    add_metadata=True
)

# Célula 3: Executar ingestão
engine = IngestionEngine()
print("🚀 Iniciando ingestão...")

result = engine.ingest(config)

if result["success"]:
    print(f"✅ Sucesso! Tabela: {result['table']}")
    print(f"📊 Modo: {result['mode']}")
    print(f"💬 Mensagem: {result['message']}")
else:
    print(f"❌ Erro: {result['error']}")

# Célula 4: Verificar resultado
table_name_full = f"{catalog_name}.{schema_name}.{table_name}"
count = spark.sql(f"SELECT COUNT(*) as total FROM {table_name_full}").collect()[0]['total']
print(f"📊 Total de registros ingeridos: {count}")

# Mostrar sample dos dados
display(spark.sql(f"SELECT * FROM {table_name_full} LIMIT 10"))
```

## 🎯 6. Ingestão com Validação e Error Handling

### 🛡️ Exemplo Robusto
```python
from dino_sdk.ingestion_engine import IngestionEngine, IngestionConfig
import logging

def ingest_with_validation(source_path, catalog, schema, table):
    """Ingestão com validação completa"""
    
    try:
        # 1. Configurar logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        # 2. Criar configuração
        config = IngestionConfig(
            source_path=source_path,
            catalog_name=catalog,
            schema_name=schema,
            table_name=table,
            file_extension="csv",
            add_metadata=True
        )
        
        # 3. Validar antes de iniciar
        logger.info("🔍 Validando configuração...")
        engine = IngestionEngine()
        
        # 4. Executar ingestão
        logger.info("🚀 Iniciando ingestão...")
        result = engine.ingest(config)
        
        # 5. Verificar resultado
        if result["success"]:
            logger.info(f"✅ Ingestão concluída: {result['table']}")
            
            # Validar dados inseridos
            table_full = f"{catalog}.{schema}.{table}"
            count = spark.sql(f"SELECT COUNT(*) as total FROM {table_full}").collect()[0]['total']
            
            if count > 0:
                logger.info(f"📊 {count} registros inseridos com sucesso")
                return {"status": "success", "records": count}
            else:
                logger.warning("⚠️ Nenhum registro encontrado após ingestão")
                return {"status": "warning", "records": 0}
        else:
            logger.error(f"❌ Falha na ingestão: {result.get('error', 'Erro desconhecido')}")
            return {"status": "error", "error": result.get('error')}
            
    except Exception as e:
        logger.error(f"💥 Exceção durante ingestão: {str(e)}")
        return {"status": "exception", "error": str(e)}

# Usar a função
result = ingest_with_validation(
    source_path="/data/vendas/",
    catalog="data_master_dev_dbw",
    schema="bronze",
    table="vendas_validadas"
)

print(f"Resultado: {result}")
```

## 🔄 7. Ingestão Batch vs Streaming

### 📊 Comparação de Modos

| Aspecto | Batch | Streaming |
|---------|-------|-----------|
| **Uso** | Cargas pontuais | Dados em tempo real |
| **Performance** | Alta para volumes grandes | Baixa latência |
| **Recursos** | Temporários | Contínuos |
| **Monitoramento** | Por execução | Por stream |

### 📝 Exemplo de Escolha
```python
def choose_ingestion_mode(data_frequency, latency_requirement):
    """Escolhe o modo de ingestão baseado nos requisitos"""
    
    if latency_requirement == "real_time":
        return "streaming"
    elif data_frequency == "daily" or data_frequency == "hourly":
        return "batch"
    else:
        return "streaming"  # Default para casos não claros

# Configuração dinâmica
mode = choose_ingestion_mode("hourly", "batch_ok")

config = IngestionConfig(
    source_path="/data/",
    catalog_name="meu_catalogo",
    schema_name="bronze",
    table_name="dados_dinamicos",
    type_run=mode  # "batch" ou "streaming"
)

engine = IngestionEngine()
result = engine.ingest(config)
```

## 🎛️ 8. Configurações Avançadas

### ⚙️ Schema Evolution
```python
# Configuração para evolução automática de schema
config = IngestionConfig(
    source_path="/data/evolving/",
    catalog_name="meu_catalogo",
    schema_name="bronze",
    table_name="schema_evolutivo",
    schema_evolution_mode="addNewColumns",  # Adiciona colunas automaticamente
    rescue_data_column="_dados_nao_mapeados"
)
```

### 🏷️ Metadados Personalizados
```python
config = IngestionConfig(
    source_path="/data/com_metadata/",
    catalog_name="meu_catalogo",
    schema_name="bronze",
    table_name="com_metadados",
    add_metadata=True,
    metadata_columns=[
        "_file_path",           # Caminho do arquivo
        "_file_modification_time",  # Data de modificação
        "_file_size"            # Tamanho do arquivo
    ]
)
```

## 📊 9. Monitoramento e Logs

### 📋 Verificação de Status
```python
# Após ingestão, verificar status
result = engine.ingest(config)

if result["success"]:
    if result["mode"] == "streaming":
        # Para streaming, monitorar o stream
        stream_id = result["stream_id"]
        print(f"🔄 Stream ativo: {stream_id}")
        
        # Verificar status periodicamente
        import time
        time.sleep(10)
        
        # Status do stream (código conceitual)
        # stream_status = spark.streams.get(stream_id).status
        # print(f"📊 Status: {stream_status}")
    else:
        # Para batch, verificar tabela final
        table_full = f"{config.catalog_name}.{config.schema_name}.{config.table_name}"
        count = spark.sql(f"SELECT COUNT(*) FROM {table_full}").collect()[0][0]
        print(f"📊 Total processado: {count} registros")
```

## 🚨 10. Troubleshooting Comum

### ❌ Erros Frequentes e Soluções

```python
def handle_ingestion_errors():
    """Exemplos de tratamento de erros comuns"""
    
    try:
        config = IngestionConfig(...)
        engine = IngestionEngine()
        result = engine.ingest(config)
        
    except ValueError as e:
        if "table_name é obrigatório" in str(e):
            print("🔧 Solução: Fornecer table_name na configuração")
        elif "source_path não existe" in str(e):
            print("🔧 Solução: Verificar se o caminho fonte está correto")
            
    except Exception as e:
        if "Schema não encontrado" in str(e):
            print("🔧 Solução: Criar o schema primeiro ou usar schema_manager")
        elif "Permissão negada" in str(e):
            print("🔧 Solução: Verificar permissões no Unity Catalog")
        else:
            print(f"💥 Erro não tratado: {str(e)}")
```

## 🎯 Resumo - Pontos Importantes

### ✅ **Vantagens do IngestionEngine**
- 🚀 **AutoLoader integrado** - Detecta novos arquivos automaticamente
- 🔄 **Batch e Streaming** - Flexibilidade para diferentes cenários
- 📊 **Unity Catalog** - Integração nativa com catálogo
- 🛡️ **Schema Evolution** - Adaptação automática a mudanças
- 📋 **Metadados** - Rastreabilidade completa dos dados

### 🎛️ **Configurações Essenciais**
- `source_path` - Onde estão os dados
- `catalog_name`, `schema_name`, `table_name` - Destino no Unity Catalog
- `file_extension` - Formato dos arquivos (csv, json, parquet)
- `type_run` - Modo de execução (batch vs streaming)

### 🚀 **Próximos Passos**
1. Experimentar com seus dados
2. Ajustar configurações conforme necessidade
3. Implementar monitoramento adequado
4. Considerar automação via jobs do Databricks

---

**🦕 DINO SDK IngestionEngine - Pronto para Ingestão de Dados!**
