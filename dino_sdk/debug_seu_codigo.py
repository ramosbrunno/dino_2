#!/usr/bin/env python3
"""
🔍 DEBUG - Reproduzir EXATAMENTE seu código que funciona
🎯 Para entender por que as_shallow_dict() não funciona no SDK
"""

print("🔍 DEBUG - REPRODUZINDO SEU CÓDIGO EXATO")
print("=" * 60)

# Testar exatamente como você fez
try:
    from databricks.sdk.service.jobs import JobSettings as Job
    from databricks.sdk import WorkspaceClient
    
    print("✅ Imports OK")
    
    # ✅ SEU CÓDIGO EXATO - copiar/colar
    dino_debug_test = Job.from_dict(
        {
            "name": "dino-debug-test-exato",
            "trigger": {
                "pause_status": "UNPAUSED",
                "file_arrival": {
                    "url": "/Volumes/data_master_dev_dbw/bronze_test_volumes/raw/",
                },
            },
            "tasks": [
                {
                    "task_key": "dino_ingestion_task",
                    "notebook_task": {
                        "notebook_path": "/Workspace/Users/user@company.com/debug_test",
                        "source": "WORKSPACE",
                    },
                    "existing_cluster_id": "0904-143938-4t78b4kc",
                },
            ],
        }
    )
    
    print(f"✅ Job.from_dict() OK")
    print(f"🔍 Type: {type(dino_debug_test)}")
    print(f"🔍 Methods: {[m for m in dir(dino_debug_test) if 'dict' in m]}")
    
    # Verificar se tem as_shallow_dict
    if hasattr(dino_debug_test, 'as_shallow_dict'):
        print("✅ as_shallow_dict() existe!")
        
        # Testar sua sintaxe exata
        w = WorkspaceClient()
        job = w.jobs.create(**dino_debug_test.as_shallow_dict())
        print(f"🎉 SUCESSO! Job ID: {job.job_id}")
        
    else:
        print("❌ as_shallow_dict() NÃO existe")
        print("🔍 Métodos disponíveis:")
        for method in dir(dino_debug_test):
            if not method.startswith('_'):
                print(f"   - {method}")
                
        # Testar alternativas
        print("\n🔄 Testando alternativas...")
        
        w = WorkspaceClient()
        
        try:
            # Tentar sem desempacotar
            job = w.jobs.create(dino_debug_test)
            print(f"✅ FUNCIONOU sem desempacotar! Job ID: {job.job_id}")
        except Exception as e:
            print(f"❌ Sem desempacotar falhou: {e}")
            
            try:
                # Tentar as_dict se existir
                if hasattr(dino_debug_test, 'as_dict'):
                    job = w.jobs.create(**dino_debug_test.as_dict())
                    print(f"✅ FUNCIONOU com as_dict()! Job ID: {job.job_id}")
            except Exception as e2:
                print(f"❌ as_dict() falhou: {e2}")
                
except Exception as e:
    print(f"❌ Erro geral: {e}")
    import traceback
    traceback.print_exc()

print(f"\n🎯 ANÁLISE:")
print(f"   📚 Versão SDK pode ser diferente")
print(f"   🔧 as_shallow_dict() pode não existir na sua versão")
print(f"   💡 Precisamos encontrar método correto")
