"""
🎯 TESTE v2.1.0 - Criação Automática de Cluster
===============================================
Nova funcionalidade: auto_create_cluster=True baseado no seu código de referência
"""

import sys
sys.path.insert(0, r'c:\Users\User\OneDrive\Documentos\Projetos\Data_Master_2025\GIT\dino_2\dino_sdk\dist\dino_sdk-2.0.0-py3-none-any.whl')

from dino_sdk import WorkflowManager, WorkflowConfig

print("🎯 TESTE: Criação Automática de Cluster")
print("=" * 60)

# ✅ TESTE 1: Usando cluster existente (funcionou anteriormente)
print("🧪 TESTE 1: Com cluster existente")
config1 = WorkflowConfig(
    job_name="dino-v210-cluster-existente",
    notebook_path="/Workspace/Users/user@company.com/test_cluster_existente", 
    source_schema_name="bronze_test_volumes",
    table_name="test_cluster_existente",
    existing_cluster_id="0904-143938-4t78b4kc",  # ✅ Cluster existente
    is_automated=True
)

try:
    workflow_manager = WorkflowManager()
    job_id1 = workflow_manager.create_dino_workflow(config1)
    print(f"✅ TESTE 1 SUCESSO! Job com cluster existente: {job_id1}")
except Exception as e:
    print(f"❌ TESTE 1 FALHOU: {str(e)}")

print("\n" + "-" * 60)

# ✅ TESTE 2: Criação automática de cluster (NOVA FUNCIONALIDADE)
print("🆕 TESTE 2: Com criação automática de cluster")
config2 = WorkflowConfig(
    job_name="dino-v210-cluster-automatico",
    notebook_path="/Workspace/Users/user@company.com/test_cluster_automatico",
    source_schema_name="bronze_test_volumes", 
    table_name="test_cluster_automatico",
    # ✅ SEM cluster existente - vai criar automaticamente
    auto_create_cluster=True,  # ✅ NOVA FUNCIONALIDADE!
    cluster_name_prefix="dino-sdk",
    node_type_id="Standard_F4",  # ✅ Seu node type que funciona
    spark_version="17.1.x-scala2.13",  # ✅ Sua versão que funciona
    autotermination_minutes=10,  # ✅ Auto-terminate como seu exemplo
    single_node=True,  # ✅ Single node como seu exemplo
    is_automated=True
)

try:
    job_id2 = workflow_manager.create_dino_workflow(config2)
    print(f"✅ TESTE 2 SUCESSO! Job com cluster criado automaticamente: {job_id2}")
    print("🎉 NOVA FUNCIONALIDADE FUNCIONANDO!")
except Exception as e:
    print(f"❌ TESTE 2 FALHOU: {str(e)}")
    print("🔍 Verifique os logs para detalhes da criação do cluster")

print("\n" + "=" * 60)
print("🏁 Testes de cluster concluídos")
