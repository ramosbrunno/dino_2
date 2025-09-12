# 🔧 Solução: Erro de Tabela Temporária não Encontrada

## ❌ Problema Identificado

O erro `[TABLE_OR_VIEW_NOT_FOUND] The table or view temp_batch_read_xxx cannot be found` acontecia porque:

1. **Memory sink inconsistente**: O formato `memory` para streaming não garantia que a tabela temporária ficasse disponível no contexto SQL do Spark
2. **Timing issues**: A tabela temporária era removida antes da consulta ser executada
3. **Problemas de contexto**: Tables criadas via `memory` format podem não estar visíveis em todas as sessões

## ✅ Nova Solução Implementada

### Estratégia `foreachBatch` com Global Temp Views

```python
def read_data_as_batch(spark: SparkSession, config: IngestionConfig) -> DataFrame:
    """
    Lê dados usando AutoLoader e converte para DataFrame batch usando:
    1. AutoLoader streaming
    2. foreachBatch para capturar microbatches
    3. Global Temp Views para persistir dados
    4. Fallback para CSV simples se necessário
    """
```

### Como Funciona:

1. **AutoLoader Stream**: Usa o AutoLoader normal para ler dados
2. **foreachBatch**: Processa cada microbatch individualmente
3. **Global Temp View**: Cada batch é salvo em `global_temp.temp_table_name`
4. **availableNow=True**: Processa todos os arquivos disponíveis uma vez só
5. **Batch DataFrame**: Retorna DataFrame batch para operações como `.count()`

### Vantagens:

- ✅ **Mais robusto**: Usa Global Temp Views que persistem entre sessões
- ✅ **Fallback duplo**: Local temp view + CSV simples se AutoLoader falhar  
- ✅ **Melhor logging**: Acompanha cada etapa do processo
- ✅ **Compatibilidade**: Funciona em notebooks e cluster jobs

## 🚀 Como Usar (Atualizado)

### 1. Instalar o Wheel Atualizado

```bash
%pip install /path/to/dino_sdk-1.2.0-py3-none-any.whl --force-reinstall
```

### 2. Usar o Método Correto na Célula 7

**❌ Método Antigo (causava erro):**
```python
df = DataReader.read_data(spark, base_config)
```

**✅ Método Novo (funciona):**
```python
# Importar
from dino_sdk.ingestion_engine import DataReader

# Usar read_data_as_batch para notebook operations
df = DataReader.read_data_as_batch(spark, base_config)
print(f"   Registros lidos: {df.count()}")  # Agora funciona!
```

### 3. Exemplo Completo

```python
# Célula 7 - Teste DataReader com Schema Location
print("=== Test DataReader com Schema Location ===")

try:
    print(f"Lendo dados de: {base_config.source_path}")
    
    # Usar método específico para batch operations
    df = DataReader.read_data_as_batch(spark, base_config)
    
    print("✅ Data read successful com schema location configurado")
    print(f"   Schema location será: {base_config.schema_location}")
    print(f"   Registros lidos: {df.count()}")
    print(f"   Colunas: {', '.join(df.columns)}")
    
    # Mostrar algumas linhas
    df.show(5, truncate=False)
    
except Exception as e:
    print(f"❌ Erro no DataReader: {str(e)}")
```

## 🔧 Detalhes Técnicos

### Fluxo de Processamento:

1. **Stream Setup**: AutoLoader configura o stream com cloudFiles
2. **Micro-batch Processing**: Cada arquivo/batch é processado via `foreachBatch`
3. **Temp View Creation**: Dados são salvos em `global_temp.temp_table_xxx`
4. **Batch Conversion**: Stream é convertido para DataFrame batch
5. **Cleanup**: Views temporárias são limpas automaticamente

### Fallbacks Implementados:

1. **Global Temp View** → Local Temp View → CSV Simples
2. **AutoLoader** → CSV Reader nativo do Spark
3. **Error Handling**: Logs detalhados em cada etapa

## 📝 Próximos Passos

1. **Instale o wheel atualizado**
2. **Modifique a Célula 7** para usar `read_data_as_batch()`
3. **Execute o teste** - deve funcionar sem erros
4. **Verifique os logs** - agora com mais detalhes

## 💡 Notas Importantes

- **Para notebooks**: Use sempre `read_data_as_batch()` quando precisar fazer `.count()`, `.show()`, etc.
- **Para pipelines**: Use `read_data()` normal para streaming contínuo
- **Performance**: `read_data_as_batch()` processa todos os dados na memória - adequado para testes e datasets pequenos/médios
- **Logs**: Acompanhe os logs para ver qual estratégia está sendo usada (AutoLoader + foreachBatch ou fallback CSV)
