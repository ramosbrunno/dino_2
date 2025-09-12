"""
🎯 TESTE v2.0.2 - PauseStatus.UNPAUSED Enum Correto
==================================================
Erro identificado: pause_status="UNPAUSED" (string) → PauseStatus.UNPAUSED (enum)
"""

import sys
sys.path.insert(0, r'c:\Users\User\OneDrive\Documentos\Projetos\Data_Master_2025\GIT\dino_2\dino_sdk\dist\dino_sdk-2.0.0-py3-none-any.whl')

from dino_sdk import WorkflowManager, WorkflowConfig

print("🎯 TESTE: PauseStatus.UNPAUSED Enum Correto")
print("=" * 60)

# ✅ TESTE: Job COM file arrival trigger - correção do enum
config = WorkflowConfig(
    job_name="dino-v202-pausestatus-enum-correto",
    notebook_path="/Workspace/Users/user@company.com/test_pausestatus_enum",
    source_schema_name="bronze_test_volumes",
    table_name="test_pausestatus_enum",
    existing_cluster_id="0904-143938-4t78b4kc",
    file_arrival_url="/Volumes/data_master_dev_dbw/bronze_test_volumes/raw/test_pausestatus_enum/"
)

try:
    workflow_manager = WorkflowManager()
    
    print("🔧 Testando com PauseStatus.UNPAUSED (enum correto)...")
    job_id = workflow_manager.create_dino_workflow(config)
    print(f"✅ SUCESSO! Enum corrigido funcionou! Job ID: {job_id}")

except Exception as e:
    print(f"❌ ERRO: {str(e)}")
    print("🔍 Verifique se ainda há outros enums incorretos")

print("\n" + "=" * 60)
print("🏁 Teste PauseStatus enum concluído")
