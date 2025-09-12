"""
🎯 TESTE v2.0.1 - Stack Trace Completo + Source.WORKSPACE Corrigido
====================================================================
"""

import sys
sys.path.insert(0, r'c:\Users\User\OneDrive\Documentos\Projetos\Data_Master_2025\GIT\dino_2\dino_sdk\dist\dino_sdk-2.0.0-py3-none-any.whl')

from dino_sdk import WorkflowManager, WorkflowConfig

print("🔍 TESTE COM STACK TRACE COMPLETO")
print("=" * 60)

# ✅ TESTE: Job COM file arrival trigger
config = WorkflowConfig(
    job_name="dino-v201-debug-stacktrace",
    notebook_path="/Workspace/Users/user@company.com/test_debug_stacktrace",
    source_schema_name="bronze_test_volumes",
    table_name="test_debug_stacktrace",
    existing_cluster_id="0904-143938-4t78b4kc",
    file_arrival_url="/Volumes/data_master_dev_dbw/bronze_test_volumes/raw/test_debug_stacktrace/"
)

try:
    workflow_manager = WorkflowManager()
    
    print("🚀 Testando com stack trace completo...")
    job_id = workflow_manager.create_dino_workflow(config)
    print(f"✅ SUCESSO! Job ID: {job_id}")

except Exception as e:
    print(f"❌ ERRO: {str(e)}")
    print("🔍 Agora com stack trace completo no log!")

print("\n" + "=" * 60)
print("🏁 Teste concluído - verifique o stack trace detalhado no log")
