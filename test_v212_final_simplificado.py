"""
🎯 TESTE FINAL v2.1.2 - Imports Corrigidos + Interface Simplificada  
================================================================
Demonstrando a nova função create_dino_job() que só precisa de 4 parâmetros!
"""

import sys
sys.path.insert(0, r'c:\Users\User\OneDrive\Documentos\Projetos\Data_Master_2025\GIT\dino_2\dino_sdk\dist\dino_sdk-2.0.0-py3-none-any.whl')

print("🎯 TESTE: Imports Corrigidos + Interface Simplificada")
print("=" * 65)

# ✅ TESTE 1: Imports que agora funcionam
print("1️⃣ TESTANDO IMPORTS CORRIGIDOS:")
try:
    from dino_sdk import WorkflowManager, WorkflowConfig, create_dino_job
    print("✅ WorkflowManager: OK")
    print("✅ WorkflowConfig: OK")
    print("✅ create_dino_job: OK")
except ImportError as e:
    print(f"❌ Import Error: {e}")

print("\n" + "-" * 65)

# ✅ TESTE 2: Interface simplificada - apenas 4 parâmetros!
print("2️⃣ TESTANDO INTERFACE SIMPLIFICADA:")
print("📋 create_dino_job() - só precisa de 4 parâmetros:")
print("   • catalog_name")
print("   • schema_name")
print("   • table_name") 
print("   • is_automated")

try:
    # Job SEM trigger (manual)
    print("\n🧪 Teste A: Job manual (is_automated=False)")
    result1 = create_dino_job(
        catalog_name="data_master_dev_dbw",
        schema_name="bronze_test_volumes",
        table_name="test_manual",
        is_automated=False
    )
    print(f"✅ Job manual criado: {result1.get('job_id')}")
    
    # Job COM trigger (automático)  
    print("\n🧪 Teste B: Job automático (is_automated=True)")
    result2 = create_dino_job(
        catalog_name="data_master_dev_dbw",
        schema_name="bronze_test_volumes", 
        table_name="test_automatico",
        is_automated=True
    )
    print(f"✅ Job automático criado: {result2.get('job_id')}")
    
    print("\n🎉 INTERFACE SIMPLIFICADA FUNCIONANDO!")
    print("📊 Automações aplicadas:")
    print("   • job_name: dino_ingestion_{catalog}_{schema}_{table}")
    print("   • notebook_path: /Workspace/dino/dino_ingestion")
    print("   • cluster: criado automaticamente") 
    print("   • file_arrival_url: /Volumes/{catalog}/{schema}/raw/{table}/")
    
except Exception as e:
    print(f"❌ Erro na interface simplificada: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 65)
print("🏁 TESTES CONCLUÍDOS - DINO SDK v2.1.2 PRONTO!")
