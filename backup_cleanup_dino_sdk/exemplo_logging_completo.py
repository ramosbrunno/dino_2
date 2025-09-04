#!/usr/bin/env python3
"""
Dino SDK - Exemplo Completo com Logging
Demonstração do sistema de logging do Azure SQL Database
"""

import os
import time
import random
from datetime import datetime

# Configurar ambiente para demonstração
os.environ['DINO_AZURE_SQL_SERVER'] = 'demo-server.database.windows.net'
os.environ['DINO_AZURE_SQL_DATABASE'] = 'dino_logging'
os.environ['DINO_AZURE_SQL_USERNAME'] = 'dino_admin'
os.environ['DINO_AZURE_SQL_PASSWORD'] = 'demo_password'

# Para demonstração sem conexão real
os.environ['DINO_DEMO_MODE'] = 'true'

try:
    from src.ingestion_engine import IngestionEngine
    from src.azure_sql_logger import get_sql_logger
    from src.config_manager import get_config_manager
except ImportError:
    print("❌ Erro: Execute este exemplo do diretório dino_sdk")
    exit(1)


def exemplo_logging_simples():
    """Exemplo básico de uso do sistema de logging"""
    
    print("🦕 Dino SDK - Exemplo de Logging")
    print("=" * 50)
    
    # Obter logger
    logger = get_sql_logger()
    
    print("📊 1. Teste de Conexão")
    print("-" * 30)
    
    try:
        # Em modo demo, simula conexão
        if os.getenv('DINO_DEMO_MODE') == 'true':
            print("✅ Conexão simulada com Azure SQL (modo demo)")
            print("🕒 Hora do servidor: 2025-09-01 10:30:00")
            print("📊 Logs dos últimos 7 dias: 42 registros")
        else:
            # Teste real de conexão
            with logger._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT GETDATE() as current_time")
                result = cursor.fetchone()
                print(f"✅ Conexão bem-sucedida")
                print(f"🕒 Hora do servidor: {result[0]}")
    except Exception as e:
        print(f"⚠️ Usando modo simulado: {e}")
    
    print("\n📝 2. Registro Manual de Execução")
    print("-" * 40)
    
    # Exemplo de logging manual
    execution_id = logger.start_execution(
        job_name="exemplo_manual_logging",
        table_name="clientes",
        schema_name="bronze",
        catalog_name="main",
        source_path="/Volumes/main/raw/clientes.csv",
        ingestion_mode="batch",
        file_format="csv"
    )
    
    print(f"📋 ID da Execução: {execution_id}")
    
    # Simular processamento
    print("⚡ Simulando processamento...")
    for i in range(3):
        time.sleep(0.5)
        records_processed = (i + 1) * 1000
        logger.update_execution_progress(
            execution_id, 
            records_read=records_processed,
            records_written=records_processed
        )
        print(f"   📊 Progresso: {records_processed:,} registros")
    
    # Finalizar com sucesso
    logger.complete_execution(
        execution_id,
        records_read=3000,
        records_written=3000
    )
    
    print("\n📈 3. Exemplo de Erro")
    print("-" * 25)
    
    # Exemplo de logging de erro
    error_execution_id = logger.start_execution(
        job_name="exemplo_erro_logging",
        table_name="produtos",
        schema_name="bronze",
        catalog_name="main",
        source_path="/Volumes/main/raw/produtos.json",
        ingestion_mode="streaming",
        file_format="json"
    )
    
    try:
        # Simular erro
        raise ValueError("Formato de arquivo inválido: campo 'price' deve ser numérico")
    except Exception as e:
        logger.log_execution_error(error_execution_id, e)
        print(f"💥 Erro registrado: {e}")


def exemplo_ingestao_com_logging():
    """Exemplo de ingestão usando o IngestionEngine com logging automático"""
    
    print("\n🚀 4. Ingestão com Logging Automático")
    print("-" * 40)
    
    # Criar engine de ingestão
    engine = IngestionEngine(
        target_schema="vendas_db",
        table_name="pedidos",
        file_path="/Volumes/main/landing/pedidos.csv",
        delimiter=",",
        is_automated=False,
        file_format="csv"
    )
    
    print("📊 Executando ingestão batch...")
    result = engine.run_batch_ingestion()
    
    print(f"✅ Ingestão concluída!")
    print(f"   📋 Execution ID: {result.get('execution_id', 'N/A')}")
    print(f"   📊 Registros: {result.get('records_processed', {})}")
    print(f"   ⏱️ Tempo: {result.get('execution_time', 0):.2f}s")
    
    print("\n🔄 Executando ingestão streaming...")
    
    engine_streaming = IngestionEngine(
        target_schema="vendas_db",
        table_name="pedidos_streaming",
        file_path="/Volumes/main/landing/pedidos/",
        delimiter=",",
        is_automated=True,
        file_format="csv"
    )
    
    result_streaming = engine_streaming.run_streaming_ingestion()
    
    print(f"✅ Streaming configurado!")
    print(f"   📋 Execution ID: {result_streaming.get('execution_id', 'N/A')}")
    print(f"   🔄 Checkpoint: {result_streaming.get('checkpoint_location', 'N/A')}")


def exemplo_simulacao_historico():
    """Simula histórico de execuções para demonstração"""
    
    print("\n📚 5. Simulando Histórico de Execuções")
    print("-" * 42)
    
    logger = get_sql_logger()
    
    # Simular várias execuções
    tabelas = ["clientes", "produtos", "pedidos", "vendedores", "categorias"]
    status_opcoes = ["concluido", "concluido", "concluido", "erro", "concluido"]
    
    for i, (tabela, status) in enumerate(zip(tabelas, status_opcoes)):
        print(f"   📊 Simulando execução {i+1}: {tabela}")
        
        execution_id = logger.start_execution(
            job_name=f"ingestao_{tabela}",
            table_name=tabela,
            schema_name="bronze",
            catalog_name="main",
            source_path=f"/Volumes/main/raw/{tabela}.csv",
            ingestion_mode="batch",
            file_format="csv"
        )
        
        time.sleep(0.1)  # Pequena pausa
        
        if status == "concluido":
            records = random.randint(1000, 10000)
            logger.complete_execution(
                execution_id,
                records_read=records,
                records_written=records
            )
        else:
            error = Exception(f"Erro simulado na tabela {tabela}")
            logger.log_execution_error(execution_id, error)
    
    print("✅ Histórico simulado criado!")


def demonstrar_comandos_cli():
    """Demonstra os comandos CLI de logging"""
    
    print("\n🖥️ 6. Comandos CLI de Logging")
    print("-" * 35)
    
    print("📝 Comandos disponíveis:")
    print("   dino-logs history              # Histórico de execuções")
    print("   dino-logs history --status erro # Filtrar por status")
    print("   dino-logs history --table pedidos # Filtrar por tabela")
    print("   dino-logs stats                # Estatísticas gerais")
    print("   dino-logs stats --days 7       # Estatísticas de 7 dias")
    print("   dino-logs test-connection      # Testar conexão")
    print("   dino-logs cleanup --days 90    # Limpar logs antigos")
    
    print("\n💡 Exemplo de saída dos comandos:")
    print("-" * 40)
    
    # Simular saída do comando history
    print("$ dino-logs history --limit 3")
    print()
    print("📊 Histórico de Execuções (últimas 3)")
    print("=" * 50)
    print()
    print("✅ a1b2c3d4... | CONCLUIDO")
    print("   📊 Tabela: main.bronze.pedidos")
    print("   📁 Origem: /Volumes/main/raw/pedidos.csv")
    print("   📄 Formato: csv | Modo: batch")
    print("   📈 Registros: 5,432 → 5,432")
    print("   ⏱️ Tempo: 12.34s")
    print("   🕒 Criado: 2025-09-01 10:15:30")
    print()
    print("❌ e5f6g7h8... | ERRO")
    print("   📊 Tabela: main.bronze.produtos")
    print("   📁 Origem: /Volumes/main/raw/produtos.json")
    print("   📄 Formato: json | Modo: streaming")
    print("   ⏱️ Tempo: 3.21s")
    print("   🕒 Criado: 2025-09-01 09:45:12")
    print("   💥 Erro: Formato de arquivo inválido")
    
    print()
    print("$ dino-logs stats")
    print()
    print("📈 Estatísticas dos Últimos 30 Dias")
    print("=" * 40)
    print()
    print("🎯 Execuções Totais: 156")
    print("✅ Sucessos: 142")
    print("❌ Falhas: 14")
    print("🔄 Em Execução: 0")
    print("📊 Taxa de Sucesso: 91.0%")
    print("⏱️ Tempo Médio: 8.45s")
    print("📥 Registros Lidos: 2,845,621")
    print("📤 Registros Escritos: 2,842,198")
    print("🕒 Última Execução: 2025-09-01 10:15:30")


def main():
    """Função principal do exemplo"""
    
    print("🦕 Dino SDK - Demonstração Completa do Sistema de Logging")
    print("=" * 65)
    print()
    print("Este exemplo demonstra:")
    print("• 📊 Sistema de logging para Azure SQL Database")
    print("• 🔍 Rastreabilidade completa de execuções")
    print("• 📈 Métricas de performance e volume")
    print("• 💥 Tratamento e registro de erros")
    print("• 🖥️ Comandos CLI para análise")
    print()
    
    try:
        # Executar exemplos
        exemplo_logging_simples()
        exemplo_ingestao_com_logging()
        exemplo_simulacao_historico()
        demonstrar_comandos_cli()
        
        print("\n🎉 Demonstração Concluída!")
        print("=" * 30)
        print()
        print("📋 Próximos Passos:")
        print("1. Configure as variáveis do Azure SQL Database")
        print("2. Execute: dino-logs test-connection")
        print("3. Use os comandos dino-ingest para ingestão real")
        print("4. Monitore com: dino-logs history e dino-logs stats")
        print()
        print("📚 Consulte GUIA_CONFIGURACAO_DISTRIBUICAO.md para detalhes")
        
    except Exception as e:
        print(f"\n❌ Erro durante demonstração: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
