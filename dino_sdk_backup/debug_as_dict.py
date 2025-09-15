# DEBUG - Testar EXATAMENTE sua sintaxe com as_dict()
from databricks.sdk.service.jobs import JobSettings as Job
from databricks.sdk import WorkspaceClient

# SEU CÓDIGO EXATO - mas com as_dict() descoberto
test_settings = Job.from_dict(
    {
        "name": "dino-debug-as-dict-teste",
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
                    "notebook_path": "/Workspace/Users/user@company.com/debug_as_dict",
                    "source": "WORKSPACE",
                },
                "existing_cluster_id": "0904-143938-4t78b4kc",
            },
        ],
    }
)

print(f"✅ JobSettings criado: {type(test_settings)}")

# TESTE: as_dict() simples
try:
    dict_result = test_settings.as_dict()
    print(f"✅ as_dict() OK: {type(dict_result)}")
    
    # TESTE: Usar o resultado com **
    w = WorkspaceClient()
    print(f"🧪 Testando: w.jobs.create(**dict_result)")
    
    job = w.jobs.create(**dict_result)
    print(f"🎉 SUCESSO TOTAL! Job ID: {job.job_id}")
    print(f"✅ MÉTODO CORRETO ENCONTRADO: **test_settings.as_dict()")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
    
    # ALTERNATIVA: Verificar se precisa argumentos nomeados específicos
    print(f"\n🔄 Tentando alternativa...")
    try:
        job2 = w.jobs.create(
            name="dino-debug-alternativa",
            trigger={
                "pause_status": "UNPAUSED",
                "file_arrival": {"url": "/Volumes/data_master_dev_dbw/bronze_test_volumes/raw/"}
            },
            tasks=[{
                "task_key": "dino_ingestion_task",
                "notebook_task": {
                    "notebook_path": "/Workspace/Users/user@company.com/debug_alternativa",
                    "source": "WORKSPACE",
                },
                "existing_cluster_id": "0904-143938-4t78b4kc",
            }]
        )
        print(f"✅ ALTERNATIVA funcionou! Job ID: {job2.job_id}")
    except Exception as e2:
        print(f"❌ Alternativa falhou: {e2}")
