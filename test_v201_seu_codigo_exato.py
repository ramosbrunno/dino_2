"""
🎯 TESTE FINAL v2.0.1 - SEU CÓDIGO EXATO
=======================================
Usando LITERALMENTE sua sintaxe, apenas substituindo valores por variáveis
"""

import sys
sys.path.insert(0, r'c:\Users\User\OneDrive\Documentos\Projetos\Data_Master_2025\GIT\dino_2\dino_sdk\dist\dino_sdk-2.0.0-py3-none-any.whl')

from dino_sdk import WorkflowManager, WorkflowConfig

print("🎯 TESTE FINAL: SEU CÓDIGO EXATO com variáveis")
print("=" * 60)

# ✅ TESTE: Job COM file arrival trigger usando SEU CÓDIGO EXATO
config = WorkflowConfig(
    job_name="dino-v201-seu-codigo-exato",
    notebook_path="/Workspace/Users/user@company.com/test_seu_codigo_exato",
    source_schema_name="bronze_test_volumes",
    table_name="test_seu_codigo_exato",
    existing_cluster_id="0904-143938-4t78b4kc",
    file_arrival_url="/Volumes/data_master_dev_dbw/bronze_test_volumes/raw/test_seu_codigo_exato/"  # ✅ COM file arrival!
)

try:
    workflow_manager = WorkflowManager()
    
    # ✅ TESTE 2: Job COM file arrival trigger - SEU CÓDIGO EXATO
    print("✅ SEU CÓDIGO EXATO - ZERO modificações na sintaxe")
    print("=" * 70)
    job_id = workflow_manager.create_dino_workflow(config)
    print(f"✅ SUCESSO! Job ID: {job_id}")
    print("✅ SEU CÓDIGO EXATO FUNCIONOU!")

except Exception as e:
    print(f"❌ FALHOU: {str(e)}")
    print("🔧 Verifique se as importações estão corretas")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("🏁 FIM DOS TESTES")
