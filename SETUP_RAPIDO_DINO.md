# 🦕 DINO SDK - Setup Rápido de Ambiente

Este documento fornece exemplos de código para setup rápido do ambiente Unity Catalog usando o DINO SDK.

## 📋 Setup Básico

### Uso da Função de Conveniência (Método Simples)

```python
# Import necessário
from dino_sdk.schema_manager import ensure_schema_simple

# Parâmetros
CATALOG_NAME = "data_master_dev"  # Seu catálogo
SCHEMA_NAME = "bronze"            # Seu schema

# Setup completo em uma linha (cria schema + volumes padrão)
result = ensure_schema_simple(spark, CATALOG_NAME, SCHEMA_NAME)

# Verificar resultado
if result['success']:
    print("✅ Setup concluído com sucesso!")
    print(f"📦 Volumes criados: {result.get('volumes_created', [])}")
    print(f"📦 Volumes existentes: {result.get('volumes_existing', [])}")
else:
    print("❌ Erro no setup:")
    for error in result.get('errors', []):
        print(f"   {error}")
```

### Uso da Classe SchemaManager (Método Completo)

```python
from dino_sdk.schema_manager import SchemaManager

# Configuração
CATALOG_NAME = "data_master_dev"
SCHEMA_NAME = "bronze"

# Inicializar manager
manager = SchemaManager(CATALOG_NAME, SCHEMA_NAME)

# Verificar se catálogo existe
if not manager.catalog_exists(spark):
    print(f"❌ Catálogo '{CATALOG_NAME}' não encontrado!")
    # Criar catálogo se necessário
    spark.sql(f"CREATE CATALOG IF NOT EXISTS {CATALOG_NAME}")

# Criar schema e volumes
result = manager.ensure_schema_exists(spark)

# Verificar informações completas
info = manager.get_schema_info(spark)
print(f"Schema existe: {info['schema_exists']}")
print(f"Tabelas: {len(info['tables'])}")
```

## 📦 Criação Individual de Volumes

```python
from dino_sdk.schema_manager import SchemaManager

manager = SchemaManager("meu_catalogo", "meu_schema")

# Volumes padrão do DINO SDK
volumes = ['_checkpoints', '_schemas', 'raw']

for volume_name in volumes:
    result = manager.create_volume(spark, volume_name)
    if result['success']:
        print(f"✅ Volume '{volume_name}' OK")
    else:
        print(f"❌ Erro no volume '{volume_name}'")
```

## 🔍 Verificação de Status

```python
from dino_sdk.schema_manager import SchemaManager

manager = SchemaManager("meu_catalogo", "meu_schema")

# Informações completas
info = manager.get_schema_info(spark)

print(f"Catálogo: {info['catalog']}")
print(f"Schema: {info['schema']}")  
print(f"Catálogo existe: {info['catalog_exists']}")
print(f"Schema existe: {info['schema_exists']}")
print(f"External Location: {info['external_location']}")
print(f"Tabelas: {info['tables']}")

# Verificar volumes específicos
volumes_esperados = ['_checkpoints', '_schemas', 'raw']
for volume in volumes_esperados:
    existe = manager.volume_exists(spark, volume)
    print(f"Volume '{volume}': {'✅' if existe else '❌'}")
```

## 🚀 Setup Completo para Produção

```python
from dino_sdk.schema_manager import SchemaManager
from datetime import datetime

def setup_dino_environment(catalog_name: str, schema_name: str):
    """
    Setup completo do ambiente DINO SDK
    """
    print(f"🦕 DINO SDK Setup - {datetime.now()}")
    print("=" * 40)
    
    # Inicializar manager
    manager = SchemaManager(catalog_name, schema_name)
    
    # Verificar pré-requisitos
    print("🔍 Verificando pré-requisitos...")
    if not manager.catalog_exists(spark):
        print(f"❌ Catálogo '{catalog_name}' não existe!")
        return False
    
    # Setup completo
    print("🔧 Configurando ambiente...")
    result = manager.ensure_schema_exists(spark)
    
    if result['success']:
        print("✅ Setup concluído com sucesso!")
        
        # Relatório
        info = manager.get_schema_info(spark)
        print(f"\n📊 Resumo:")
        print(f"   Catálogo: {info['catalog']}")
        print(f"   Schema: {info['schema']}")
        print(f"   Volumes criados: {result.get('volumes_created', [])}")
        print(f"   Volumes existentes: {result.get('volumes_existing', [])}")
        print(f"   Tabelas: {len(info['tables'])}")
        
        return True
    else:
        print("❌ Falha no setup!")
        for error in result.get('errors', []):
            print(f"   {error}")
        return False

# Usar a função
sucesso = setup_dino_environment("data_master_dev", "bronze")
```

## 🎯 Casos de Uso Comuns

### 1. Setup para Development
```python
setup_dino_environment("data_master_dev", "bronze")
setup_dino_environment("data_master_dev", "silver") 
setup_dino_environment("data_master_dev", "gold")
```

### 2. Setup para Production
```python
setup_dino_environment("data_master_prod", "bronze")
setup_dino_environment("data_master_prod", "silver")
setup_dino_environment("data_master_prod", "gold")
```

### 3. Setup Personalizado com External Location
```python
from dino_sdk.schema_manager import SchemaManager

manager = SchemaManager("meu_catalogo", "meu_schema")
result = manager.ensure_schema_exists(
    spark, 
    managed_location="s3://meu-bucket/meu-catalogo/meu-schema/"
)
```

## ⚡ One-Liner para Setup Rápido

```python
# Setup completo em uma linha
from dino_sdk.schema_manager import ensure_schema_simple
ensure_schema_simple(spark, "data_master_dev", "bronze")
```

## 📝 Notas Importantes

1. **Spark Session**: A variável `spark` deve estar disponível (automática no Databricks)
2. **Permissões**: Usuário deve ter permissões para criar schemas e volumes
3. **External Location**: Se o catálogo usa external location, será detectado automaticamente
4. **Volumes Padrão**: `_checkpoints`, `_schemas` e `raw` são criados automaticamente
5. **Idempotência**: Todas as operações são seguras para executar múltiplas vezes
