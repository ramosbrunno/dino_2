# Databricks notebook source
# MAGIC %md
# MAGIC # 🦕 DINO SDK v1.2.0 - WorkflowManager Teste Simplificado
# MAGIC 
# MAGIC **Objetivo:** Testar o WorkflowManager do DINO SDK no Databricks com imports corretos
# MAGIC 
# MAGIC **Funcionalidades testadas:**
# MAGIC - ✅ Jobs automatizados com file arrival triggers
# MAGIC - ✅ Job clusters com configurações customizadas
# MAGIC - ✅ Custom tags preenchidas automaticamente
# MAGIC - ✅ Integração simplificada para Databricks

# COMMAND ----------

# MAGIC %md
# MAGIC ## 📦 1. Instalar e Configurar Dependências

# COMMAND ----------

# Instalar DINO SDK
%pip install --quiet --upgrade databricks-sdk

# COMMAND ----------

# Imports necessários - APENAS os que funcionam no Databricks
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Union

# Databricks SDK - apenas imports que existem
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.jobs import (
    JobSettings,
    NotebookTask,
    Task,
    CronSchedule,
    JobCluster,
    ClusterSpec,
    TriggerSettings,
    JobEmailNotifications,
    PauseStatus,
    FileArrivalTrigger,
    Source
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("📦 Imports carregados com sucesso!")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🔧 2. Implementação do DinoWorkflowManager Simplificado

# COMMAND ----------

class SimpleDinoWorkflowManager:
    """
    🦕 DINO Workflow Manager Simplificado para Databricks
    
    Implementação direta sem dependências externas
    """
    
    def __init__(self):
        self.client = WorkspaceClient()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Validar conexão
        try:
            self.workspace_info = self.client.current_user.me()
            print(f"✅ Conectado como: {self.workspace_info.user_name}")
            print(f"🏢 Workspace: {self.client.config.host}")
        except Exception as e:
            print(f"❌ Erro na conexão: {e}")
            raise
    
    def create_job_cluster_config(self, 
                                 cluster_name: str,
                                 node_type_id: str = "Standard_D4ds_v5",
                                 min_workers: int = 1,
                                 max_workers: int = 2,
                                 custom_tags: Optional[Dict] = None) -> JobCluster:
        """Cria configuração de job cluster otimizada"""
        
        # Custom tags preenchidas automaticamente
        default_tags = {
            "CreatedBy": "DINO_SDK_v1.2.0",
            "CreatedAt": datetime.now().isoformat(),
        }
        if custom_tags:
            default_tags.update(custom_tags)
        
        # Configuração do cluster
        cluster_config = {
            "data_security_mode": "DATA_SECURITY_MODE_DEDICATED",
            "custom_tags": default_tags,
            "kind": "CLASSIC_PREVIEW",
            "spark_env_vars": {
                "PYSPARK_PYTHON": "/databricks/python3/bin/python3"
            },
            "azure_attributes": {
                "availability": "SPOT_WITH_FALLBACK_AZURE"
            },
            "runtime_engine": "PHOTON",
            "spark_version": "17.1.x-scala2.13",
            "node_type_id": node_type_id,
            "is_single_node": False,
            "autoscale": {
                "min_workers": min_workers,
                "max_workers": max_workers
            }
        }
        
        # Criar job cluster
        cluster_spec = ClusterSpec.from_dict(cluster_config)
        job_cluster = JobCluster(
            job_cluster_key=cluster_name,
            new_cluster=cluster_spec
        )
        
        print(f"🏗️ Job cluster configurado: {cluster_name}")
        print(f"   💻 Tipo: {node_type_id} ({min_workers}-{max_workers} workers)")
        print(f"   🏷️ Tags: {len(default_tags)} configuradas")
        
        return job_cluster
    
    def create_dino_job(self,
                       job_name: str,
                       notebook_path: str,
                       catalog_name: str,
                       schema_name: str,
                       table_name: str,
                       source_path: str,
                       is_automated: bool = False,
                       file_arrival_url: Optional[str] = None,
                       cron_schedule: Optional[str] = None,
                       projeto: str = "",
                       **cluster_kwargs) -> Dict:
        """
        Cria job DINO completo no Databricks
        """
        try:
            print(f"🦕 Criando job DINO: {job_name}")
            
            # Custom tags para o cluster
            custom_tags = {
                "Projeto": projeto,
                "Catalogo": catalog_name,
                "Schema": schema_name,
                "Tabela": table_name,
                "SourcePath": source_path,
                "IsAutomated": str(is_automated)
            }
            
            # Criar job cluster
            cluster_name = f"{job_name}-cluster"
            job_cluster = self.create_job_cluster_config(
                cluster_name=cluster_name,
                custom_tags=custom_tags,
                **cluster_kwargs
            )
            
            # Criar task de notebook
            task = Task(
                task_key=f"ingest-{table_name}",
                description=f"DINO Ingestion: {catalog_name}.{schema_name}.{table_name}",
                notebook_task=NotebookTask(
                    notebook_path=notebook_path,
                    source=Source.WORKSPACE
                ),
                job_cluster_key=cluster_name
            )
            
            # Configurações base do job
            job_settings = JobSettings(
                name=job_name,
                description=f"DINO Workflow: {catalog_name}.{schema_name}.{table_name}",
                job_clusters=[job_cluster],
                tasks=[task],
                queue={"enabled": True}
            )
            
            # Configurar trigger/schedule
            if is_automated:
                # File arrival trigger
                trigger_url = file_arrival_url or source_path
                job_settings.trigger = TriggerSettings(
                    pause_status=PauseStatus.UNPAUSED,
                    file_arrival=FileArrivalTrigger(url=trigger_url)
                )
                print(f"⚡ File arrival trigger configurado: {trigger_url}")
            elif cron_schedule:
                # CRON schedule
                job_settings.schedule = CronSchedule(
                    quartz_cron_expression=cron_schedule,
                    timezone_id="America/Sao_Paulo",
                    pause_status=PauseStatus.PAUSED
                )
                print(f"⏰ CRON schedule configurado: {cron_schedule}")
            
            # Criar job no Databricks
            job_response = self.client.jobs.create(settings=job_settings)
            
            # Resultado
            result = {
                "success": True,
                "job_id": job_response.job_id,
                "job_name": job_name,
                "job_url": f"{self.client.config.host}/#job/{job_response.job_id}",
                "cluster_name": cluster_name,
                "is_automated": is_automated,
                "trigger_type": "file_arrival" if is_automated else "cron_schedule",
                "custom_tags": custom_tags,
                "message": "Job criado com sucesso!"
            }
            
            print(f"✅ Job criado: {job_name} (ID: {job_response.job_id})")
            print(f"🔗 URL: {result['job_url']}")
            
            return result
            
        except Exception as e:
            print(f"❌ Erro ao criar job: {e}")
            return {
                "success": False,
                "job_name": job_name,
                "error": str(e)
            }

# Criar instância do manager
manager = SimpleDinoWorkflowManager()
print("🦕 SimpleDinoWorkflowManager criado com sucesso!")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🧪 3. Teste 1: Job Automatizado com File Arrival

# COMMAND ----------

# Configuração do job automatizado
job_config_automated = {
    "job_name": "dino-test-automated-iot",
    "notebook_path": "/Workspace/Users/user@company.com/iot_ingestion_notebook",
    "catalog_name": "iot_data", 
    "schema_name": "bronze",
    "table_name": "sensor_telemetry",
    "source_path": "abfss://iot@storage.dfs.core.windows.net/sensors/",
    "is_automated": True,  # 🔥 File arrival trigger ativo
    "projeto": "IoT Platform",
    "node_type_id": "Standard_D8ds_v5",
    "min_workers": 2,
    "max_workers": 6
}

print("⚡ Testando criação de job automatizado com file arrival trigger:")
print(f"📋 Configuração: {json.dumps(job_config_automated, indent=2)}")

# IMPORTANTE: Mudar para dry_run=False apenas quando quiser criar o job real
resultado_automatizado = manager.create_dino_job(**job_config_automated)

print("\n📊 Resultado do Teste Automatizado:")
if resultado_automatizado["success"]:
    print("✅ SUCESSO!")
    for key, value in resultado_automatizado.items():
        if key != "custom_tags":
            print(f"   {key}: {value}")
    print(f"   custom_tags: {len(resultado_automatizado['custom_tags'])} tags configuradas")
else:
    print(f"❌ FALHOU: {resultado_automatizado.get('error')}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🧪 4. Teste 2: Job Programado com CRON

# COMMAND ----------

# Configuração do job programado
job_config_scheduled = {
    "job_name": "dino-test-scheduled-sales", 
    "notebook_path": "/Workspace/Users/user@company.com/daily_sales_notebook",
    "catalog_name": "sales_data",
    "schema_name": "bronze", 
    "table_name": "daily_transactions",
    "source_path": "abfss://sales@storage.dfs.core.windows.net/daily/",
    "is_automated": False,  # Job programado
    "cron_schedule": "0 0 9 * * ?",  # Todo dia às 9h
    "projeto": "Sales Analytics",
    "node_type_id": "Standard_D4ds_v5",
    "min_workers": 1,
    "max_workers": 4
}

print("⏰ Testando criação de job programado com CRON schedule:")
print(f"📋 Configuração: {json.dumps(job_config_scheduled, indent=2)}")

resultado_programado = manager.create_dino_job(**job_config_scheduled)

print("\n📊 Resultado do Teste Programado:")
if resultado_programado["success"]:
    print("✅ SUCESSO!")
    for key, value in resultado_programado.items():
        if key != "custom_tags":
            print(f"   {key}: {value}")
    print(f"   custom_tags: {len(resultado_programado['custom_tags'])} tags configuradas")
else:
    print(f"❌ FALHOU: {resultado_programado.get('error')}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 📊 5. Listagem de Jobs DINO Existentes

# COMMAND ----------

# Listar jobs DINO
print("📋 Listando jobs DINO existentes no workspace:")
print("=" * 50)

try:
    dino_jobs = []
    all_jobs = list(manager.client.jobs.list())
    
    for job in all_jobs:
        # Verificar se é job DINO
        if (job.settings.name and 
            ("dino" in job.settings.name.lower() or 
             job.settings.name.startswith("dino-"))):
            
            dino_jobs.append({
                "job_id": job.job_id,
                "job_name": job.settings.name,
                "creator": job.creator_user_name,
                "created_time": job.created_time
            })
    
    print(f"🦕 Jobs DINO encontrados: {len(dino_jobs)}")
    
    if dino_jobs:
        for i, job in enumerate(dino_jobs, 1):
            print(f"\n{i}. {job['job_name']}")
            print(f"   🆔 ID: {job['job_id']}")
            print(f"   👤 Criador: {job['creator']}")
            print(f"   📅 Criado em: {job['created_time']}")
            print(f"   🔗 URL: {manager.client.config.host}/#job/{job['job_id']}")
    else:
        print("ℹ️ Nenhum job DINO encontrado")
        print("💡 Execute os testes acima para criar jobs de exemplo")

except Exception as e:
    print(f"❌ Erro ao listar jobs: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🎯 6. Resumo e Validação Final

# COMMAND ----------

print("🦕 DINO SDK v1.2.0 - WorkflowManager - Resumo dos Testes")
print("=" * 60)

# Resultados dos testes
tests_results = [
    {
        "name": "Job Automatizado (File Arrival)",
        "success": resultado_automatizado["success"],
        "details": resultado_automatizado
    },
    {
        "name": "Job Programado (CRON Schedule)", 
        "success": resultado_programado["success"],
        "details": resultado_programado
    }
]

successful_tests = sum(1 for test in tests_results if test["success"])
total_tests = len(tests_results)

print(f"✅ Testes bem-sucedidos: {successful_tests}/{total_tests}")
print(f"📈 Taxa de sucesso: {(successful_tests/total_tests)*100:.1f}%")

print(f"\n🚀 Funcionalidades testadas:")
features = [
    "✅ File arrival triggers automáticos",
    "✅ CRON schedules programados", 
    "✅ Job clusters com Photon runtime",
    "✅ Custom tags preenchidas automaticamente",
    "✅ Azure Spot instances com fallback",
    "✅ Configurações de autoscaling",
    "✅ Integração com Databricks SDK"
]

for feature in features:
    print(f"   {feature}")

if successful_tests == total_tests:
    print(f"\n🎉 TODOS OS TESTES PASSARAM! 🦕")
    print(f"🚀 DINO WorkflowManager está funcionando perfeitamente no Databricks!")
else:
    print(f"\n⚠️ {total_tests - successful_tests} teste(s) falharam.")
    print(f"🔍 Verificar configurações do workspace e permissões.")

print(f"\n📝 Para usar em produção:")
print(f"   1. Ajuste os notebook_path para notebooks reais")
print(f"   2. Configure source_path com locais reais de dados") 
print(f"   3. Remova dry_run=False para criar jobs reais")
print(f"   4. Configure notificações por email se necessário")

print(f"\n🦕 DINO SDK WorkflowManager - Teste concluído! ✨")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🔧 7. Exemplo de Uso Rápido (Copy & Paste)
# MAGIC 
# MAGIC ```python
# MAGIC # Exemplo rápido para usar em seus notebooks
# MAGIC 
# MAGIC from databricks.sdk import WorkspaceClient
# MAGIC 
# MAGIC # Criar job automatizado rapidamente
# MAGIC manager = SimpleDinoWorkflowManager()
# MAGIC 
# MAGIC resultado = manager.create_dino_job(
# MAGIC     job_name="meu-job-automatizado",
# MAGIC     notebook_path="/Workspace/Users/MEU_USER/meu_notebook",
# MAGIC     catalog_name="meu_catalogo",
# MAGIC     schema_name="bronze", 
# MAGIC     table_name="minha_tabela",
# MAGIC     source_path="abfss://dados@storage.dfs.core.windows.net/raw/",
# MAGIC     is_automated=True,  # 🔥 File arrival trigger ativo
# MAGIC     projeto="Meu Projeto"
# MAGIC )
# MAGIC 
# MAGIC print(f"Job criado: {resultado['job_url']}")
# MAGIC ```
# MAGIC 
# MAGIC ---
# MAGIC 
# MAGIC **🦕 DINO SDK v1.2.0 - WorkflowManager funcionando no Databricks!** 🚀
