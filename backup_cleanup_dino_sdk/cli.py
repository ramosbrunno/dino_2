#!/usr/bin/env python3
"""
Dino SDK - Interface de Linha de Comando
Ferramenta para ingestão batch de dados no Databricks
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
from ingestion_engine import IngestionEngine
from workflow_manager import WorkflowManager
from genie_assistant import GenieAssistant


def setup_logging(debug: bool = False):
    """Configura logging baseado no nível de debug"""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


@click.command()
@click.option('--target-schema', required=True, 
              help='Schema destino da ingestão')
@click.option('--table-name', required=True, 
              help='Nome lógico da entidade a ser processada')
@click.option('--file-path', required=True, 
              help='Caminho completo do arquivo a ser ingerido no storage RAW')
@click.option('--delimiter', default=',', 
              help='Delimitador utilizado no arquivo de origem (padrão: ",")')
@click.option('--is-automated', is_flag=True, 
              help='Se true, realiza ingestão assim que o arquivo é colocado no diretório (file arrival)')
@click.option('--has-genie', is_flag=True, 
              help='Se true, cria sala Genie e catalogação Unity Catalog Assistant')
@click.option('--catalog-name', 
              help='Nome do catálogo Unity Catalog (usa padrão se não informado)')
@click.option('--output-mode', type=click.Choice(['append', 'overwrite', 'merge']), 
              default='append', help='Modo de escrita (padrão: append)')
@click.option('--file-format', type=click.Choice(['csv', 'json', 'parquet', 'delta', 'avro']), 
              help='Formato do arquivo (detectado automaticamente se não informado)')
@click.option('--debug', is_flag=True, 
              help='Ativar modo debug com logs detalhados')
def main(target_schema, table_name, file_path, delimiter, is_automated, 
         has_genie, catalog_name, output_mode, file_format, debug):
    """
    Dino SDK - Ferramenta de ingestão para Databricks
    
    Realiza ingestão de dados com suporte a:
    - Ingestão batch e streaming com file arrival
    - Múltiplos formatos (CSV, JSON, Parquet, Delta, Avro)
    - Integração com Genie Assistant
    - Metadados de auditoria automáticos
    
    PRÉ-REQUISITOS:
    - Schema de destino deve existir
    - Permissões adequadas no Unity Catalog
    """
    
    # Configurar logging
    setup_logging(debug)
    
    # Configurar variáveis de ambiente para debug
    if debug:
        os.environ['DINO_DEBUG'] = 'true'
    
    print("🦕 Dino SDK - Data Ingestion v1.0.0")
    print("=" * 50)
    
    try:
        # Validar entrada
        _validate_inputs(target_schema, table_name, file_path)
        
        # Criar engine de ingestão
        print(f"⚙️ Configurando ingestão...")
        print(f"   📊 Schema: {target_schema}")
        print(f"   📋 Tabela: {table_name}")
        print(f"   📁 Origem: {file_path}")
        print(f"   💾 Modo: {output_mode}")
        print(f"   🔄 Automatizada: {'Sim' if is_automated else 'Não'}")
        
        engine = IngestionEngine(
            target_schema=target_schema,
            table_name=table_name,
            file_path=file_path,
            delimiter=delimiter,
            catalog_name=catalog_name,
            output_mode=output_mode,
            file_format=file_format
        )
        
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
