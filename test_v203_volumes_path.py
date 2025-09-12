"""
🎯 TESTE v2.0.3 - Volumes Path Correto
=====================================
Correção: file_arrival_url usando /Volumes/{catalog}/{schema}/raw/{table}/ 
Em vez de path ABFSS que causa conflito
"""

import sys
sys.path.insert(0, r'c:\Users\User\OneDrive\Documentos\Projetos\Data_Master_2025\GIT\dino_2\dino_sdk\dist\dino_sdk-2.0.0-py3-none-any.whl')

from dino_sdk import WorkflowManager, WorkflowConfig

print("🎯 TESTE: Volumes Path Correto")
print("=" * 60)

# ✅ TESTE: Job COM file arrival trigger - path Volumes correto
config = WorkflowConfig(
    job_name="dino-v203-volumes-path-correto",
    notebook_path="/Workspace/Users/user@company.com/test_volumes_path",
    source_schema_name="bronze_test_volumes", 
    table_name="test_volumes_path",
    existing_cluster_id="0904-143938-4t78b4kc",
    # ✅ Não definir file_arrival_url - deixar o SDK gerar automaticamente com Volumes
    is_automated=True  # Vai gerar: /Volumes/data_master_dev_dbw/bronze_test_volumes/raw/test_volumes_path/
)

try:
    workflow_manager = WorkflowManager()
    
    print("🔧 Testando com path Volumes gerado automaticamente...")
    print("📍 Esperado: /Volumes/data_master_dev_dbw/bronze_test_volumes/raw/test_volumes_path/")
    
    job_id = workflow_manager.create_dino_workflow(config)
    print(f"✅ SUCESSO! Path Volumes funcionou! Job ID: {job_id}")

except Exception as e:
    print(f"❌ ERRO: {str(e)}")
    print("🔍 Verifique se o path Volumes foi gerado corretamente")

print("\n" + "=" * 60)
print("🏁 Teste Volumes path concluído")
