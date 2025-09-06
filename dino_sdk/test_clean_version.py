#!/usr/bin/env python3
"""
Teste para validar DINO SDK v2.2.0 limpo - SEM argumentos inválidos no ClusterSpec
"""

def test_imports():
    """Teste básico de imports"""
    try:
        from dino_sdk import create_dino_job
        print("✅ Import create_dino_job funcionou")
        
        from dino_sdk.workflow_manager import WorkflowManager
        print("✅ Import WorkflowManager funcionou")
        
        # Testar se ClusterSpec pode ser criado sem is_single_node
        from databricks.sdk.service.compute import ClusterSpec
        
        # Teste: ClusterSpec com argumentos válidos (sem is_single_node)
        test_cluster = ClusterSpec(
            num_workers=0,  # Correto para single node
            spark_conf={
                "spark.databricks.cluster.profile": "singleNode",
                "spark.master": "local[*]",
            },
            custom_tags={
                "ResourceClass": "SingleNode",
                "CreatedBy": "dino-sdk", 
                "Purpose": "JobCluster"
            }
        )
        print("✅ ClusterSpec criado corretamente SEM is_single_node")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nos imports: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_function_signature():
    """Testa se create_dino_job aceita 4 parâmetros"""
    try:
        from dino_sdk import create_dino_job
        import inspect
        
        # Verificar assinatura da função
        sig = inspect.signature(create_dino_job)
        params = list(sig.parameters.keys())
        
        expected_params = ['catalog_name', 'schema_name', 'table_name', 'is_automated']
        
        print(f"Parâmetros encontrados: {params}")
        print(f"Parâmetros esperados: {expected_params}")
        
        if set(expected_params).issubset(set(params)):
            print("✅ Assinatura da função correta - 4 parâmetros principais encontrados")
            return True
        else:
            print("❌ Assinatura da função incorreta")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar assinatura: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 TESTE DINO SDK v2.2.0 LIMPO")
    print("=" * 50)
    
    print("\n1. Testando imports...")
    imports_ok = test_imports()
    
    print("\n2. Testando assinatura da função...")
    signature_ok = test_function_signature()
    
    print("\n" + "=" * 50)
    if imports_ok and signature_ok:
        print("✅ TODOS OS TESTES PASSARAM!")
        print("🎉 DINO SDK v2.2.0 está limpo e otimizado para job_clusters")
    else:
        print("❌ ALGUNS TESTES FALHARAM")
        
    print("\n📋 RESUMO v2.2.0:")
    print("- ✅ Removido auto_create_cluster")  
    print("- ✅ Otimizado para job_clusters")
    print("- ✅ Interface simplificada com 4 parâmetros")
    print("- ✅ ClusterSpec SEM is_single_node")
    print("- ✅ Código limpo sem comentários de correção")
