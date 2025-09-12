"""
🎯 TESTE v2.1.1 - Correção dos Campos min_workers/max_workers
============================================================
Correção: Removidos campos obsoletos e ajustado para nova estrutura de configuração
"""

import sys
sys.path.insert(0, r'c:\Users\User\OneDrive\Documentos\Projetos\Data_Master_2025\GIT\dino_2\dino_sdk\dist\dino_sdk-2.0.0-py3-none-any.whl')

from dino_sdk import WorkflowManager, WorkflowConfig

print("🎯 TESTE: Correção campos min_workers/max_workers")
print("=" * 60)

# ✅ TESTE: Job COM file arrival trigger - campos corrigidos
config = WorkflowConfig(
    job_name="dino-v211-campos-corrigidos",
    notebook_path="/Workspace/Users/user@company.com/test_campos_corrigidos",
    source_schema_name="bronze_test_volumes",
    table_name="test_campos_corrigidos",
    existing_cluster_id="0904-143938-4t78b4kc",
    is_automated=True
)

try:
    workflow_manager = WorkflowManager()
    
    print("🔧 Testando com campos corrigidos...")
    job_id = workflow_manager.create_dino_workflow(config)
    print(f"✅ SUCESSO! Campos corrigidos funcionaram! Job ID: {job_id}")

except Exception as e:
    print(f"❌ ERRO: {str(e)}")
    print("🔍 Ainda há problemas com os campos de configuração")

print("\n" + "=" * 60)
print("🏁 Teste campos corrigidos concluído")
