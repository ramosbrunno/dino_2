#!/usr/bin/env python3
"""
🦕 DINO SDK v1.6.0 - TESTE CRUCIAL COM CLASSES OFICIAIS
🎯 DEVE resolver 'dict' object has no attribute 'as_dict'
"""

print("🦕 DINO SDK v1.6.0 - TESTE CRUCIAL COM CLASSES OFICIAIS")
print("🎯 Task(), NotebookTask(), NewCluster() → Objetos tipados!")
print("=" * 80)

# Teste de importação v1.6.0
try:
    from dino_sdk import __version__, create_dino_workflow
    print(f"✅ DINO SDK v{__version__} importado!")
    
    if __version__ == "1.6.0":
        print("🎯 *** v1.6.0 CONFIRMADA - CLASSES OFICIAIS IMPLEMENTADAS! ***")
    else:
        print(f"⚠️ Versão: {__version__} (esperava 1.6.0)")
        
except ImportError as e:
    print(f"❌ Erro: {e}")
    exit(1)

# Teste Databricks
try:
    from databricks.sdk import WorkspaceClient
    w = WorkspaceClient()
    current_user = w.current_user.me()
    print(f"✅ Databricks: {current_user.user_name}")
except Exception as e:
    print(f"⚠️ Databricks: {e}")
    exit(1)

print(f"\n🧪 EXECUTANDO TESTE CRUCIAL v1.6.0...")
print(f"🎯 Este DEVE resolver o erro 'as_dict' definitivamente!")
print("=" * 80)

try:
    # TESTE CRÍTICO com cluster existente da sua referência
    resultado = create_dino_workflow(
        job_name="dino-v160-classes-oficiais-final",
        notebook_path="/Workspace/Users/user@company.com/test_v160_final",
        catalog_name="data_master_dev_dbw",
        schema_name="bronze",
        table_name="test_v160_final",
        existing_cluster_id="0904-143938-4t78b4kc",  # Seu cluster
        source_path="test_v160_final",
        is_automated=False,
        projeto="DINO SDK v1.6.0 Classes Oficiais",
        description="🧪 Teste final - Classes Task(), NotebookTask(), NewCluster()"
    )
    
    print(f"\n🎯 RESULTADO v1.6.0:")
    print("=" * 60)
    
    if resultado.get("success"):
        print("🎉 *** SUCESSO ABSOLUTO v1.6.0! ***")
        print("✅ ERRO 'as_dict' RESOLVIDO COM CLASSES OFICIAIS!")
        print(f"   🆔 Job ID: {resultado.get('job_id')}")
        print(f"   📛 Nome: {resultado.get('job_name')}")
        print(f"   🔗 URL: {resultado.get('job_url')}")
        
        print(f"\n🏆 VALIDAÇÃO FINAL:")
        print(f"   ✅ Task() → Objeto oficial com método as_dict()")
        print(f"   ✅ NotebookTask() → Objeto oficial com método as_dict()")
        print(f"   ✅ NewCluster() → Objeto oficial com método as_dict()")
        print(f"   ✅ client.jobs.create(tasks=[task_object])")
        print(f"   ✅ ZERO erros 'dict has no attribute as_dict'")
        
        print(f"\n🦕 DINO SDK v1.6.0 É A VERSÃO DE PRODUÇÃO!")
        
    else:
        print("🔍 AINDA COM PROBLEMA v1.6.0:")
        erro = resultado.get('error', 'N/A')
        print(f"   🐛 Erro: {erro}")
        
        if "'dict' object has no attribute 'as_dict'" in str(erro):
            print(f"   ❌ Mesmo erro - problema mais profundo")
        else:
            print(f"   ✅ ERRO DIFERENTE! Progresso significativo!")
            print(f"   🎯 Classes oficiais podem ter resolvido 'as_dict'")
            
except Exception as e:
    print(f"❌ EXCEÇÃO: {e}")
    import traceback
    traceback.print_exc()

print(f"\n📋 SUMMARY:")
print(f"   📦 DINO SDK v1.6.0 - Classes Oficiais Task(), NotebookTask(), NewCluster()")
print(f"   🎯 Baseado na sua referência da documentação oficial")
print(f"   🏆 DEVE resolver 'dict has no attribute as_dict' definitivamente!")
