"""
🦕 DINO SDK v1.2.0 - Exemplo de Uso no Databricks
Demonstra como usar o SDK corretamente no ambiente Databricks
"""

# Exemplo 1: Usar função programática (RECOMENDADO)
def exemplo_criar_schema_programatico():
    """
    Exemplo de criação de schema usando função programática
    Use esta abordagem diretamente no notebook Databricks
    """
    
    print("🦕 DINO SDK v1.2.0 - Criação de Schema (Programático)")
    print("=" * 55)
    
    # Parâmetros de configuração
    catalog_name = "vendas"
    schema_name = "bronze"
    
    try:
        # No Databricks, a variável 'spark' está disponível globalmente
        print(f"📊 Catálogo: {catalog_name}")
        print(f"📋 Schema: {schema_name}")
        
        # Verificar se o catálogo existe
        print(f"\n🔍 Verificando catálogo '{catalog_name}'...")
        try:
            spark.sql(f"DESCRIBE CATALOG {catalog_name}").collect()
            print(f"✅ Catálogo '{catalog_name}' encontrado")
        except Exception as e:
            print(f"❌ Catálogo '{catalog_name}' não encontrado: {e}")
            return False
        
        # Obter external location
        print(f"🔍 Obtendo external location...")
        external_location = spark.sql(f"DESCRIBE EXTERNAL LOCATION {catalog_name}").select("url").collect()[0].url
        schema_location = f"{external_location}/{catalog_name}/{schema_name}/"
        
        print(f"✅ External Location: {external_location}")
        print(f"📍 Schema Location: {schema_location}")
        
        # Criar schema usando a sintaxe exata especificada
        print(f"\n📊 Criando schema '{catalog_name}.{schema_name}'...")
        
        spark.sql(f"""
            CREATE SCHEMA IF NOT EXISTS {catalog_name}.{schema_name}
            MANAGED LOCATION '{schema_location}'
        """)
        
        print(f"✅ Schema '{catalog_name}.{schema_name}' criado com sucesso!")
        
        # Verificar se foi criado
        print(f"\n🔍 Verificando criação...")
        result = spark.sql(f"DESCRIBE SCHEMA {catalog_name}.{schema_name}").collect()
        print(f"✅ Schema verificado: {len(result)} propriedades encontradas")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


# Exemplo 2: Usar comando CLI
def exemplo_cli_setup():
    """
    Exemplo de uso do comando CLI (execute no terminal do Databricks)
    """
    
    comando = """
# No terminal do notebook Databricks:

%pip install /dbfs/FileStore/shared_uploads/dino_sdk-1.2.0-py3-none-any.whl
dbutils.library.restartPython()

# Depois execute:
!dino-config setup \
  --project-name bronze \
  --storage-name mystorageaccount \
  --catalog-name vendas \
  --schema-name bronze
"""
    
    print("🦕 DINO SDK v1.2.0 - Exemplo CLI")
    print("=" * 40)
    print(comando)


# Exemplo 3: Configuração completa do projeto
def exemplo_configuracao_completa():
    """
    Exemplo de configuração completa de um projeto
    """
    
    print("🦕 DINO SDK v1.2.0 - Configuração Completa")
    print("=" * 50)
    
    # Configurações do projeto
    projeto_config = {
        'project_name': 'vendas_analytics',
        'storage_name': 'vendasstorage',
        'catalog_name': 'vendas',
        'schemas': ['bronze', 'silver', 'gold']
    }
    
    print(f"🏢 Projeto: {projeto_config['project_name']}")
    print(f"💾 Storage: {projeto_config['storage_name']}")
    print(f"📁 Catálogo: {projeto_config['catalog_name']}")
    print(f"📊 Schemas: {', '.join(projeto_config['schemas'])}")
    
    # Criar todos os schemas
    for schema_name in projeto_config['schemas']:
        print(f"\n📋 Criando schema: {schema_name}")
        
        try:
            # Obter external location
            external_location = spark.sql(f"DESCRIBE EXTERNAL LOCATION {projeto_config['catalog_name']}").select("url").collect()[0].url
            schema_location = f"{external_location}/{projeto_config['catalog_name']}/{schema_name}/"
            
            # Criar schema
            spark.sql(f"""
                CREATE SCHEMA IF NOT EXISTS {projeto_config['catalog_name']}.{schema_name}
                MANAGED LOCATION '{schema_location}'
            """)
            
            print(f"✅ Schema {projeto_config['catalog_name']}.{schema_name} criado")
            print(f"   📍 Localização: {schema_location}")
            
        except Exception as e:
            print(f"❌ Erro ao criar {schema_name}: {e}")
    
    print(f"\n🎉 Configuração do projeto '{projeto_config['project_name']}' concluída!")


# Exemplo 4: Validação de configuração
def exemplo_validacao():
    """
    Exemplo de validação de configuração
    """
    
    print("🦕 DINO SDK v1.2.0 - Validação")
    print("=" * 40)
    
    catalog_name = "vendas"
    schemas = ["bronze", "silver", "gold"]
    
    print(f"🔍 Validando catálogo: {catalog_name}")
    
    try:
        # Verificar catálogo
        spark.sql(f"DESCRIBE CATALOG {catalog_name}").collect()
        print(f"✅ Catálogo '{catalog_name}' existe")
        
        # Verificar cada schema
        for schema_name in schemas:
            try:
                spark.sql(f"DESCRIBE SCHEMA {catalog_name}.{schema_name}").collect()
                print(f"✅ Schema '{catalog_name}.{schema_name}' existe")
            except:
                print(f"❌ Schema '{catalog_name}.{schema_name}' NÃO existe")
        
        print(f"\n🎉 Validação concluída!")
        
    except Exception as e:
        print(f"❌ Erro na validação: {e}")


if __name__ == "__main__":
    print("🦕 DINO SDK v1.2.0 - Exemplos de Uso no Databricks")
    print("=" * 60)
    print()
    print("Para usar, copie as funções para seu notebook Databricks:")
    print()
    print("1. exemplo_criar_schema_programatico()")
    print("2. exemplo_cli_setup()")
    print("3. exemplo_configuracao_completa()")
    print("4. exemplo_validacao()")
    print()
    print("⚠️  IMPORTANTE: Execute no ambiente Databricks onde 'spark' está disponível")
