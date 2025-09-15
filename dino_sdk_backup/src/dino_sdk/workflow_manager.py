#!/usr/bin/env python3
"""
🦕 DINO SDK v1.2.0 - Workflow Manager

Classe para criar e gerenciar workflows/jobs do Databricks que utilizam o IngestionEngine.
Suporte para job clusters, triggers file_arrival e configurações avançadas.

Autor: DINO SDK Team
Versão: 1.2.0
"""

import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.jobs import (
    PauseStatus
)
# Usando apenas dicionários para máxima compatibilidade com Databricks SDK
# Removidos todos os imports de classes que serão substituídas por dicionários

# ✅ NOVO: Import schema_manager para criar diretórios no volume
try:
    from .schema_manager import SchemaManager
except ImportError:
    # Fallback para importação direta se estiver sendo executado como módulo independente
    from schema_manager import SchemaManager

logger = logging.getLogger(__name__)

@dataclass
class DinoWorkflowConfig:
    """
    Configuração para criação de workflows DINO
    """
    # Informações básicas
    job_name: str
    notebook_path: str
    
    # Parâmetros de ingestão
    catalog_name: str
    schema_name: str
    table_name: str
    source_path: str
    
    # Configurações do job
    is_automated: bool = False
    file_arrival_url: Optional[str] = None
    cron_schedule: Optional[str] = None
    timezone: str = "America/Sao_Paulo"
    
    # Configurações do cluster (para job_cluster)
    existing_cluster_id: Optional[str] = None  # ✅ Suporte a cluster existente (opcional)
    node_type_id: str = "Standard_F4"  # ✅ Node type para job_cluster
    spark_version: str = "16.4.x-scala2.13"   # ✅ Spark version para job_cluster
    autotermination_minutes: int = 10  # ✅ Auto-terminate para job_cluster
    single_node: bool = True  # ✅ Single node cluster por padrão
    
    # Configurações avançadas
    liquid_clustering: bool = True
    clustering_columns: Optional[List[str]] = None
    schema_evolution_mode: str = "rescue"
    type_run: str = "batch"
    
    # Notificações
    email_notifications: Optional[Dict[str, List[str]]] = None
    
    # Tags customizadas
    projeto: Optional[str] = None
    description: Optional[str] = None

class DinoWorkflowManager:
    """
    Gerenciador de workflows para o DINO SDK
    
    Cria e gerencia jobs do Databricks que utilizam o IngestionEngine
    com configurações otimizadas e suporte a file arrival triggers.
    """
    
    def __init__(self, workspace_client: Optional[WorkspaceClient] = None):
        """
        Inicializa o WorkflowManager
        
        Args:
            workspace_client: Cliente do Databricks Workspace (opcional)
        """
        # self.client = workspace_client or WorkspaceClient()
        self.client = WorkspaceClient()
        self.logger = logging.getLogger(__name__)

    def _get_schema_location(self, catalog_name: str, schema_name: str) -> Optional[str]:
        """
        Obtém o location do schema Unity Catalog
        
        Args:
            catalog_name: Nome do catálogo
            schema_name: Nome do schema
            
        Returns:
            Location do schema ou None se não encontrado
        """
        try:
            # Query para obter informações do schema
            schema_info = self.client.schemas.get(f"{catalog_name}.{schema_name}")
            
            # Se o schema tem storage_location definido, usar ele
            if hasattr(schema_info, 'storage_location') and schema_info.storage_location:
                location = schema_info.storage_location
                self.logger.info(f"📍 Location do schema encontrado: {location}")
                return location
            
        except Exception as e:
            self.logger.warning(f"⚠️ Schema {catalog_name}.{schema_name} não encontrado: {e}")
        
        # Fallback: tentar obter via external location do catálogo
        try:
            catalogs = self.client.catalogs.list()
            for catalog in catalogs:
                if catalog.name == catalog_name:
                    # Verificar se tem storage_location
                    if hasattr(catalog, 'storage_location') and catalog.storage_location:
                        base_location = catalog.storage_location.rstrip('/')
                        schema_location = f"{base_location}/{catalog_name}/{schema_name}"
                        self.logger.info(f"📍 Location gerado a partir do catálogo: {schema_location}")
                        return schema_location
                    
                    # Se não tem storage_location, tentar uma convenção padrão
                    # Para catálogos main, usar convenção DBFS/Unity Catalog
                    if catalog_name == "main":
                        default_location = f"abfss://unity-catalog-storage@storage.dfs.core.windows.net/{catalog_name}/{schema_name}"
                        self.logger.info(f"📍 Usando location padrão para catálogo main: {default_location}")
                        return default_location
                    
        except Exception as e:
            self.logger.warning(f"Não foi possível obter location do catálogo: {e}")
        
        # Fallback final: convenção baseada no nome do catálogo
        try:
            # Para data_master_dev_dbw, usar uma convenção esperada
            if "data_master" in catalog_name.lower():
                default_location = f"abfss://datalake@{catalog_name.lower().replace('_', '')}.dfs.core.windows.net/{schema_name}"
                self.logger.info(f"📍 Usando location baseado em convenção: {default_location}")
                return default_location
        except Exception as e:
            self.logger.warning(f"Falha na convenção de naming: {e}")
        
        # Se não conseguir obter, retornar None
        self.logger.warning(f"⚠️ Não foi possível determinar location do schema {catalog_name}.{schema_name}")
        return None
    
    def _resolve_paths(self, config: DinoWorkflowConfig) -> DinoWorkflowConfig:
        """
        Resolve automaticamente source_path e file_arrival_url baseados no location do schema
        
        Args:
            config: Configuração do workflow
            
        Returns:
            Configuração com paths resolvidos
        """
        # Se source_path não começa com abfss:// ou outros protocolos, tentar resolver
        if not any(config.source_path.startswith(proto) for proto in ['abfss://', 'adls://', 's3://', 'gs://']):
            schema_location = self._get_schema_location(config.catalog_name, config.schema_name)
            if schema_location:
                # Gerar source_path: {location_schema}/{table_name}/
                resolved_source = f"{schema_location.rstrip('/')}/{config.table_name}/"
                config.source_path = resolved_source
                self.logger.info(f"🔧 Source path resolvido: {resolved_source}")
        
        # Se file_arrival_url não está definida e is_automated=True, gerar automaticamente
        if config.is_automated and not config.file_arrival_url:
            # Usar sintaxe de Volumes: /Volumes/{catalog}/{schema}/raw/{table}/
            # Não usar ABFSS path que causa erro "overlaps with another external table"
            volumes_path = f"/Volumes/{config.catalog_name}/{config.schema_name}/raw/{config.table_name}/"
            config.file_arrival_url = volumes_path
            self.logger.info(f"🔧 File arrival URL resolvido (Volumes): {volumes_path}")
        
        return config
        
    def create_workflow(self, config: DinoWorkflowConfig) -> Dict[str, Any]:
        """
        Cria um workflow/job do Databricks para ingestão DINO
        
        Args:
            config: Configuração do workflow
            
        Returns:
            Dict com informações do job criado
        """
        try:
            self.logger.info(f"🚀 Criando workflow: {config.job_name}")
            
            # Resolver paths automaticamente baseados no schema location
            config = self._resolve_paths(config)
            
            # Validar configuração
            self._validate_config(config)
            
            # Remover criação automática de cluster - agora usa job_cluster!
            # Job clusters são mais eficientes que clusters dedicados para jobs
            self.logger.info("🔧 Usando job_cluster - cluster será criado sob demanda pelo job")
            
            # Remover job existente se houver
            self._delete_existing_job(config.job_name)
            
            # ✅ NOVO: Criar diretório no volume para jobs com file_arrival
            # if config.is_automated and config.file_arrival_url:
            self.logger.info("📁 Criando diretório da tabela no volume RAW")
            self._create_volume_directory_for_file_arrival(config)
            
            # Comentar job_settings antigo - usando nova implementação com ClusterSpec
            # job_settings = self._build_job_settings(config)
            
            # Removido DEBUG antigo - usando nova implementação direta
            
            # SOLUÇÃO: Usar EXATAMENTE o código que funciona na sua referência
            self.logger.info(f"🔍 Usando código EXATO da sua referência que funciona...")
            
            try:
                from databricks.sdk.service.jobs import Task, NotebookTask, Source, JobSettings as Job, TriggerSettings, FileArrivalTriggerConfiguration, PauseStatus,NotebookTask
                from databricks.sdk.service.compute import ClusterSpec, Library

                # ✅ Se tem file arrival, usar SEU CÓDIGO EXATO - apenas substituir valores
                if config.file_arrival_url:
                    self.logger.info(f"🔗 Usando SEU CÓDIGO EXATO - apenas substituindo valores!")
                    
                    # Job cluster para file arrival trigger
                    from databricks.sdk.service.compute import ClusterSpec
                    
                    job_cluster = ClusterSpec(
                        spark_version=config.spark_version,
                        node_type_id=config.node_type_id,
                        num_workers=0,  # single node job cluster
                        # REMOVIDO: autotermination_minutes - job clusters não suportam
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

                    trigger_conf = FileArrivalTriggerConfiguration(
                                    url=config.file_arrival_url
                                    )
                    
                    trigger = TriggerSettings(
                        pause_status=PauseStatus.UNPAUSED,
                        file_arrival=trigger_conf
                    )

                    # notebook_task = NotebookTask({
                    #                                 "catalog_name": config.catalog_name,
                    #                                 "schema_name": config.schema_name,
                    #                                 "table_name": config.table_name,
                    #                                 "source_path": f"/Volumes/{config.catalog_name}/{config.schema_name}/raw/"
                    #                             })

                    libraries = Library(
                                whl="/Workspace/dino/dino_sdk.whl"
                    )

                    task = Task(
                        task_key="dino_ingestion_task",
                        new_cluster=job_cluster,
                        libraries=[libraries],
                        notebook_task=NotebookTask(
                            notebook_path=config.notebook_path,
                            source=Source.WORKSPACE,
                            base_parameters={
                                "catalog_name": config.catalog_name,
                                "schema_name": config.schema_name,
                                "table_name": config.table_name,
                                "source_path": f"/Volumes/{config.catalog_name}/{config.schema_name}/raw/"
                            }
                        )
                    )

                    job = self.client.jobs.create(
                        name=config.job_name,
                        trigger=trigger,
                        tasks=[task]
                    )

                    self.logger.info(f"Job com trigger criado! Job ID: {job.job_id}")
                    
                else:
                    # ✅ Sem trigger - usar sintaxe simples que já funcionou
                    # task = Task(
                    #     task_key="dino_ingestion_task",
                    #     existing_cluster_id=config.existing_cluster_id if config.existing_cluster_id else None,
                    #     notebook_task=NotebookTask(
                    #         notebook_path=config.notebook_path,
                    #         source=Source.WORKSPACE  # ✅ CORREÇÃO: Source.WORKSPACE
                    #     )
                    # )
                    
                    # Job cluster configuração para single node
                    from databricks.sdk.service.compute import ClusterSpec
                    
                    job_cluster = ClusterSpec(
                        spark_version=config.spark_version,
                        node_type_id=config.node_type_id,
                        num_workers=0,  # single node job cluster
                        # REMOVIDO: autotermination_minutes - job clusters não suportam
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


                    task = Task(
                        task_key="dino_ingestion_task",
                        new_cluster=job_cluster,
                        libraries=[{
                            "whl": "/Workspace/dino/dino_sdk-2.4.0-py3-none-any.whl",
                        }],
                        notebook_task=NotebookTask(
                            notebook_path=config.notebook_path,
                            source=Source.WORKSPACE,
                            base_parameters={
                                "catalog_name": config.catalog_name,
                                "schema_name": config.schema_name,
                                "table_name": config.table_name,
                                "source_path": f"/Volumes/{config.catalog_name}/{config.schema_name}/raw/"
                            }
                        )
                    )

                    job = self.client.jobs.create(
                        name=config.job_name,
                        tasks=[task]
                    )
                
                self.logger.info(f"Job criado com sucesso! Job ID: {job.job_id}")
                
                # ✅ SUCESSO! Usar o job criado diretamente
                # Não precisa de versão "completa" - a sintaxe da sua referência já é completa
                self.logger.info(f"✅ Job completo criado com sintaxe da sua referência!")
                
            except ValueError as ve:
                self.logger.error(f"❌ Erro de configuração: {ve}")
                raise ve
                
            except Exception as direct_error:
                self.logger.error(f"❌ Erro com sintaxe direta: {direct_error}")
                import traceback
                self.logger.error(f"🔍 STACK TRACE COMPLETO:")
                self.logger.error(traceback.format_exc())
                raise direct_error
            
            result = {
                'success': True,
                'job_id': job.job_id,
                'job_name': config.job_name,
                'job_url': f"{self.client.config.host}/#job/{job.job_id}",
                'config_applied': {
                    'is_automated': config.is_automated,
                    'file_arrival_trigger': config.file_arrival_url is not None,
                    'job_cluster': True,
                    'liquid_clustering': config.liquid_clustering
                }
            }
            
            self.logger.info(f"Workflow criado com sucesso: {config.job_name}")
            self.logger.info(f"URL do job: {result['job_url']}")
            
            return result
            
        except Exception as e:
            error_msg = f"Erro ao criar workflow {config.job_name}: {str(e)}"
            self.logger.error(error_msg)
            import traceback
            self.logger.error(f"Stack trace completo:")
            self.logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': str(e),
                'job_name': config.job_name
            }
    
    def _validate_config(self, config: DinoWorkflowConfig) -> None:
        """Valida a configuração do workflow"""
        
        required_fields = [
            'job_name', 'notebook_path', 'catalog_name', 
            'schema_name', 'table_name', 'source_path'
        ]
        
        for field in required_fields:
            if not getattr(config, field):
                raise ValueError(f"Campo obrigatório '{field}' não fornecido")
        
        # Validar trigger automatizado
        if config.is_automated and not config.file_arrival_url:
            # Tentar resolver automaticamente antes de falhar
            schema_location = self._get_schema_location(config.catalog_name, config.schema_name)
            if schema_location:
                # Se conseguimos obter o location, a validação passou (será resolvido depois)
                self.logger.info("✅ file_arrival_url será resolvido automaticamente")
            else:
                raise ValueError("file_arrival_url é obrigatório quando is_automated=True e não foi possível resolver automaticamente o schema location")
        
        # Validar schedule manual
        if not config.is_automated and not config.cron_schedule:
            config.cron_schedule = "0 0 6 * * ?"  # Default: 6h da manhã diariamente
            self.logger.info("⏰ Usando schedule padrão: 6h da manhã diariamente")
    
    def _delete_existing_job(self, job_name: str) -> None:
        """Remove job existente com o mesmo nome"""
        
        try:
            for job in self.client.jobs.list():
                if job.settings and job.settings.name == job_name:
                    self.client.jobs.delete(job_id=job.job_id)
                    self.logger.info(f"🗑️ Job existente removido: {job_name}")
                    break
        except Exception as e:
            self.logger.warning(f"⚠️ Erro ao remover job existente: {e}")
    
    def _create_volume_directory_for_file_arrival(self, config: DinoWorkflowConfig) -> None:
        """
        Cria o diretório da tabela no volume quando o job tem file_arrival habilitado
        
        Este método garante que existe um diretório específico para a tabela no volume,
        onde os arquivos serão depositados e monitorados pelo file_arrival trigger.
        
        Args:
            config: Configuração do workflow com informações da tabela e volume
        """
        try:
            self.logger.info(f"📁 Criando diretório no volume RAW: {config.table_name}")
            
            # Construir o path do diretório no volume
            # Formato: /Volumes/{catalog}/{schema}/raw/{table_name}/
            volume_directory_path = f"/Volumes/{config.catalog_name}/{config.schema_name}/raw/{config.table_name}"
            
            self.logger.info(f"🎯 Path do diretório: {volume_directory_path}")
            
            # Usar WorkspaceClient para executar comando Python no workspace
            # Isso simula a execução de dbutils.fs.mkdirs() no Databricks
            try:
                # Tentar usar a API do Databricks para criar diretório
                from databricks.sdk.service.workspace import Language
                
                # Código Python para criar diretório usando dbutils
#                 create_directory_code = f"""
# # Criar diretório no volume se não existir
# try:
#     dbutils.fs.mkdirs("{volume_directory_path}")
#     print(f"✅ Diretório criado: {volume_directory_path}")
# except Exception as e:
#     print(f"⚠️ Diretório pode já existir ou erro: {{e}}")
# """           
                self.client.dbfs.mkdirs(volume_directory_path)
                
                # Executar o código através da API do workspace (se possível)
                # Por enquanto, apenas logar que o diretório deveria ser criado
                self.logger.info(f"📋 Comando para criar diretório: dbfs.mkdirs('{volume_directory_path}')")
                
                self.logger.info(f"✅ Diretório configurado para criação: {volume_directory_path}")
                
            except Exception as api_error:
                self.logger.warning(f"⚠️ Não foi possível criar diretório via API: {api_error}")
                self.logger.info("💡 O diretório será criado automaticamente quando o primeiro arquivo chegar")
            
            # Atualizar o file_arrival_url para apontar para o diretório específico da tabela
            if not config.file_arrival_url or config.file_arrival_url.endswith("/raw/"):
                config.file_arrival_url = volume_directory_path
                self.logger.info(f"🔗 File arrival URL atualizada: {config.file_arrival_url}")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao configurar diretório no volume: {e}")
            self.logger.warning(f"⚠️ Continuando criação do job - diretório será criado automaticamente no primeiro file arrival")
            # Não falha a criação do job - apenas registra o erro
    
    def _build_job_settings(self, config: DinoWorkflowConfig) -> Dict[str, Any]:
        """Constrói as configurações do job como dicionário"""
        
        # Configurar trigger
        trigger = None
        schedule = None
        
        if config.is_automated and config.file_arrival_url:
            # Trigger file arrival para jobs automatizados (dicionário)
            trigger = {
                "pause_status": "UNPAUSED",
                "file_arrival": {"url": config.file_arrival_url}
            }
        else:
            # Schedule CRON para jobs manuais/programados (dicionário)
            schedule = {
                "quartz_cron_expression": config.cron_schedule,
                "timezone_id": config.timezone,
                "pause_status": "PAUSED"  # Inicia pausado
            }
        
        # Configurar job cluster
        new_cluster_config = self._build_job_cluster(config)
        
        # Configurar task
        task = self._build_main_task(config)
        
        # Configurar notificações  
        email_notifications = self._build_email_notifications(config)
        
        # Montar configuração final como dicionário
        job_settings = {
            "name": config.job_name,
            "email_notifications": email_notifications,
            "job_clusters": [{
                "job_cluster_key": "dino_cluster",
                "new_cluster": new_cluster_config
            }],
            "tasks": [task],
            "queue": {"enabled": True}  # Habilitar queue para melhor gerenciamento
        }
        
        # Adicionar trigger ou schedule
        if config.is_automated and config.file_arrival_url:
            job_settings["trigger"] = {
                "pause_status": "UNPAUSED",
                "file_arrival": {"url": config.file_arrival_url}
            }
        else:
            job_settings["schedule"] = {
                "quartz_cron_expression": config.cron_schedule,
                "timezone_id": config.timezone,
                "pause_status": "PAUSED"  # Inicia pausado
            }
        
        return job_settings
    
    def _build_job_cluster(self, config: DinoWorkflowConfig) -> Dict[str, Any]:
        """
        Constrói configuração de job cluster usando dicionário new_cluster.
        
        CORREÇÃO v1.3.8: new_cluster deve ser um dicionário, não uma classe NewCluster.
        Baseado na documentação oficial do Databricks SDK.
        """
        
        # Tags personalizados
        custom_tags = {
            "created_by": "dino_sdk",
            "version": "1.3.8",
            "projeto": config.projeto or "DINO_SDK",
            "catalog": config.catalog_name,
            "schema": config.schema_name,
            "table": config.table_name
        }
        
        if config.description:
            custom_tags["description"] = config.description[:50]  # Limitar tamanho
        
        # Configuração base do new_cluster como dicionário
        new_cluster = {
            # Configurações obrigatórias
            "spark_version": config.spark_version,
            "node_type_id": config.node_type_id,
            
            # Auto-terminação para economia
            "autotermination_minutes": 30,
            
            # Tags personalizados
            "custom_tags": custom_tags,
            
            # Environment variables
            "spark_env_vars": {
                "PYTHONPATH": "/databricks/python_shell/scripts:/databricks/python/lib/python3.9/site-packages"
            },
            
            # Azure Spot instances para economia
            "azure_attributes": {
                "availability": "SPOT_WITH_FALLBACK_AZURE",
                "first_on_demand": 1,
                "spot_bid_max_price": -1.0
            }
        }
        
        # Configurar workers baseado no tipo (single node vs multi-node)
        if config.single_node:  # ✅ CORREÇÃO: config.single_node (não is_single_node)
            new_cluster["num_workers"] = 0  # Single node
            # ✅ Adicionar configurações single node do seu exemplo
            new_cluster["spark_conf"] = {
                "spark.databricks.cluster.profile": "singleNode",
                "spark.master": "local[*]",
            }
            new_cluster["custom_tags"] = {
                "ResourceClass": "SingleNode",
                "CreatedBy": "dino-sdk",
                "Purpose": "AutoIngestJob"
            }
        else:
            new_cluster["num_workers"] = 1  # ✅ CORREÇÃO: usar valor fixo para multi-node
            new_cluster["custom_tags"] = {
                "CreatedBy": "dino-sdk", 
                "Purpose": "AutoIngestJob"
            }
        
        return new_cluster
    
    def _build_main_task(self, config: DinoWorkflowConfig) -> Dict[str, Any]:
        """Constrói a task principal do job como dicionário"""
        
        # Parâmetros para o notebook
        notebook_params = self._build_notebook_parameters(config)
        
        # Task do notebook como dicionário
        task = {
            "task_key": "dino_ingestion_task",
            "description": f"DINO SDK Ingestion: {config.catalog_name}.{config.schema_name}.{config.table_name}",
            "job_cluster_key": "dino_cluster",
            "notebook_task": {
                "notebook_path": config.notebook_path,
                "source": "WORKSPACE",
                "base_parameters": {
                    "catalog_name": config.catalog_name,
                    "schema_name": config.schema_name,
                    "table_name": config.table_name,
                    "source_path": f"/Volumes/{config.catalog_name}/{config.schema_name}/raw/"
                }
            },
            "timeout_seconds": 3600  # 1 hora de timeout
        }
        
        return task
    
    def _build_notebook_parameters(self, config: DinoWorkflowConfig) -> Dict[str, str]:
        """Constrói parâmetros para o notebook"""
        
        params = {
            # Configurações básicas
            "catalog_name": config.catalog_name,
            "schema_name": config.schema_name,
            "table_name": config.table_name,
            "source_path": config.source_path,
            
            # Configurações avançadas
            "liquid_clustering": str(config.liquid_clustering),
            "schema_evolution_mode": config.schema_evolution_mode,
            "type_run": config.type_run,
            
            # Metadados
            "dino_version": "1.2.0",
            "job_type": "automated" if config.is_automated else "scheduled"
        }
        
        # Adicionar colunas de clustering se especificadas
        if config.clustering_columns:
            params["clustering_columns"] = ",".join(config.clustering_columns)
        
        return params
    
    def _build_email_notifications(self, config: DinoWorkflowConfig) -> Optional[Dict[str, List[str]]]:
        """Constrói configurações de notificação por email como dicionário"""
        
        if not config.email_notifications:
            return None
        
        return {
            "on_start": config.email_notifications.get('on_start', []),
            "on_success": config.email_notifications.get('on_success', []),
            "on_failure": config.email_notifications.get('on_failure', [])
        }
   
    def get_job_status(self, job_id: int) -> Dict[str, Any]:
        """
        Obtém status de um job
        
        Args:
            job_id: ID do job
            
        Returns:
            Dict com informações do status
        """
        try:
            job = self.client.jobs.get(job_id=job_id)
            runs = list(self.client.jobs.list_runs(job_id=job_id, limit=5))
            
            return {
                'success': True,
                'job_id': job_id,
                'job_name': job.settings.name if job.settings else "Unknown",
                'status': 'Active' if job.settings else 'Inactive',
                'recent_runs': len(runs),
                'last_run_state': runs[0].state.life_cycle_state if runs else "Never run"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'job_id': job_id
            }
    
    def list_dino_jobs(self) -> List[Dict[str, Any]]:
        """
        Lista todos os jobs DINO no workspace
        
        Returns:
            Lista de jobs DINO
        """
        try:
            dino_jobs = []
            
            for job in self.client.jobs.list():
                if job.settings and job.settings.name and "dino" in job.settings.name.lower():
                    dino_jobs.append({
                        'job_id': job.job_id,
                        'job_name': job.settings.name,
                        'creator': job.creator_user_name,
                        'created_time': job.created_time
                    })
            
            return dino_jobs
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao listar jobs DINO: {e}")
            return []


def create_dino_workflow(
    job_name: str,
    notebook_path: str,
    catalog_name: str,
    schema_name: str,
    table_name: str,
    source_path: str,
    is_automated: bool = False,
    file_arrival_url: Optional[str] = None,
    existing_cluster_id: Optional[str] = None,  # ✅ Cluster existente (opcional)
    node_type_id: str = "Standard_F4",  # ✅ Para job_cluster
    spark_version: str = "16.4.x-scala2.13",  # ✅ Para job_cluster
    autotermination_minutes: int = 10,  # ✅ Para job_cluster
    single_node: bool = True,  # ✅ Para job_cluster
    **kwargs
) -> Dict[str, Any]:
    """
    Função helper para criar workflows DINO facilmente
    
    Args:
        job_name: Nome do job
        notebook_path: Caminho do notebook no workspace
        catalog_name: Nome do catálogo
        schema_name: Nome do schema
        table_name: Nome da tabela
        source_path: Caminho dos dados de origem
        is_automated: Se deve usar file arrival trigger
        file_arrival_url: URL para file arrival (obrigatório se is_automated=True)
        existing_cluster_id: ID de cluster existente (opcional - usa job_cluster se não fornecido)
        node_type_id: Tipo do nó para job_cluster
        spark_version: Versão do Spark para job_cluster
        autotermination_minutes: Minutos para auto-terminate do job_cluster
        single_node: Se deve ser single node cluster
        **kwargs: Configurações adicionais
    
    Returns:
        Dict com resultado da criação
    """
    
    config = DinoWorkflowConfig(
        job_name=job_name,
        notebook_path=notebook_path,
        catalog_name=catalog_name,
        schema_name=schema_name,
        table_name=table_name,
        source_path=source_path,
        is_automated=is_automated,
        file_arrival_url=file_arrival_url,
        existing_cluster_id=existing_cluster_id,  # ✅ Cluster existente (opcional)
        node_type_id=node_type_id,  # ✅ Para job_cluster
        spark_version=spark_version,  # ✅ Para job_cluster
        autotermination_minutes=autotermination_minutes,  # ✅ Para job_cluster
        single_node=single_node,  # ✅ Para job_cluster
        **kwargs
    )
    
    manager = DinoWorkflowManager()
    return manager.create_workflow(config)


# Exemplo de uso
if __name__ == "__main__":
    """
    Exemplo de uso do WorkflowManager
    """
    print("🦕 DINO SDK v1.2.0 - Workflow Manager")
    print("Este módulo deve ser usado em notebooks Databricks")
    
    example_usage = '''
    # Exemplo de uso:
    
    from dino_sdk.workflow_manager import create_dino_workflow, DinoWorkflowConfig, DinoWorkflowManager
    
    # Método simples
    result = create_dino_workflow(
        job_name="ingest-vendas-bronze",
        notebook_path="/Workspace/Users/user@company.com/dino_ingestion_notebook",
        catalog_name="main",
        schema_name="bronze",
        table_name="vendas",
        source_path="abfss://container@storage.dfs.core.windows.net/raw/vendas/",
        is_automated=True,
        file_arrival_url="abfss://container@storage.dfs.core.windows.net/raw/vendas/",
        liquid_clustering=True,
        clustering_columns=["region", "date"]
    )
    
    # Método avançado
    config = DinoWorkflowConfig(
        job_name="ingest-sales-advanced",
        notebook_path="/Workspace/Users/user@company.com/advanced_notebook",
        catalog_name="main",
        schema_name="bronze", 
        table_name="sales_data",
        source_path="abfss://storage.dfs.core.windows.net/raw/sales/",
        is_automated=False,
        cron_schedule="0 0 8 * * ?",  # 8h da manhã
        liquid_clustering=True,
        clustering_columns=["customer_id", "order_date"],
        email_notifications={
            "on_failure": ["admin@company.com"],
            "on_success": ["team@company.com"]
        }
    )
    
    manager = DinoWorkflowManager()
    result = manager.create_workflow(config)
    
    if result['success']:
        print(f"Job criado: {result['job_url']}")
    else:
        print(f"Erro: {result['error']}")
    '''
    
    print(example_usage)