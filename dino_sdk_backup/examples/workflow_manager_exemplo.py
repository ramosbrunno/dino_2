#!/usr/bin/env python3
"""
🦕 DINO SDK v1.2.0 - Exemplo WorkflowManager

Exemplo prático de como criar workflows/jobs do Databricks que utilizam
o IngestionEngine com file arrival triggers e job clusters otimizados.

Casos de uso demonstrados:
1. Job manual com schedule CRON
2. Job automatizado com file arrival trigger  
3. Configuração avançada com clusters personalizados
4. Geração de templates de notebook
"""

from dino_sdk import (
    DinoWorkflowManager,
    DinoWorkflowConfig, 
    create_dino_workflow
)
from databricks.sdk import WorkspaceClient
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def exemplo_workflow_manual():
    """
    Exemplo 1: Workflow manual com schedule CRON
    Ideal para ETLs programados (ex: processamento diário)
    """
    
    print("🔧 Exemplo 1: Workflow Manual Programado")
    print("=" * 45)
    
    resultado = create_dino_workflow(
        # Identificação do job
        job_name="dino-ingest-vendas-diario",
        notebook_path="/Workspace/Users/user@company.com/vendas_diario_notebook",
        
        # Destino dos dados
        catalog_name="comercial",
        schema_name="bronze",
        table_name="vendas_diarias", 
        source_path="abfss://dados@empresa.dfs.core.windows.net/vendas/diario/",
        
        # Configurações de schedule
        is_automated=False,  # Job manual/programado
        cron_schedule="0 0 7 * * ?",  # Todo dia às 7h
        timezone="America/Sao_Paulo",
        
        # Configurações de ingestão
        liquid_clustering=True,
        clustering_columns=["data_venda", "regiao", "categoria"],
        schema_evolution_mode="rescue",
        type_run="batch",
        
        # Configurações de cluster
        node_type_id="Standard_D4ds_v5",
        min_workers=1,
        max_workers=4,
        
        # Notificações
        email_notifications={
            "on_failure": ["admin@empresa.com"],
            "on_success": ["vendas@empresa.com"]
        },
        
        # Metadados
        projeto="Vendas_Analytics"
    )
    
    print("📋 Resultado:")
    if resultado['success']:
        print(f"   ✅ Job criado: {resultado['job_name']}")
        print(f"   🔗 URL: {resultado['job_url']}")
        print(f"   🆔 ID: {resultado['job_id']}")
    else:
        print(f"   ❌ Erro: {resultado['error']}")
    
    return resultado


def exemplo_workflow_automatizado():
    """
    Exemplo 2: Workflow automatizado com file arrival trigger
    Ideal para ingestão em tempo real quando novos arquivos chegam
    """
    
    print("\n🔧 Exemplo 2: Workflow Automatizado (File Arrival)")
    print("=" * 55)
    
    resultado = create_dino_workflow(
        # Identificação do job
        job_name="dino-ingest-logs-realtime",
        notebook_path="/Workspace/Shared/DINO/logs_realtime_notebook",
        
        # Destino dos dados
        catalog_name="observabilidade",
        schema_name="logs_raw",
        table_name="application_logs",
        source_path="abfss://logs@sistema.dfs.core.windows.net/apps/",
        
        # 🔥 AUTOMAÇÃO ATIVA - File Arrival Trigger
        is_automated=True,
        file_arrival_url="abfss://logs@sistema.dfs.core.windows.net/apps/",
        
        # Configurações para streaming
        liquid_clustering=True,
        clustering_columns=["app_name", "log_level", "timestamp_hour"],
        schema_evolution_mode="addNewColumns",  # Novos campos de log
        type_run="streaming",  # Streaming para tempo real
        
        # Cluster otimizado para streaming
        node_type_id="Standard_D8ds_v5",  # Cluster maior
        min_workers=2,
        max_workers=8,  # Escalabilidade automática
        
        # Notificações críticas
        email_notifications={
            "on_failure": ["ops@empresa.com", "dev@empresa.com"],
            "on_success": ["logs-success@empresa.com"]
        },
        
        # Metadados
        projeto="Observabilidade_Platform"
    )
    
    print("📋 Resultado:")
    if resultado['success']:
        print(f"   ✅ Job automatizado criado: {resultado['job_name']}")
        print(f"   🔗 URL: {resultado['job_url']}")
        print(f"   ⚡ File Arrival: {resultado['config_applied']['file_arrival_trigger']}")
        print(f"   🏗️ Job Cluster: {resultado['config_applied']['job_cluster']}")
    else:
        print(f"   ❌ Erro: {resultado['error']}")
    
    return resultado


def exemplo_workflow_avancado():
    """
    Exemplo 3: Configuração avançada usando DinoWorkflowConfig
    Para casos complexos que precisam de controle total
    """
    
    print("\n🔧 Exemplo 3: Configuração Avançada")
    print("=" * 40)
    
    # Configuração detalhada
    config = DinoWorkflowConfig(
        # Informações básicas
        job_name="dino-advanced-customer-pipeline",
        notebook_path="/Workspace/Analytics/customer_advanced_notebook",
        
        # Destino
        catalog_name="customer_analytics",
        schema_name="bronze",
        table_name="customer_interactions",
        source_path="abfss://analytics@crm.dfs.core.windows.net/interactions/",
        
        # Automação sofisticada
        is_automated=True,
        file_arrival_url="abfss://analytics@crm.dfs.core.windows.net/interactions/",
        
        # Cluster enterprise
        node_type_id="Standard_D16ds_v5",  # Cluster potente
        min_workers=3,
        max_workers=15,  # Alta escalabilidade
        spark_version="17.1.x-scala2.13",
        is_single_node=False,
        
        # Ingestão avançada
        liquid_clustering=True,
        clustering_columns=["customer_segment", "interaction_date", "channel", "region"],
        schema_evolution_mode="rescue",
        type_run="streaming",
        
        # Notificações completas
        email_notifications={
            "on_start": ["pipeline-start@empresa.com"],
            "on_success": ["analytics@empresa.com", "marketing@empresa.com"],
            "on_failure": ["critical-alerts@empresa.com", "ops@empresa.com"]
        },
        
        # Configurações extras
        timezone="America/Sao_Paulo",
        projeto="Customer_360_Analytics"
    )
    
    # Usar WorkflowManager diretamente
    manager = DinoWorkflowManager()
    resultado = manager.create_workflow(config)
    
    print("📋 Resultado Avançado:")
    if resultado['success']:
        print(f"   ✅ Pipeline avançado criado: {config.job_name}")
        print(f"   🔗 URL: {resultado['job_url']}")
        print(f"   💎 Clustering: {config.clustering_columns}")
        print(f"   🖥️ Cluster: {config.node_type_id} ({config.min_workers}-{config.max_workers} workers)")
        print(f"   📧 Notificações: {len(config.email_notifications)} tipos configurados")
    else:
        print(f"   ❌ Erro: {resultado['error']}")
    
    return resultado, manager, config


def exemplo_template_notebook():
    """
    Exemplo 4: Geração de template de notebook
    O WorkflowManager pode gerar notebooks otimizados automaticamente
    """
    
    print("\n📝 Exemplo 4: Geração de Template de Notebook")
    print("=" * 50)
    
    # Configuração para gerar template
    template_config = DinoWorkflowConfig(
        job_name="template-example",
        notebook_path="/Workspace/Templates/exemplo_template",
        catalog_name="exemplos",
        schema_name="bronze",
        table_name="dados_exemplo",
        source_path="abfss://exemplos@storage.dfs.core.windows.net/dados/",
        liquid_clustering=True,
        clustering_columns=["categoria", "data_criacao"],
        is_automated=False
    )
    
    # Gerar template
    manager = DinoWorkflowManager()
    template_code = manager.create_notebook_template(template_config)
    
    # Estatísticas do template
    lines = template_code.split('\n')
    total_lines = len(lines)
    code_cells = template_code.count('# COMMAND ----------')
    magic_commands = template_code.count('# MAGIC')
    
    print(f"📋 Template Gerado:")
    print(f"   📄 Linhas totais: {total_lines}")
    print(f"   🔢 Células de código: {code_cells}")
    print(f"   ✨ Comandos mágicos: {magic_commands}")
    
    # Mostrar início do template
    print(f"\n📋 Início do template:")
    print("=" * 30)
    for i, line in enumerate(lines[:15], 1):
        print(f"{i:2d}: {line}")
    print("...")
    
    # Salvar template (opcional)
    template_file = "/tmp/dino_template_exemplo.py"
    with open(template_file, 'w', encoding='utf-8') as f:
        f.write(template_code)
    
    print(f"\n💾 Template salvo em: {template_file}")
    
    return template_code


def exemplo_gerenciamento_jobs():
    """
    Exemplo 5: Gerenciamento de jobs existentes
    Como listar, monitorar e gerenciar jobs DINO
    """
    
    print("\n📊 Exemplo 5: Gerenciamento de Jobs DINO")
    print("=" * 45)
    
    manager = DinoWorkflowManager()
    
    # Listar jobs DINO
    dino_jobs = manager.list_dino_jobs()
    
    print(f"🦕 Jobs DINO encontrados: {len(dino_jobs)}")
    
    if dino_jobs:
        print("\n📋 Lista de Jobs DINO:")
        for job in dino_jobs[:5]:  # Mostrar até 5 jobs
            print(f"   • {job['job_name']} (ID: {job['job_id']})")
            print(f"     Criador: {job['creator']}")
            
            # Verificar status do job
            status = manager.get_job_status(job['job_id'])
            if status['success']:
                print(f"     Status: {status.get('status', 'Unknown')}")
                print(f"     Última execução: {status.get('last_run_state', 'Never run')}")
            else:
                print(f"     Status: Erro ao obter - {status['error']}")
            print()
    else:
        print("ℹ️ Nenhum job DINO encontrado no workspace")
    
    return dino_jobs


def main():
    """
    Função principal - executa todos os exemplos
    """
    
    print("🦕 DINO SDK v1.2.0 - Exemplos WorkflowManager")
    print("=" * 55)
    print("Demonstração completa de criação de workflows Databricks\n")
    
    try:
        # Verificar conexão
        w = WorkspaceClient()
        print(f"✅ Conectado ao workspace: {w.config.host}\n")
        
        # Executar exemplos
        resultado1 = exemplo_workflow_manual()
        resultado2 = exemplo_workflow_automatizado() 
        resultado3, manager, config = exemplo_workflow_avancado()
        template = exemplo_template_notebook()
        jobs_existentes = exemplo_gerenciamento_jobs()
        
        # Resumo final
        print("\n🎉 RESUMO DOS EXEMPLOS")
        print("=" * 25)
        
        resultados = [resultado1, resultado2, resultado3]
        sucessos = sum(1 for r in resultados if r.get('success', False))
        
        print(f"✅ Workflows criados com sucesso: {sucessos}/{len(resultados)}")
        print(f"📝 Template de notebook gerado: ✅")
        print(f"📊 Jobs existentes listados: {len(jobs_existentes)}")
        
        print(f"\n🚀 FUNCIONALIDADES DEMONSTRADAS:")
        features = [
            "Jobs manuais com schedule CRON",
            "Jobs automatizados com file arrival trigger",
            "Configurações avançadas de cluster",
            "Liquid Clustering e AutoLoader",
            "Templates de notebook automáticos", 
            "Notificações por email",
            "Gerenciamento de jobs existentes"
        ]
        
        for feature in features:
            print(f"   ✅ {feature}")
        
        print(f"\n🦕 DINO SDK WorkflowManager - Todos os exemplos concluídos!")
        
    except Exception as e:
        logger.error(f"❌ Erro na execução: {e}")
        return False
    
    return True


if __name__ == "__main__":
    """
    Execução dos exemplos
    """
    
    print("🦕 DINO SDK v1.2.0 - WorkflowManager Examples")
    print("Este script demonstra o uso do WorkflowManager")
    print("\nPara executar em Databricks:")
    print("1. Importe este módulo")
    print("2. Execute main() ou funções individuais")
    print("3. Ajuste configurações conforme seu ambiente")
    
    # Exemplo de uso
    usage_example = '''
    # Exemplo de uso em notebook Databricks:
    
    from examples.workflow_manager_exemplo import (
        exemplo_workflow_manual,
        exemplo_workflow_automatizado,
        exemplo_workflow_avancado,
        main
    )
    
    # Executar exemplo específico
    resultado = exemplo_workflow_manual()
    
    # Ou executar todos os exemplos
    main()
    '''
    
    print(usage_example)
    
    # Se executado diretamente, mostrar apenas informações
    success = main() if __name__ == "__main__" else True
    
    if success:
        print("\n✨ Exemplos carregados com sucesso!")
    else:
        print("\n⚠️ Alguns exemplos podem precisar de ajustes para seu ambiente")


"""
🦕 DINO SDK v1.2.0 - WorkflowManager Examples

FUNCIONALIDADES DEMONSTRADAS:
✅ Criação de jobs manuais com schedule CRON
✅ Jobs automatizados com file arrival triggers
✅ Configurações avançadas de cluster
✅ Job clusters com custom tags
✅ Templates de notebook gerados automaticamente
✅ Notificações por email configuráveis
✅ Gerenciamento de jobs existentes
✅ Liquid Clustering e AutoLoader integrados

CASOS DE USO COBERTOS:
• ETLs programados (vendas diárias)
• Ingestão em tempo real (logs de aplicação)
• Pipelines analytics avançados (customer 360)
• Monitoramento e observabilidade
• Templates reutilizáveis

WorkflowManager - Automatize sua ingestão no Databricks! 🚀
"""
