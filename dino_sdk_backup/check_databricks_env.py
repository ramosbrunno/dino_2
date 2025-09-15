#!/usr/bin/env python3
"""
Diagnóstico de Variáveis de Ambiente - Databricks
Para identificar como obter a URL do workspace no ambiente Databricks
"""

def check_databricks_environment():
    """Verifica todas as variáveis relacionadas ao Databricks"""
    
    print("🔍 DIAGNÓSTICO AMBIENTE DATABRICKS")
    print("=" * 50)
    
    import os
    
    # Lista de variáveis que podem conter a URL do workspace
    potential_vars = [
        'DATABRICKS_HOST',
        'DATABRICKS_WORKSPACE_URL', 
        'WORKSPACE_URL',
        'DATABRICKS_URL',
        'DATABRICKS_INSTANCE',
        'DATABRICKS_SERVER_HOSTNAME',
        'SPARK_DATABRICKS_HOST',
        'DB_HOST',
        'DB_WORKSPACE_URL'
    ]
    
    print("\n1. VARIÁVEIS DE URL DO WORKSPACE:")
    found_vars = []
    for var in potential_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var}: {value}")
            found_vars.append((var, value))
        else:
            print(f"   ❌ {var}: não definido")
    
    # Variáveis de autenticação
    auth_vars = [
        'DATABRICKS_TOKEN',
        'DATABRICKS_ACCESS_TOKEN',
        'AZURE_CLIENT_ID',
        'AZURE_CLIENT_SECRET', 
        'AZURE_TENANT_ID',
        'DATABRICKS_AAD_TOKEN'
    ]
    
    print("\n2. VARIÁVEIS DE AUTENTICAÇÃO:")
    for var in auth_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var}: {value[:10]}... (truncado)")
        else:
            print(f"   ❌ {var}: não definido")
    
    # Todas as variáveis de ambiente que contêm 'databricks'
    print("\n3. TODAS AS VARIÁVEIS COM 'DATABRICKS':")
    databricks_vars = {k: v for k, v in os.environ.items() if 'databricks' in k.lower()}
    if databricks_vars:
        for key, value in databricks_vars.items():
            if len(value) > 50:
                print(f"   {key}: {value[:50]}...")
            else:
                print(f"   {key}: {value}")
    else:
        print("   ❌ Nenhuma variável com 'databricks' encontrada")
    
    # Teste de auto-detecção
    print("\n4. TESTE DE AUTO-DETECÇÃO:")
    try:
        from databricks.sdk import WorkspaceClient
        
        # Tentar criar client sem parâmetros (auto-detecção)
        try:
            client = WorkspaceClient()
            print("   ✅ WorkspaceClient() - auto-detecção funcionou!")
            
            # Tentar obter informações do workspace
            try:
                current_user = client.current_user.me()
                print(f"   ✅ User conectado: {current_user.user_name}")
            except Exception as e:
                print(f"   ⚠️  Erro ao obter user: {e}")
                
        except Exception as e:
            print(f"   ❌ Auto-detecção falhou: {e}")
            
    except ImportError:
        print("   ❌ databricks-sdk não disponível")
    
    # Informações do contexto Spark (se disponível)
    print("\n5. CONTEXTO SPARK:")
    try:
        from pyspark.sql import SparkSession
        spark = SparkSession.getActiveSession()
        if spark:
            print("   ✅ Spark session ativa encontrada")
            spark_conf = spark.sparkContext.getConf()
            
            # Procurar configurações relacionadas ao Databricks
            databricks_configs = []
            for item in spark_conf.getAll():
                if 'databricks' in item[0].lower():
                    databricks_configs.append(item)
            
            if databricks_configs:
                print("   📋 Configurações Databricks no Spark:")
                for key, value in databricks_configs[:5]:  # Limitar a 5 itens
                    print(f"     {key}: {value[:50]}...")
            else:
                print("   ⚠️  Nenhuma config Databricks no Spark")
        else:
            print("   ❌ Nenhuma Spark session ativa")
            
    except Exception as e:
        print(f"   ❌ Erro verificando Spark: {e}")
    
    print("\n" + "=" * 50)
    if found_vars:
        print("✅ RESULTADO: Variáveis de workspace encontradas!")
        print("Use uma dessas variáveis no código:")
        for var, value in found_vars:
            print(f"   {var} = {value}")
    else:
        print("⚠️  RESULTADO: Nenhuma variável de workspace encontrada")
        print("Teste auto-detecção do WorkspaceClient() no ambiente Databricks")
    print("=" * 50)

if __name__ == "__main__":
    check_databricks_environment()
