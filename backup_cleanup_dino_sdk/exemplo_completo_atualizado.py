#!/usr/bin/env python3
"""
Dino SDK - Exemplo Completo de Uso
Demonstra todas as funcionalidades do SDK
"""

import os
import time
from datetime import datetime

# Simular ambiente Databricks (para teste local)
os.environ['DINO_CATALOG_NAME'] = 'main'
os.environ['DATABRICKS_WORKSPACE_URL'] = 'https://your-workspace.cloud.databricks.com'
os.environ['DINO_CHECKPOINT_BASE_PATH'] = '/tmp/checkpoints/dino_sdk'
os.environ['DINO_VOLUME_BASE_PATH'] = '/Volumes'

# Importar componentes do Dino SDK
from src.ingestion_engine import IngestionEngine
from src.genie_assistant import GenieAssistant
from src.job_manager import JobManager
from src.config_manager import get_config_manager


def exemplo_configuracao():
    """Exemplo 1: Configuração inicial"""
    print("🦕 Exemplo 1: Configuração do Dino SDK")
    print("=" * 50)
    
    # Obter gerenciador de configuração
    config = get_config_manager()
    
    # Mostrar configuração atual
    print("📋 Configuração atual:")
    current_config = config.show_config()
    for key, value in current_config.items():
        print(f"   {key}: {value}")
    
    # Validar configuração
    is_valid = config.validate_databricks_config()
    status = "✅ Válida" if is_valid else "❌ Inválida"
    print(f"\n🔍 Status da configuração: {status}")
    
    print("\n" + "=" * 50 + "\n")


def exemplo_ingestao_batch():
    """Exemplo 2: Ingestão batch simples"""
    print("🦕 Exemplo 2: Ingestão Batch")
    print("=" * 50)
    
    # Configurar engine de ingestão
    engine = IngestionEngine(
        target_schema="vendas_db",
        table_name="clientes",
        file_path="/Volumes/main/landing/clientes.csv",
        delimiter=",",
        is_automated=False,  # Modo batch
        file_format="csv"
    )
    
    print(f"📊 Tabela destino: {engine.get_table_full_name()}")
    print(f"📁 Arquivo origem: {engine.file_path}")
    print(f"💾 Modo: {engine.output_mode}")
    print(f"📄 Formato: {engine.file_format}")
    
    # Gerar código de ingestão
    print("\n📝 Código gerado:")
    batch_code = engine._generate_batch_code()
    print(batch_code[:500] + "..." if len(batch_code) > 500 else batch_code)
    
    print("\n" + "=" * 50 + "\n")


def exemplo_ingestao_streaming():
    """Exemplo 3: Ingestão streaming com Auto Loader"""
    print("🦕 Exemplo 3: Ingestão Streaming")
    print("=" * 50)
    
    # Configurar engine para streaming
    engine = IngestionEngine(
        target_schema="vendas_db",
        table_name="pedidos",
        file_path="/Volumes/main/landing/pedidos/",
        delimiter=",",
        is_automated=True,  # Modo streaming
        file_format="csv"
    )
    
    print(f"📊 Tabela destino: {engine.get_table_full_name()}")
    print(f"📁 Diretório origem: {engine.file_path}")
    print(f"🔄 Checkpoint: {engine.checkpoint_location}")
    print(f"📋 Schema location: {engine.schema_location}")
    
    # Gerar código de streaming
    print("\n📝 Código Auto Loader gerado:")
    streaming_code = engine._generate_streaming_code()
    print(streaming_code[:500] + "..." if len(streaming_code) > 500 else streaming_code)
    
    print("\n" + "=" * 50 + "\n")


def exemplo_genie_assistant():
    """Exemplo 4: Configuração do Genie"""
    print("🦕 Exemplo 4: Genie Assistant")
    print("=" * 50)
    
    # Inicializar Genie Assistant
    genie = GenieAssistant()
    
    # Configurar sala Genie
    result = genie.setup_genie_room(
        schema_name="vendas_db",
        table_name="pedidos",
        description="Tabela de pedidos do e-commerce com análise em tempo real"
    )
    
    print(f"🧞 Sala criada: {result['display_name']}")
    print(f"🆔 Room ID: {result['room_id']}")
    print(f"🔗 URL: {result['url']}")
    print(f"🏷️ Tags: {', '.join(result['tags'])}")
    
    # Gerar consultas de exemplo
    print("\n📊 Consultas de exemplo:")
    queries = genie.generate_sample_queries("vendas_db", "pedidos")
    for i, query in enumerate(queries[:3], 1):
        print(f"\n{i}. {query}")
    
    print("\n" + "=" * 50 + "\n")


def exemplo_job_manager():
    """Exemplo 5: Criação de Job"""
    print("🦕 Exemplo 5: Job Manager")
    print("=" * 50)
    
    # Inicializar Job Manager
    job_manager = JobManager()
    
    # Criar configuração de job
    job_config = job_manager.create_ingestion_job(
        job_name="Ingestao_Produtos_Automatizada",
        target_schema="vendas_db",
        table_name="produtos",
        file_path="/Volumes/main/landing/produtos/",
        delimiter=",",
        is_automated=True,  # File arrival trigger
        file_format="csv",
        has_genie=True
    )
    
    print(f"🏗️ Job criado: {job_config['name']}")
    print(f"📋 Descrição: {job_config['description']}")
    print(f"🔄 Trigger: {job_config.get('trigger', 'Manual')}")
    print(f"🧞 Inclui Genie: {len(job_config['tasks']) > 1}")
    
    # Salvar configuração do job
    job_file = job_manager.create_job_definition_file(
        job_name="Ingestao_Produtos_Demo",
        target_schema="vendas_db",
        table_name="produtos",
        file_path="/Volumes/main/landing/produtos/",
        delimiter=",",
        is_automated=True,
        has_genie=True
    )
    
    print(f"\n📄 Arquivo de configuração salvo: {job_file}")
    
    print("\n" + "=" * 50 + "\n")


def exemplo_casos_uso():
    """Exemplo 6: Casos de uso práticos"""
    print("🦕 Exemplo 6: Casos de Uso Práticos")
    print("=" * 50)
    
    casos = [
        {
            "nome": "E-commerce - Pedidos",
            "schema": "ecommerce",
            "tabela": "pedidos",
            "path": "/Volumes/main/ecommerce/pedidos/",
            "formato": "csv",
            "streaming": True,
            "genie": True
        },
        {
            "nome": "Logs de Aplicação",
            "schema": "logs",
            "tabela": "aplicacao",
            "path": "/Volumes/main/logs/app/",
            "formato": "json",
            "streaming": True,
            "genie": False
        },
        {
            "nome": "Dados Financeiros",
            "schema": "financeiro",
            "tabela": "transacoes",
            "path": "/Volumes/main/financeiro/transacoes.parquet",
            "formato": "parquet",
            "streaming": False,
            "genie": True
        }
    ]
    
    for caso in casos:
        print(f"\n📋 Caso: {caso['nome']}")
        print(f"   📊 Destino: {caso['schema']}.{caso['tabela']}")
        print(f"   📁 Origem: {caso['path']}")
        print(f"   📄 Formato: {caso['formato']}")
        print(f"   🔄 Streaming: {'Sim' if caso['streaming'] else 'Não'}")
        print(f"   🧞 Genie: {'Sim' if caso['genie'] else 'Não'}")
        
        # Comando CLI equivalente
        cmd_parts = [
            "dino-ingest",
            f"--target-schema {caso['schema']}",
            f"--table-name {caso['tabela']}",
            f"--file-path {caso['path']}",
            f"--file-format {caso['formato']}"
        ]
        
        if caso['streaming']:
            cmd_parts.append("--is-automated")
        
        if caso['genie']:
            cmd_parts.append("--has-genie")
        
        cmd = " \\\n  ".join(cmd_parts)
        print(f"   💻 Comando CLI:\n   {cmd}")
    
    print("\n" + "=" * 50 + "\n")


def exemplo_monitoramento():
    """Exemplo 7: Monitoramento e auditoria"""
    print("🦕 Exemplo 7: Monitoramento e Auditoria")
    print("=" * 50)
    
    # Consultas de monitoramento
    queries_monitoramento = [
        {
            "nome": "Últimas ingestões",
            "sql": """
SELECT 
  _dino_batch_id,
  _dino_ingestion_timestamp,
  COUNT(*) as records,
  _dino_source_file
FROM main.vendas_db.pedidos
WHERE _dino_ingestion_timestamp >= CURRENT_DATE - INTERVAL 7 DAY
GROUP BY ALL
ORDER BY _dino_ingestion_timestamp DESC
LIMIT 10;
            """
        },
        {
            "nome": "Volume por dia",
            "sql": """
SELECT 
  DATE(_dino_ingestion_timestamp) as data_ingestao,
  COUNT(*) as registros_ingeridos,
  COUNT(DISTINCT _dino_batch_id) as batches,
  COUNT(DISTINCT _dino_source_file) as arquivos
FROM main.vendas_db.pedidos
WHERE _dino_ingestion_timestamp >= CURRENT_DATE - INTERVAL 30 DAY
GROUP BY DATE(_dino_ingestion_timestamp)
ORDER BY data_ingestao DESC;
            """
        },
        {
            "nome": "Status por arquivo",
            "sql": """
SELECT 
  _dino_source_file,
  MIN(_dino_ingestion_timestamp) as primeira_ingestao,
  MAX(_dino_ingestion_timestamp) as ultima_ingestao,
  COUNT(*) as total_registros,
  COUNT(DISTINCT _dino_batch_id) as total_batches
FROM main.vendas_db.pedidos
GROUP BY _dino_source_file
ORDER BY ultima_ingestao DESC;
            """
        }
    ]
    
    for query in queries_monitoramento:
        print(f"\n📊 {query['nome']}:")
        print(query['sql'].strip())
    
    print("\n" + "=" * 50 + "\n")


def main():
    """Função principal - executa todos os exemplos"""
    print("🦕 DINO SDK - EXEMPLOS COMPLETOS")
    print("=" * 60)
    print(f"⏰ Executado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60 + "\n")
    
    try:
        # Executar todos os exemplos
        exemplo_configuracao()
        exemplo_ingestao_batch()
        exemplo_ingestao_streaming()
        exemplo_genie_assistant()
        exemplo_job_manager()
        exemplo_casos_uso()
        exemplo_monitoramento()
        
        print("🎉 Todos os exemplos executados com sucesso!")
        print("\n💡 Próximos passos:")
        print("1. Configure o ambiente: dino-config init")
        print("2. Valide a configuração: dino-config validate")
        print("3. Execute sua primeira ingestão: dino-ingest --help")
        
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
