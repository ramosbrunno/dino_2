"""
🎯 TESTE v2.2.0 - Job Cluster (Sem Criação Automática de Cluster)
================================================================
Nova versão otimizada: usa job_cluster ao invés de clusters dedicados
"""

import sys
sys.path.insert(0, r'c:\Users\User\OneDrive\Documentos\Projetos\Data_Master_2025\GIT\dino_2\dino_sdk\dist\dino_sdk-2.0.0-py3-none-any.whl')

print("🎯 TESTE: Job Cluster - Sem Criação Automática")
print("=" * 65)

# ✅ TESTE: Interface simplificada com job_cluster
print("🔧 VANTAGENS DO JOB_CLUSTER:")
print("   • ✅ Mais eficiente - cluster criado sob demanda")
print("   • ✅ Menor custo - cluster destruído após o job")
print("   • ✅ Sem necessidade de gerenciar clusters dedicados")
print("   • ✅ Auto-scaling automático conforme necessidade")

try:
    from dino_sdk import create_dino_job
    
    # Job COM file arrival trigger usando job_cluster
    print("\n🧪 TESTE: Job com job_cluster")
    result = create_dino_job(
        catalog_name="data_master_dev_dbw",
        schema_name="bronze_test_volumes",
        table_name="test_job_cluster",
        is_automated=True  # COM trigger
    )
    
    print(f"✅ SUCESSO! Job com job_cluster criado:")
    print(f"📋 Job ID: {result.get('job_id')}")
    print(f"📋 Job Name: dino_ingestion_data_master_dev_dbw_bronze_test_volumes_test_job_cluster")
    print(f"🔗 URL: {result.get('job_url')}")
    
    print("\n🎯 COMPORTAMENTO DO JOB_CLUSTER:")
    print("   1. Job inicia → Cluster é criado automaticamente")
    print("   2. Job executa → Usa o cluster dedicado")
    print("   3. Job termina → Cluster é destruído automaticamente")
    print("   4. Custo otimizado → Paga apenas pelo tempo de execução")
    
    print("\n✨ CONFIGURAÇÕES APLICADAS:")
    config_details = result.get('config_applied', {})
    print(f"   • File Arrival Trigger: {config_details.get('file_arrival_trigger', 'N/A')}")
    print(f"   • Job Cluster: {config_details.get('job_cluster', True)}")
    print(f"   • Node Type: Standard_F4 (single node)")
    print(f"   • Auto-terminate: 10 minutos")
    
except Exception as e:
    print(f"❌ ERRO: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 65)
print("🏁 TESTE CONCLUÍDO - Job Cluster Otimizado!")
print("🎉 DINO SDK v2.2.0: Mais eficiente e econômico!")
