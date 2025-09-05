# exemplo_schema_manager.py
"""
DINO SDK v1.2.0 - Exemplo de uso do SchemaManager e comando create-schema
Demonstra como criar schemas usando tanto a classe quanto o CLI
"""

from pyspark.sql import SparkSession
from src.dino_sdk.schema_manager import SchemaManager, create_schema_simple


def exemplo_uso_classe_schema_manager():
    """
    Exemplo usando a classe SchemaManager diretamente em notebook Databricks
    """
    print("🦕 Exemplo: Usando SchemaManager em Notebook")
    print("=" * 50)
    
    # Em notebook Databricks, spark já está disponível globalmente
    # spark = SparkSession.getActiveSession()  # ou usar spark global
    
    # Exemplo com diferentes cenários
    exemplos = [
        {"catalog": "main", "schema": "bronze_vendas", "descricao": "Schema para dados brutos de vendas"},
        {"catalog": "main", "schema": "silver_vendas", "descricao": "Schema para dados refinados de vendas"},
        {"catalog": "analytics", "schema": "gold_reports", "descricao": "Schema para relatórios finais"},
    ]
    
    for exemplo in exemplos:
        print(f"\n📊 Criando: {exemplo['catalog']}.{exemplo['schema']}")
        print(f"   Descrição: {exemplo['descricao']}")
        
        # Método 1: Usando a classe
        manager = SchemaManager(exemplo['catalog'], exemplo['schema'])
        
        # Em notebook real, substituir 'spark' pela sessão disponível
        # result = manager.create_schema(spark)
        print(f"   Código: manager = SchemaManager('{exemplo['catalog']}', '{exemplo['schema']}')")
        print(f"   Código: result = manager.create_schema(spark)")
        
        # Método 2: Usando função de conveniência  
        # result = create_schema_simple(spark, exemplo['catalog'], exemplo['schema'])
        print(f"   Alternativa: create_schema_simple(spark, '{exemplo['catalog']}', '{exemplo['schema']}')")


def exemplo_uso_cli_create_schema():
    """
    Exemplos de uso do comando CLI create-schema
    """
    print("\n🖥️ Exemplo: Usando CLI create-schema")
    print("=" * 40)
    
    comandos_exemplo = [
        {
            "cmd": "dino-config create-schema --catalog-name main --schema-name bronze",
            "desc": "Criar schema bronze no catálogo main (usa external location automática)"
        },
        {
            "cmd": "dino-config create-schema --catalog-name vendas --schema-name silver",
            "desc": "Criar schema silver no catálogo vendas"
        },
        {
            "cmd": "dino-config create-schema --catalog-name main --schema-name gold --managed-location 'abfss://gold@storage.dfs.core.windows.net/gold/'",
            "desc": "Criar schema com localização gerenciada específica"
        }
    ]
    
    for i, exemplo in enumerate(comandos_exemplo, 1):
        print(f"\n{i}. {exemplo['desc']}")
        print(f"   Comando: {exemplo['cmd']}")


def exemplo_workflow_completo():
    """
    Exemplo de workflow completo usando SchemaManager
    """
    print("\n🔄 Exemplo: Workflow Completo de Schema")
    print("=" * 45)
    
    workflow_steps = [
        "1. Verificar se catálogo existe",
        "2. Criar schema se não existir", 
        "3. Obter informações do schema",
        "4. Listar tabelas existentes",
        "5. Configurar para uso em pipelines"
    ]
    
    print("Passos do workflow:")
    for step in workflow_steps:
        print(f"   {step}")
    
    print(f"\nCódigo exemplo:")
    print(f"""
# Em notebook Databricks:
from src.dino_sdk.schema_manager import SchemaManager

# Configurar schema para projeto
catalog_name = "main"
schema_name = "bronze_vendas"
manager = SchemaManager(catalog_name, schema_name)

# 1. Verificar catálogo
if not manager.catalog_exists(spark):
    print(f"❌ Catálogo {{catalog_name}} não existe")
    exit()

# 2. Criar schema
result = manager.create_schema(spark)
if result['success']:
    print(f"✅ Schema criado: {{catalog_name}}.{{schema_name}}")
    
# 3. Obter informações
info = manager.get_schema_info(spark)
print(f"📊 Tabelas no schema: {{len(info['tables'])}}")

# 4. Usar em pipeline
df = spark.read.csv("caminho/dados.csv")
df.write.mode("overwrite").saveAsTable(f"{{catalog_name}}.{{schema_name}}.tabela_vendas")
""")


def exemplo_casos_uso_reais():
    """
    Exemplos de casos de uso reais
    """
    print("\n🎯 Casos de Uso Reais")
    print("=" * 25)
    
    casos = [
        {
            "nome": "Pipeline Bronze/Silver/Gold",
            "schemas": ["bronze", "silver", "gold"],
            "uso": "Arquitetura medalion para data lake"
        },
        {
            "nome": "Multi-tenant por Departamento", 
            "schemas": ["vendas", "marketing", "rh", "financeiro"],
            "uso": "Isolamento de dados por departamento"
        },
        {
            "nome": "Ambiente de Desenvolvimento",
            "schemas": ["dev_bronze", "dev_silver", "staging"],
            "uso": "Separação de ambientes de desenvolvimento"
        }
    ]
    
    for caso in casos:
        print(f"\n📋 {caso['nome']}")
        print(f"   Uso: {caso['uso']}")
        print(f"   Schemas: {', '.join(caso['schemas'])}")
        
        # Comandos CLI para cada schema
        for schema in caso['schemas']:
            print(f"   CLI: dino-config create-schema --catalog-name main --schema-name {schema}")


if __name__ == "__main__":
    print("🦕 DINO SDK v1.2.0 - SchemaManager Examples")
    print("=" * 60)
    
    exemplo_uso_classe_schema_manager()
    exemplo_uso_cli_create_schema()
    exemplo_workflow_completo()
    exemplo_casos_uso_reais()
    
    print(f"\n🎉 SchemaManager: Criação de schemas simplificada!")
    print(f"   • Use em notebooks: SchemaManager(catalog, schema).create_schema(spark)")
    print(f"   • Use via CLI: dino-config create-schema --catalog-name X --schema-name Y") 
    print(f"   • Suporte a external locations automáticas")
    print(f"   • Verificação de existência integrada")
    print(f"   • Informações detalhadas de schemas")
