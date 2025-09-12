# 🔧 Solução para Erro de Incompatibilidade de Schema Delta

## ❌ Problema: DELTA_MERGE_INCOMPATIBLE_DATATYPE

O erro acontece porque:

1. **Tabela existente** foi criada com `file_size: BIGINT` (LongType)
2. **DataFrame novo** tinha `file_size` como `IntegerType` 
3. **Delta não consegue** fazer merge entre LongType ↔ IntegerType

### Erro Específico:
```
[DELTA_MERGE_INCOMPATIBLE_DATATYPE] Failed to merge incompatible data types LongType and IntegerType
```

## ✅ Correção Implementada

### 1. **Tipos Corrigidos no save_data_as_batch():**
```python
# ❌ Antes (causava erro):
lit(0).alias("file_size")              # IntegerType
lit(0).alias("file_block_start")       # IntegerType  
lit(0).alias("file_block_length")      # IntegerType

# ✅ Agora (compatível):
lit(0).cast(LongType()).alias("file_size")           # LongType = BIGINT
lit(0).cast(LongType()).alias("file_block_start")    # LongType = BIGINT
lit(0).cast(LongType()).alias("file_block_length")   # LongType = BIGINT
```

### 2. **Mapeamento de Tipos Spark ↔ SQL:**
| SQL (CREATE TABLE) | Spark Type | Python lit() padrão | Correção necessária |
|-------------------|------------|----------------------|---------------------|
| `BIGINT` | `LongType` | `IntegerType` | `.cast(LongType())` |
| `STRING` | `StringType` | `StringType` | ✅ Ok |
| `TIMESTAMP` | `TimestampType` | `TimestampType` | ✅ Ok |

## 🚀 Soluções Disponíveis

### **Opção 1: Reinstalar wheel atualizado (Recomendado)**
```bash
%pip install /path/to/dino_sdk-1.2.0-py3-none-any.whl --force-reinstall
```
Agora o `save_data_as_batch()` usa os tipos corretos.

### **Opção 2: Remover tabela existente (Se persistir erro)**
Se ainda houver erro, execute antes da Célula 8:
```python
# Remover tabela com schema incompatível
table_name = f"{base_config.catalog_name}.{base_config.schema_name}.{base_config.table_name}"
spark.sql(f"DROP TABLE IF EXISTS {table_name}")
print(f"Tabela {table_name} removida para recriação com schema correto")
```

### **Opção 3: Usar nome de tabela diferente**
```python
# Célula 6 - Mudar nome da tabela para evitar conflito
base_config.table_name = "sales_test_fixed_v2"  # Nome diferente
```

## 📋 Próximos Passos

1. **Instalar wheel corrigido:**
   ```bash
   %pip install /caminho/do/dino_sdk-1.2.0-py3-none-any.whl --force-reinstall
   ```

2. **Executar Célula 8 novamente** - deve funcionar com tipos corretos

3. **Se ainda houver erro:** Use Opção 2 para limpar tabela existente

## 💡 Verificação dos Tipos

Para confirmar que os tipos estão corretos, você pode verificar o schema:
```python
# Verificar schema do DataFrame antes do save
df_with_metadata = df.withColumn("dino_ingestion_date", current_date()) \
                    .withColumn("dino_ingestion_timestamp", current_timestamp()) \
                    .withColumn("dino_metadata", struct(
                        lit("notebook_batch").alias("file_path"),
                        lit("batch_operation").alias("file_name"),
                        lit(0).cast("bigint").alias("file_size"),  # Explícito como bigint
                        lit(0).cast("bigint").alias("file_block_start"),
                        lit(0).cast("bigint").alias("file_block_length"),
                        current_timestamp().alias("file_modification_time")
                    ))

print("Schema do dino_metadata:")
df_with_metadata.select("dino_metadata").printSchema()
```

Isso deve resolver o problema de compatibilidade de tipos!
