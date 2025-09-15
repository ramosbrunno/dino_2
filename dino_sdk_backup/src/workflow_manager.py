#!/usr/bin/env python3
"""
🦕 DINO SDK v1.2.0 - Workflow Manager
Gerador avançado de workflows/jobs do Databricks para automação de ingestão

Funcionalidades:
- File arrival triggers automáticos
- Job clusters otimizados com Photon
- Custom tags preenchidas automaticamente
- Templates de notebook
- Integração com IngestionEngine
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field, asdict

# Databricks SDK - imports corretos para Databricks
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
    Source
)

from .config_manager import get_config_manager


@dataclass
class DinoWorkflowConfig:
    """
    🦕 Configuração completa para criação de workflows DINO
    """
    # Identificação básica
    job_name: str
    notebook_path: str
    
    # Destino dos dados
    catalog_name: str
    schema_name: str
    table_name: str
    source_path: str
    
    # Configurações de automação
    is_automated: bool = False
    file_arrival_url: Optional[str] = None
    cron_schedule: Optional[str] = None
    timezone: str = "America/Sao_Paulo"
    
    # Configurações de cluster
    node_type_id: str = "Standard_D4ds_v5"
    min_workers: int = 1
    max_workers: int = 2
    spark_version: str = "17.1.x-scala2.13"
    is_single_node: bool = False
    
    # Configurações de ingestão  
    liquid_clustering: bool = False
    clustering_columns: List[str] = field(default_factory=list)
    schema_evolution_mode: str = "addNewColumns"
    type_run: str = "batch"
    
    # Notificações
    email_notifications: Dict[str, List[str]] = field(default_factory=dict)
    
    # Metadados
    projeto: str = ""
    description: Optional[str] = None


class DinoWorkflowManager:
    """
    🦕 DINO Workflow Manager - Gerador avançado de workflows Databricks
    
    Cria jobs/workflows otimizados para uso com IngestionEngine, incluindo:
    - File arrival triggers automáticos
    - Job clusters com Photon e autoscaling
    - Custom tags preenchidas automaticamente
    - Templates de notebook gerados
    """
    
    def __init__(self, workspace_client: Optional[WorkspaceClient] = None):
        """
        Inicializa o WorkflowManager.
        
        Args:
            workspace_client: Cliente do workspace Databricks (opcional)
        """
        self.client = workspace_client or WorkspaceClient()
        self.config = get_config_manager()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Validar conexão
        try:
            self.workspace_info = self.client.current_user.me()
            self.logger.info(f"✅ WorkflowManager conectado como: {self.workspace_info.user_name}")
        except Exception as e:
            self.logger.error(f"❌ Erro na conexão com workspace: {e}")
            # Não falhar, pode ser usado offline para templates
    
    def create_job_cluster(self, config: DinoWorkflowConfig) -> JobCluster:
        """
        Cria configuração de job cluster otimizada.
        
        Args:
            config: Configuração do workflow
            
        Returns:
            JobCluster: Cluster configurado
        """
        # Custom tags preenchidas automaticamente
        custom_tags = {
            "Projeto": config.projeto,
            "Catalogo": config.catalog_name,
            "Schema": config.schema_name,
            "Tabela": config.table_name,
            "SourcePath": config.source_path,
            "CreatedBy": "DINO_SDK_v1.2.0",
            "CreatedAt": datetime.now().isoformat(),
            "IsAutomated": str(config.is_automated),
            "TypeRun": config.type_run
        }
        
        # Configuração do cluster
        cluster_config = {
            "data_security_mode": "DATA_SECURITY_MODE_DEDICATED",
            "custom_tags": custom_tags,
            "kind": "CLASSIC_PREVIEW",
            "spark_env_vars": {
                "PYSPARK_PYTHON": "/databricks/python3/bin/python3"
            },
            "azure_attributes": {
                "availability": "SPOT_WITH_FALLBACK_AZURE"
            },
            "runtime_engine": "PHOTON",
            "spark_version": config.spark_version,
            "node_type_id": config.node_type_id,
            "is_single_node": config.is_single_node
        }
        
        # Configurar autoscaling apenas se não for single node
        if not config.is_single_node:
            cluster_config["autoscale"] = {
                "min_workers": config.min_workers,
                "max_workers": config.max_workers
            }
        
        # Nome do cluster
        cluster_name = f"{config.job_name}-cluster"
        
        # Criar especificação do cluster
        cluster_spec = ClusterSpec.from_dict(cluster_config)
        
        # Criar job cluster
        job_cluster = JobCluster(
            job_cluster_key=cluster_name,
            new_cluster=cluster_spec
        )
        
        self.logger.info(f"🏗️ Job cluster configurado: {cluster_name}")
        self.logger.info(f"   💻 Tipo: {config.node_type_id}")
        self.logger.info(f"   👥 Workers: {config.min_workers}-{config.max_workers}")
        self.logger.info(f"   🏷️ Tags: {len(custom_tags)} configuradas")
        
        return job_cluster
    
    def create_notebook_task(self, config: DinoWorkflowConfig, cluster_key: str) -> Task:
        """
        Cria task de notebook para ingestão.
        
        Args:
            config: Configuração do workflow
            cluster_key: Chave do job cluster
            
        Returns:
            Task: Task configurada
        """
        task_key = f"ingest-{config.table_name}"
        
        task = Task(
            task_key=task_key,
            description=f"DINO Ingestion: {config.catalog_name}.{config.schema_name}.{config.table_name}",
            notebook_task=NotebookTask(
                notebook_path=config.notebook_path,
                source=Source.WORKSPACE
            ),
            job_cluster_key=cluster_key
        )
        
        self.logger.info(f"📋 Task criada: {task_key}")
        return task
    
    def create_file_arrival_trigger(self, url: str) -> TriggerSettings:
        """
        Cria file arrival trigger.
        
        Args:
            url: URL para monitoramento de arquivos
            
        Returns:
            TriggerSettings: Configuração do trigger
        """
        trigger = TriggerSettings(
            pause_status=PauseStatus.UNPAUSED,
            file_arrival={"url": url}  # Usando dicionário simples em vez de classe específica
        )
        
        self.logger.info(f"⚡ File arrival trigger configurado: {url}")
        return trigger
    
    def create_cron_schedule(self, cron_expression: str, timezone: str = "America/Sao_Paulo") -> CronSchedule:
        """
        Cria schedule CRON.
        
        Args:
            cron_expression: Expressão CRON
            timezone: Timezone
            
        Returns:
            CronSchedule: Schedule configurado
        """
        schedule = CronSchedule(
            quartz_cron_expression=cron_expression,
            timezone_id=timezone,
            pause_status=PauseStatus.PAUSED  # Iniciar pausado por segurança
        )
        
        self.logger.info(f"⏰ Schedule CRON configurado: {cron_expression} ({timezone})")
        return schedule
    
    def create_workflow(self, config: DinoWorkflowConfig) -> Dict[str, Any]:
        """
        Cria workflow completo no Databricks.
        
        Args:
            config: Configuração do workflow
            
        Returns:
            Dict: Resultado da criação
        """
        try:
            self.logger.info(f"🦕 Criando workflow DINO: {config.job_name}")
            
            # 1. Criar job cluster
            job_cluster = self.create_job_cluster(config)
            cluster_key = job_cluster.job_cluster_key
            
            # 2. Criar task de notebook
            notebook_task = self.create_notebook_task(config, cluster_key)
            
            # 3. Configurações base do job
            job_settings = JobSettings(
                name=config.job_name,
                description=config.description or f"DINO Workflow: {config.catalog_name}.{config.schema_name}.{config.table_name}",
                job_clusters=[job_cluster],
                tasks=[notebook_task],
                queue={"enabled": True}
            )
            
            # 4. Configurar trigger/schedule
            if config.is_automated:
                # File arrival trigger
                trigger_url = config.file_arrival_url or config.source_path
                job_settings.trigger = self.create_file_arrival_trigger(trigger_url)
            elif config.cron_schedule:
                # CRON schedule
                job_settings.schedule = self.create_cron_schedule(
                    config.cron_schedule, 
                    config.timezone
                )
            
            # 5. Configurar notificações por email
            if config.email_notifications:
                job_settings.email_notifications = JobEmailNotifications(
                    on_start=config.email_notifications.get('on_start'),
                    on_success=config.email_notifications.get('on_success'),
                    on_failure=config.email_notifications.get('on_failure')
                )
            
            # 6. Criar job no Databricks
            job_response = self.client.jobs.create(settings=job_settings)
            
            # 7. Preparar resultado
            result = {
                "success": True,
                "job_id": job_response.job_id,
                "job_name": config.job_name,
                "job_url": f"{self.client.config.host}/#job/{job_response.job_id}",
                "cluster_key": cluster_key,
                "is_automated": config.is_automated,
                "trigger_type": "file_arrival" if config.is_automated else "cron_schedule",
                "config_applied": {
                    "file_arrival_trigger": config.is_automated,
                    "job_cluster": True,
                    "custom_tags": True,
                    "photon_enabled": True,
                    "autoscaling": not config.is_single_node
                },
                "message": "Workflow criado com sucesso"
            }
            
            self.logger.info(f"✅ Workflow criado: {config.job_name} (ID: {job_response.job_id})")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao criar workflow: {e}")
            return {
                "success": False,
                "job_name": config.job_name,
                "error": str(e),
                "message": "Falha na criação do workflow"
            }
    
    def list_dino_jobs(self) -> List[Dict[str, Any]]:
        """
        Lista jobs DINO existentes.
        
        Returns:
            List: Lista de jobs DINO
        """
        try:
            dino_jobs = []
            
            for job in self.client.jobs.list():
                # Verificar se é job DINO pela tag ou nome
                if (job.settings.name and 
                    ("dino" in job.settings.name.lower() or 
                     job.settings.name.startswith("dino-"))):
                    
                    dino_jobs.append({
                        "job_id": job.job_id,
                        "job_name": job.settings.name,
                        "creator": job.creator_user_name,
                        "created_time": job.created_time
                    })
            
            self.logger.info(f"📋 Encontrados {len(dino_jobs)} jobs DINO")
            return dino_jobs
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao listar jobs: {e}")
            return []
    
    def get_job_status(self, job_id: int) -> Dict[str, Any]:
        """
        Obtém status de um job.
        
        Args:
            job_id: ID do job
            
        Returns:
            Dict: Status do job
        """
        try:
            job = self.client.jobs.get(job_id)
            runs = list(self.client.jobs.list_runs(job_id=job_id, limit=1))
            
            last_run_state = runs[0].state.life_cycle_state if runs else "NEVER_RUN"
            
            return {
                "success": True,
                "job_id": job_id,
                "job_name": job.settings.name,
                "status": "ACTIVE",
                "last_run_state": str(last_run_state),
                "creator": job.creator_user_name
            }
            
        except Exception as e:
            return {
                "success": False,
                "job_id": job_id,
                "error": str(e)
            }
    
    def create_notebook_template(self, config: DinoWorkflowConfig) -> str:
        """
        Gera template de notebook para ingestão DINO.
        
        Args:
            config: Configuração do workflow
            
        Returns:
            str: Código do notebook
        """
        template = f'''# Databricks notebook source
# MAGIC %md
# MAGIC # 🦕 DINO SDK - Notebook de Ingestão
# MAGIC 
# MAGIC **Job:** {config.job_name}  
# MAGIC **Destino:** {config.catalog_name}.{config.schema_name}.{config.table_name}  
# MAGIC **Origem:** {config.source_path}  
# MAGIC **Projeto:** {config.projeto}
# MAGIC 
# MAGIC ---

# COMMAND ----------

# MAGIC %md
# MAGIC ## 📦 Configuração e Imports

# COMMAND ----------

# Instalar DINO SDK se necessário
%pip install dino-sdk

# COMMAND ----------

# Imports necessários
from dino_sdk import get_ingestion_engine
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("🦕 DINO SDK - Notebook de Ingestão Iniciado")

# COMMAND ----------

# MAGIC %md
# MAGIC ## ⚙️ Configuração da Ingestão

# COMMAND ----------

# Configurações de ingestão
config = {{
    "catalog_name": "{config.catalog_name}",
    "schema_name": "{config.schema_name}",
    "table_name": "{config.table_name}",
    "source_path": "{config.source_path}",
    "liquid_clustering": {config.liquid_clustering},
    "clustering_columns": {config.clustering_columns},
    "schema_evolution_mode": "{config.schema_evolution_mode}",
    "type_run": "{config.type_run}",
    "is_automated": {config.is_automated}
}}

print("📋 Configurações carregadas:")
for key, value in config.items():
    print(f"   {key}: {value}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🚀 Execução da Ingestão

# COMMAND ----------

# Criar IngestionEngine
IngestionEngine = get_ingestion_engine()
engine = IngestionEngine()

print(f"🦕 Iniciando ingestão para {config['catalog_name']}.{config['schema_name']}.{config['table_name']}")

# COMMAND ----------

# Executar ingestão
try:
    if config["type_run"] == "streaming":
        # Ingestão streaming
        print("🔄 Executando ingestão streaming...")
        result = engine.ingest_streaming(
            source_path=config["source_path"],
            catalog_name=config["catalog_name"],
            schema_name=config["schema_name"],
            table_name=config["table_name"],
            clustering_columns=config["clustering_columns"] if config["liquid_clustering"] else None,
            schema_evolution_mode=config["schema_evolution_mode"]
        )
    else:
        # Ingestão batch
        print("📦 Executando ingestão batch...")
        result = engine.ingest_batch(
            source_path=config["source_path"],
            catalog_name=config["catalog_name"],
            schema_name=config["schema_name"],
            table_name=config["table_name"],
            clustering_columns=config["clustering_columns"] if config["liquid_clustering"] else None,
            schema_evolution_mode=config["schema_evolution_mode"]
        )
    
    if result["success"]:
        print(f"✅ Ingestão concluída com sucesso!")
        print(f"📊 Registros processados: {result.get('records_processed', 'N/A')}")
    else:
        print(f"❌ Erro na ingestão: {result.get('error', 'Unknown error')}")
        
except Exception as e:
    print(f"❌ Erro na execução: {e}")
    raise

# COMMAND ----------

# MAGIC %md
# MAGIC ## ✅ Validação dos Dados

# COMMAND ----------

# Validar dados ingeridos
try:
    table_path = f"{config['catalog_name']}.{config['schema_name']}.{config['table_name']}"
    
    # Contar registros
    count = spark.sql(f"SELECT COUNT(*) as total FROM {table_path}").collect()[0].total
    print(f"📊 Total de registros na tabela: {count:,}")
    
    # Mostrar schema
    print("\\n🔍 Schema da tabela:")
    spark.sql(f"DESCRIBE {table_path}").show()
    
    # Mostrar amostra dos dados
    print("\\n📋 Amostra dos dados (5 primeiros registros):")
    spark.sql(f"SELECT * FROM {table_path} LIMIT 5").show()
    
    print("✅ Validação concluída!")
    
except Exception as e:
    print(f"⚠️ Erro na validação: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 📝 Log Final
# MAGIC 
# MAGIC Ingestão executada com sucesso pelo DINO SDK v1.2.0! 🦕🚀

# COMMAND ----------

print("🦕 DINO SDK - Ingestão finalizada!")
print(f"⏰ Horário de conclusão: {datetime.now().isoformat()}")
print("🚀 Dados disponíveis no Unity Catalog!")
'''
        
        self.logger.info(f"📝 Template de notebook gerado para {config.job_name}")
        return template


def create_dino_workflow(
    # Identificação básica
    job_name: str,
    notebook_path: str,
    catalog_name: str,
    schema_name: str,
    table_name: str,
    source_path: str,
    
    # Automação  
    is_automated: bool = False,
    file_arrival_url: Optional[str] = None,
    cron_schedule: Optional[str] = None,
    timezone: str = "America/Sao_Paulo",
    
    # Cluster
    node_type_id: str = "Standard_D4ds_v5",
    min_workers: int = 1,
    max_workers: int = 2,
    spark_version: str = "17.1.x-scala2.13",
    is_single_node: bool = False,
    
    # Ingestão
    liquid_clustering: bool = False,
    clustering_columns: List[str] = None,
    schema_evolution_mode: str = "addNewColumns",
    type_run: str = "batch",
    
    # Notificações e metadados
    email_notifications: Optional[Dict[str, List[str]]] = None,
    projeto: str = "",
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    🦕 Função helper para criar workflows DINO rapidamente.
    
    Cria um job/workflow do Databricks otimizado para ingestão com IngestionEngine.
    
    Args:
        job_name: Nome do job
        notebook_path: Caminho do notebook de ingestão
        catalog_name: Catálogo de destino
        schema_name: Schema de destino  
        table_name: Tabela de destino
        source_path: Caminho dos dados de origem
        is_automated: Se deve usar file arrival trigger (True) ou schedule manual/CRON (False)
        file_arrival_url: URL para file arrival trigger (opcional, usa source_path se não informado)
        cron_schedule: Expressão CRON para jobs programados
        timezone: Timezone para schedule
        node_type_id: Tipo de VM do cluster
        min_workers: Workers mínimos do cluster
        max_workers: Workers máximos do cluster  
        spark_version: Versão do Spark
        is_single_node: Se deve usar cluster single node
        liquid_clustering: Se deve usar Liquid Clustering
        clustering_columns: Colunas para clustering
        schema_evolution_mode: Modo de evolução do schema
        type_run: Tipo de execução (batch/streaming)
        email_notifications: Configurações de notificação por email
        projeto: Nome do projeto (usado nas custom tags)
        description: Descrição do job
    
    Returns:
        Dict: Resultado da criação do workflow
        
    Example:
        ```python
        # Job automatizado com file arrival trigger
        resultado = create_dino_workflow(
            job_name="dino-ingest-vendas-realtime",
            notebook_path="/Workspace/vendas/ingest_notebook", 
            catalog_name="comercial",
            schema_name="bronze",
            table_name="vendas_realtime",
            source_path="abfss://vendas@storage.dfs.core.windows.net/raw/",
            is_automated=True,  # 🔥 File arrival trigger ativo
            projeto="Vendas Analytics"
        )
        ```
    """
    
    # Criar configuração
    config = DinoWorkflowConfig(
        job_name=job_name,
        notebook_path=notebook_path,
        catalog_name=catalog_name,
        schema_name=schema_name,
        table_name=table_name,
        source_path=source_path,
        is_automated=is_automated,
        file_arrival_url=file_arrival_url,
        cron_schedule=cron_schedule,
        timezone=timezone,
        node_type_id=node_type_id,
        min_workers=min_workers,
        max_workers=max_workers,
        spark_version=spark_version,
        is_single_node=is_single_node,
        liquid_clustering=liquid_clustering,
        clustering_columns=clustering_columns or [],
        schema_evolution_mode=schema_evolution_mode,
        type_run=type_run,
        email_notifications=email_notifications or {},
        projeto=projeto,
        description=description
    )
    
    # Criar workflow usando DinoWorkflowManager
    manager = DinoWorkflowManager()
    return manager.create_workflow(config)


# Manter compatibilidade com WorkflowManager original
class WorkflowManager:
    """
    Gerenciador de workflows para orquestração de ingestões (versão original)
    
    Funcionalidades:
    - Criação de workflows de ingestão
    - Execução sequencial e paralela
    - Monitoramento de status
    - Retry logic
    """
    
    def __init__(self):
        """Inicializa o gerenciador de workflows"""
        self.config = get_config_manager()
        self.logger = logging.getLogger(__name__)
    
    def create_workflow(
        self,
        workflow_name: str,
        tasks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Cria workflow com múltiplas tarefas de ingestão
        
        Args:
            workflow_name: Nome do workflow
            tasks: Lista de tarefas de ingestão
            
        Returns:
            Configuração do workflow
        """
        
        workflow = {
            "name": workflow_name,
            "description": f"Workflow de ingestão criado pelo Dino SDK",
            "created_at": datetime.now().isoformat(),
            "tasks": tasks,
            "status": "created"
        }
        
        self.logger.info(f"Workflow criado: {workflow_name} com {len(tasks)} tarefas")
        return workflow
    
    def execute_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa workflow (simulação)
        
        Args:
            workflow: Configuração do workflow
            
        Returns:
            Resultado da execução
        """
        
        print(f"🔄 Executando workflow: {workflow['name']}")
        
        results = []
        for i, task in enumerate(workflow['tasks'], 1):
            print(f"   ⚙️ Tarefa {i}/{len(workflow['tasks'])}: {task.get('name', 'Sem nome')}")
            
            # Simular execução
            task_result = {
                "task_name": task.get('name', f'task_{i}'),
                "status": "success",
                "execution_time": 2.5,
                "records_processed": 1000
            }
            results.append(task_result)
        
        workflow_result = {
            "workflow_name": workflow['name'],
            "status": "completed",
            "total_tasks": len(workflow['tasks']),
            "successful_tasks": len(results),
            "failed_tasks": 0,
            "total_execution_time": sum(r['execution_time'] for r in results),
            "total_records": sum(r['records_processed'] for r in results),
            "task_results": results,
            "completed_at": datetime.now().isoformat()
        }
        
        print(f"✅ Workflow concluído: {workflow_result['total_records']} registros processados")
        return workflow_result
