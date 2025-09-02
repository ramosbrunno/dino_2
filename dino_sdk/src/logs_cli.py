#!/usr/bin/env python3
"""
Dino SDK - Log CLI
Interface de linha de comando para gerenciamento de logs do Azure SQL
"""

import click
import json
from datetime import datetime
from typing import Optional

from .azure_sql_logger import get_sql_logger


@click.group(name='dino-logs')
def logs_cli():
    """Comandos para gerenciamento de logs do Dino SDK"""
    pass


@logs_cli.command('history')
@click.option('--limit', '-l', default=20, help='Número de registros a exibir')
@click.option('--status', '-s', type=click.Choice(['iniciado', 'concluido', 'erro']), help='Filtrar por status')
@click.option('--table', '-t', help='Filtrar por nome da tabela')
@click.option('--json', 'output_json', is_flag=True, help='Saída em formato JSON')
def show_history(limit: int, status: Optional[str], table: Optional[str], output_json: bool):
    """Exibe histórico de execuções"""
    
    try:
        logger = get_sql_logger()
        executions = logger.get_execution_history(
            limit=limit,
            status_filter=status,
            table_filter=table
        )
        
        if not executions:
            click.echo("📭 Nenhuma execução encontrada")
            return
        
        if output_json:
            # Converter datetime para string para JSON
            for execution in executions:
                for key, value in execution.items():
                    if isinstance(value, datetime):
                        execution[key] = value.isoformat()
            
            click.echo(json.dumps(executions, indent=2, ensure_ascii=False))
            return
        
        # Exibição formatada
        click.echo(f"\n📊 Histórico de Execuções (últimas {len(executions)})")
        click.echo("=" * 80)
        
        for execution in executions:
            status_icon = {
                'iniciado': '🔄',
                'concluido': '✅',
                'erro': '❌'
            }.get(execution['status'], '❓')
            
            click.echo(f"\n{status_icon} {execution['execution_id'][:8]}... | {execution['status'].upper()}")
            click.echo(f"   📊 Tabela: {execution['catalog_name']}.{execution['schema_name']}.{execution['table_name']}")
            click.echo(f"   📁 Origem: {execution['source_path']}")
            click.echo(f"   📄 Formato: {execution['file_format']} | Modo: {execution['ingestion_mode']}")
            
            if execution['records_read'] or execution['records_written']:
                click.echo(f"   📈 Registros: {execution['records_read']:,} → {execution['records_written']:,}")
            
            if execution['execution_time_seconds']:
                click.echo(f"   ⏱️ Tempo: {execution['execution_time_seconds']:.2f}s")
            
            click.echo(f"   🕒 Criado: {execution['created_at']}")
            
            if execution['error_message']:
                click.echo(f"   💥 Erro: {execution['error_message']}")
    
    except Exception as e:
        click.echo(f"❌ Erro ao obter histórico: {e}", err=True)


@logs_cli.command('stats')
@click.option('--days', '-d', default=30, help='Período em dias para análise')
@click.option('--json', 'output_json', is_flag=True, help='Saída em formato JSON')
def show_stats(days: int, output_json: bool):
    """Exibe estatísticas de execução"""
    
    try:
        logger = get_sql_logger()
        stats = logger.get_execution_stats(days=days)
        
        if not stats:
            click.echo("📭 Nenhuma estatística encontrada")
            return
        
        if output_json:
            # Converter datetime para string para JSON
            if 'last_execution' in stats and stats['last_execution']:
                stats['last_execution'] = stats['last_execution'].isoformat()
            
            click.echo(json.dumps(stats, indent=2, ensure_ascii=False))
            return
        
        # Exibição formatada
        click.echo(f"\n📈 Estatísticas dos Últimos {days} Dias")
        click.echo("=" * 50)
        
        total = stats.get('total_executions', 0)
        successful = stats.get('successful_executions', 0)
        failed = stats.get('failed_executions', 0)
        running = stats.get('running_executions', 0)
        
        success_rate = (successful / total * 100) if total > 0 else 0
        
        click.echo(f"\n🎯 Execuções Totais: {total:,}")
        click.echo(f"✅ Sucessos: {successful:,}")
        click.echo(f"❌ Falhas: {failed:,}")
        click.echo(f"🔄 Em Execução: {running:,}")
        click.echo(f"📊 Taxa de Sucesso: {success_rate:.1f}%")
        
        if stats.get('avg_execution_time'):
            click.echo(f"⏱️ Tempo Médio: {stats['avg_execution_time']:.2f}s")
        
        if stats.get('total_records_read'):
            click.echo(f"📥 Registros Lidos: {stats['total_records_read']:,}")
        
        if stats.get('total_records_written'):
            click.echo(f"📤 Registros Escritos: {stats['total_records_written']:,}")
        
        if stats.get('last_execution'):
            click.echo(f"🕒 Última Execução: {stats['last_execution']}")
    
    except Exception as e:
        click.echo(f"❌ Erro ao obter estatísticas: {e}", err=True)


@logs_cli.command('cleanup')
@click.option('--days', '-d', default=90, help='Dias de logs para manter')
@click.confirmation_option(prompt='Tem certeza que deseja remover logs antigos?')
def cleanup_logs(days: int):
    """Remove logs antigos"""
    
    try:
        logger = get_sql_logger()
        logger.cleanup_old_logs(days_to_keep=days)
        click.echo(f"✅ Limpeza de logs concluída (mantidos últimos {days} dias)")
    
    except Exception as e:
        click.echo(f"❌ Erro na limpeza de logs: {e}", err=True)


@logs_cli.command('test-connection')
def test_connection():
    """Testa conexão com Azure SQL Database"""
    
    try:
        logger = get_sql_logger()
        
        # Testar conexão básica
        with logger._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT GETDATE() as current_time")
            result = cursor.fetchone()
            
        click.echo("✅ Conexão com Azure SQL Database bem-sucedida")
        click.echo(f"🕒 Hora do servidor: {result[0]}")
        
        # Verificar se tabela existe
        with logger._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) as log_count 
                FROM dino_execution_logs 
                WHERE created_at >= DATEADD(day, -7, GETDATE())
            """)
            count = cursor.fetchone()[0]
            
        click.echo(f"📊 Logs dos últimos 7 dias: {count:,} registros")
    
    except Exception as e:
        click.echo(f"❌ Erro na conexão: {e}", err=True)
        click.echo("\n💡 Verifique as configurações:")
        click.echo("   - DINO_AZURE_SQL_CONNECTION_STRING")
        click.echo("   - DINO_AZURE_SQL_SERVER")
        click.echo("   - DINO_AZURE_SQL_DATABASE")
        click.echo("   - DINO_AZURE_SQL_USERNAME")
        click.echo("   - DINO_AZURE_SQL_PASSWORD")


if __name__ == '__main__':
    logs_cli()
