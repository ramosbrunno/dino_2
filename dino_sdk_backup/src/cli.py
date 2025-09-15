#!/usr/bin/env python3
"""
Dino SDK - Interface de Linha de Comando
Ferramenta para ingestão híbrida (batch/streaming) de dados no Databricks
"""

import click
import os
import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
import json
import time
from datetime import datetime

# Imports locais
from .ingestion_engine import IngestionEngine
from .workflow_manager import WorkflowManager
from .genie_assistant import GenieAssistant
from .job_manager import JobManager
from .config_manager import get_config_manager
from .logs_cli import logs_cli


def setup_logging(debug: bool = False):
    """Configura logging baseado no nível de debug"""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


@click.command()
@click.option('--target-schema', 
              help='Schema destino da ingestão (deve existir)')
@click.option('--table-name', 
              help='Nome da tabela destino')
@click.option('--file-path', 
              help='Caminho do arquivo/diretório no Volume Databricks')
@click.option('--delimiter', default=',', 
              help='Delimitador do arquivo (padrão: ",")')
@click.option('--is-automated', is_flag=True, 
              help='Usar Auto Loader com File Arrival Trigger')
@click.option('--has-genie', is_flag=True, 
              help='Criar sala Genie com a tabela')
@click.option('--catalog-name', 
              help='Nome do catálogo Unity Catalog (usa configuração padrão se não informado)')
@click.option('--output-mode', type=click.Choice(['append', 'overwrite', 'merge']), 
              default='append', help='Modo de escrita (padrão: append)')
@click.option('--file-format', type=click.Choice(['csv', 'json', 'parquet', 'delta', 'avro']), 
              help='Formato do arquivo (detectado automaticamente se não informado)')
@click.option('--create-job', is_flag=True,
              help='Criar job do Databricks para execução automatizada')
@click.option('--job-name',
              help='Nome do job (usado com --create-job)')
@click.option('--debug', is_flag=True, 
              help='Ativar modo debug com logs detalhados')
@click.option('--config-only', is_flag=True,
              help='Apenas mostrar configuração sem executar')
@click.option('--example', is_flag=True,
              help='Mostrar exemplos de uso')
def main(target_schema, table_name, file_path, delimiter, is_automated, 
         has_genie, catalog_name, output_mode, file_format, create_job, 
         job_name, debug, config_only, example):
    """
    Dino SDK - Ferramenta de ingestão híbrida para Databricks
    
    Realiza ingestão de dados com suporte a:
    - Ingestão batch e streaming com Auto Loader
    - File Arrival Trigger para execução automática
    - Múltiplos formatos (CSV, JSON, Parquet, Delta, Avro)
    - Integração com Genie Assistant
    - Jobs automatizados do Databricks
    - Metadados de auditoria automáticos
    
    PRÉ-REQUISITOS:
    - Schema de destino deve existir
    - Permissões adequadas no Unity Catalog
    - Volumes configurados corretamente
    - Variáveis de ambiente configuradas no cluster
    
    EXEMPLOS:
    
    # Ingestão batch simples
    dino-ingest --target-schema vendas_db --table-name clientes --file-path /Volumes/main/landing/clientes.csv
    
    # Ingestão streaming com Auto Loader
    dino-ingest --target-schema vendas_db --table-name pedidos --file-path /Volumes/main/landing/pedidos/ --is-automated
    
    # Criar job automatizado com Genie
    dino-ingest --target-schema vendas_db --table-name produtos --file-path /Volumes/main/landing/produtos/ --is-automated --has-genie --create-job --job-name "Ingestao_Produtos"
    """
    
    # Configurar logging
    setup_logging(debug)
    
    # Configurar variáveis de ambiente para debug
    if debug:
        os.environ['DINO_DEBUG'] = 'true'
    
    print("🦕 Dino SDK - Data Ingestion v2.0.0")
    print("=" * 50)
    
    try:
        # Se --example foi passado, mostrar exemplos e sair
        if example:
            show_examples()
            return
        
        # Validar argumentos obrigatórios se não for --example ou --config-only
        if not config_only:
            if not target_schema:
                print("❌ Erro: --target-schema é obrigatório")
                return
            if not table_name:
                print("❌ Erro: --table-name é obrigatório")
                return
            if not file_path:
                print("❌ Erro: --file-path é obrigatório")
                return
        
        # Carregar configurações
        config = get_config_manager()
        
        if config_only:
            print("⚙️ Configuração atual:")
            import pprint
            pprint.pprint(config.show_config())
            return
        
        # Validar configurações do Databricks
        if not config.validate_databricks_config():
            print("❌ Configurações do Databricks não encontradas!")
            print("💡 Configure as variáveis de ambiente necessárias no cluster:")
            print("   - DATABRICKS_WORKSPACE_URL")
            print("   - DINO_CATALOG_NAME (opcional)")
            print("   - DINO_CHECKPOINT_BASE_PATH (opcional)")
            return
        
        # Validar entrada
        _validate_inputs(target_schema, table_name, file_path)
        
        # Criar engine de ingestão
        print(f"⚙️ Configurando ingestão...")
        print(f"   📊 Schema: {target_schema}")
        print(f"   📋 Tabela: {table_name}")
        print(f"   📁 Origem: {file_path}")
        print(f"   💾 Modo: {output_mode}")
        print(f"   � Formato: {file_format or 'auto-detectado'}")
        print(f"   🔄 Streaming: {'Sim' if is_automated else 'Não'}")
        print(f"   🧞 Genie: {'Sim' if has_genie else 'Não'}")
        
        engine = IngestionEngine(
            target_schema=target_schema,
            table_name=table_name,
            file_path=file_path,
            delimiter=delimiter,
            is_automated=is_automated,
            catalog_name=catalog_name,
            output_mode=output_mode,
            file_format=file_format
        )
        
        # Criar job se solicitado
        if create_job:
            print(f"🏗️ Criando job do Databricks...")
            job_manager = JobManager()
            
            if not job_name:
                job_name = f"DinoSDK_{target_schema}_{table_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            job_file = job_manager.create_job_definition_file(
                job_name=job_name,
                target_schema=target_schema,
                table_name=table_name,
                file_path=file_path,
                delimiter=delimiter,
                is_automated=is_automated,
                file_format=file_format or engine.file_format,
                has_genie=has_genie
            )
            
            print(f"✅ Definição do job criada: {job_file}")
            print(f"💡 Para criar o job no Databricks, use:")
            print(f"   databricks jobs create --json-file {job_file}")
            
            # Se não for automatizado, ainda executar a ingestão
            if not is_automated:
                print(f"📊 Executando ingestão inicial...")
            else:
                print(f"ℹ️ Job configurado para execução automática com File Arrival Trigger")
                return
        
        # Executar ingestão
        if is_automated and not create_job:
            print(f"🔄 Executando ingestão streaming com Auto Loader...")
            result = engine.run_streaming_ingestion()
        else:
            print(f"📊 Executando ingestão batch...")
            result = engine.run_batch_ingestion()
        
        # Configurar Genie se solicitado
        if has_genie:
            print(f"🧞 Configurando Genie Assistant...")
            genie = GenieAssistant()
            genie_result = genie.setup_genie_room(
                schema_name=target_schema,
                table_name=table_name,
                description=f"Tabela ingerida via Dino SDK - {table_name}"
            )
            print(f"✅ Genie configurado: {genie_result}")
        
        print(f"🎉 Ingestão concluída com sucesso!")
        print(f"📊 Tabela: {engine.get_table_full_name()}")
        
        if result and 'execution_time' in result:
            print(f"⏱️ Tempo de execução: {result['execution_time']:.2f}s")
        
    except Exception as e:
        print(f"❌ Erro durante a execução: {e}")
        if debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)
        
        # Executar ingestão
        print(f"\n🚀 Executando ingestão...")
        result = engine.execute_ingestion(is_automated=is_automated)
        
        if not result['success']:
            print(f"❌ Erro na ingestão: {result['error']}")
            sys.exit(1)
        
        print(f"✅ Ingestão configurada com sucesso!")
        print(f"   📊 Tabela: {result['table_full_name']}")
        print(f"   📋 Formato: {result['detected_format']}")
        
        if is_automated:
            print(f"   � Checkpoint: {result.get('checkpoint_location', 'N/A')}")
            print(f"   �📝 Arquivo streaming: {result['ingestion_file']}")
        else:
            print(f"   📝 Arquivo batch: {result['ingestion_file']}")
        
        # Criar workflow se necessário
        if is_automated:
            print(f"\n🔄 Criando workflow automatizado...")
            
            workflow_manager = WorkflowManager(target_schema, table_name)
            
            workflow_result = workflow_manager.create_auto_ingestion_workflow(
                source_path=file_path,
                target_table=result['table_full_name'],
                checkpoint_location=result.get('checkpoint_location', ''),
                file_format=result['detected_format'],
                delimiter=delimiter
            )
            
            if workflow_result['success']:
                print(f"✅ Workflow criado: {workflow_result['workflow_name']}")
                print(f"   📝 Arquivo: {workflow_result.get('workflow_file', 'N/A')}")
            else:
                print(f"⚠️ Erro no workflow: {workflow_result['error']}")
        
        # Configurar Genie se solicitado
        if has_genie:
            print(f"\n🧞 Configurando Genie Assistant...")
            
            genie = GenieAssistant(
                catalog_name=result['catalog_name'],
                schema_name=target_schema,
                table_name=table_name
            )
            
            genie_result = genie.setup_genie_room_and_cataloging()
            
            if genie_result['success']:
                print(f"✅ Genie configurado!")
                print(f"   🏠 Sala: {genie_result['room_name']}")
                print(f"   📚 Status: {genie_result['catalog_status']}")
                if genie_result.get('room_url'):
                    print(f"   🔗 URL: {genie_result['room_url']}")
            else:
                print(f"⚠️ Erro no Genie: {genie_result['error']}")
        
        # Resumo final
        print(f"\n🎉 Processo concluído!")
        print(f"📋 Próximos passos:")
        print(f"   1. Execute o arquivo {result['ingestion_file']} em um notebook Databricks")
        
        if is_automated:
            print(f"   2. Importe o workflow JSON no Databricks Jobs para automação")
        
        if has_genie:
            print(f"   3. Acesse a sala Genie para consultas em linguagem natural")
        
        print(f"   4. Monitore a tabela {result['table_full_name']} no Unity Catalog")
        
    except KeyboardInterrupt:
        print(f"\n⚠️ Operação cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {str(e)}")
        if debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def _validate_inputs(target_schema: str, table_name: str, file_path: str):
    """Valida entradas do usuário"""
    
    # Validar nomes de schema e tabela
    if not target_schema.replace('_', '').isalnum():
        raise ValueError("target_schema deve conter apenas letras, números e underscore")
    
    if not table_name.replace('_', '').isalnum():
        raise ValueError("table_name deve conter apenas letras, números e underscore")
    
    # Validar path
    if not file_path or file_path.isspace():
        raise ValueError("file_path não pode estar vazio")


def _validate_cron_expression(cron_expr: str):
    """Valida expressão cron básica"""
    parts = cron_expr.split()
    if len(parts) != 5:
        raise ValueError("Expressão cron deve ter 5 campos: 'minuto hora dia mês dia_semana'")
    
    # Validação básica dos campos
    try:
        for i, part in enumerate(parts):
            if part != '*' and not part.isdigit() and '/' not in part and ',' not in part and '-' not in part:
                raise ValueError(f"Campo {i+1} da expressão cron inválido: {part}")
    except:
        raise ValueError("Expressão cron inválida. Use formato: 'minuto hora dia mês dia_semana'")


def show_examples():
    """Mostra exemplos de uso do CLI"""
    examples = [
        {
            "title": "Ingestão simples de CSV",
            "command": "dino-ingest --target-schema bronze --table-name customers --file-path /Volumes/main/raw/customers.csv"
        },
        {
            "title": "Ingestão com workflow",
            "command": "dino-ingest --target-schema bronze --table-name orders --file-path /Volumes/main/raw/orders.json --create-workflow"
        },
        {
            "title": "Ingestão agendada com Genie",
            "command": "dino-ingest --target-schema bronze --table-name sales --file-path /Volumes/main/raw/sales.csv --schedule-cron '0 6 * * *' --has-genie"
        },
        {
            "title": "Ingestão com particionamento",
            "command": "dino-ingest --target-schema bronze --table-name events --file-path /Volumes/main/raw/events.parquet --partition-columns 'year,month'"
        },
        {
            "title": "Ingestão com overwrite",
            "command": "dino-ingest --target-schema bronze --table-name products --file-path /Volumes/main/raw/products.csv --output-mode overwrite"
        }
    ]
    
    print("📚 Exemplos de uso do Dino SDK:")
    print("=" * 50)
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['title']}:")
        print(f"   {example['command']}")
    
    print(f"\n💡 Use --help para ver todas as opções disponíveis")


if __name__ == '__main__':
    main()
