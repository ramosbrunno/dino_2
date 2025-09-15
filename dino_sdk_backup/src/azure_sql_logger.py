#!/usr/bin/env python3
"""
Dino SDK - Azure SQL Logger
Sistema de logging técnico e operacional para Azure SQL Database
"""

import os
import json
import logging
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import uuid

try:
    import pyodbc
except ImportError:
    pyodbc = None

from .config_manager import get_config_manager


@dataclass
class LogEntry:
    """Estrutura de entrada de log"""
    execution_id: str
    job_name: str
    table_name: str
    schema_name: str
    catalog_name: str
    status: str  # 'iniciado', 'concluido', 'erro'
    source_path: str
    target_path: str
    records_read: int = 0
    records_written: int = 0
    execution_time_seconds: float = 0.0
    error_message: Optional[str] = None
    error_stack_trace: Optional[str] = None
    ingestion_mode: str = 'batch'  # 'batch', 'streaming'
    file_format: str = 'csv'
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class AzureSQLLogger:
    """
    Logger para Azure SQL Database
    
    Funcionalidades:
    - Registro de logs técnicos e operacionais
    - Rastreabilidade completa de execuções
    - Auditoria de volumes de dados
    - Controle de erros com stack trace
    - Métricas de performance
    """
    
    def __init__(self, connection_string: Optional[str] = None):
        """
        Inicializa o logger para Azure SQL
        
        Args:
            connection_string: String de conexão do Azure SQL (opcional, usa config se não fornecido)
        """
        self.config = get_config_manager()
        self.logger = logging.getLogger(__name__)
        
        # Configurar conexão
        self.connection_string = connection_string or self._get_connection_string()
        
        # Verificar dependências
        if pyodbc is None:
            if os.getenv('DINO_DEMO_MODE') != 'true':
                raise ImportError("pyodbc é necessário para conexão com Azure SQL. Instale com: pip install pyodbc")
            else:
                print("⚠️ Modo demonstração ativo - logging simulado")
        
        # Cache para execução atual
        self.current_execution_id = None
        self.execution_start_time = None
        
        # Validar conexão e criar tabela se necessário
        if os.getenv('DINO_DEMO_MODE') != 'true':
            self._ensure_log_table_exists()
        else:
            print("📊 Tabela de logs simulada inicializada")
    
    def _get_connection_string(self) -> str:
        """Obtém string de conexão das configurações"""
        
        # Modo demonstração - não precisa de conexão real
        if os.getenv('DINO_DEMO_MODE') == 'true':
            return "demo_connection_string"
        
        # Tentar variáveis de ambiente primeiro
        conn_str = os.getenv('DINO_AZURE_SQL_CONNECTION_STRING')
        if conn_str:
            return conn_str
        
        # Construir a partir de componentes
        server = os.getenv('DINO_AZURE_SQL_SERVER')
        database = os.getenv('DINO_AZURE_SQL_DATABASE')
        username = os.getenv('DINO_AZURE_SQL_USERNAME')
        password = os.getenv('DINO_AZURE_SQL_PASSWORD')
        
        if not all([server, database, username, password]):
            raise ValueError("""
Configuração do Azure SQL não encontrada. Configure uma das opções:

1. String de conexão completa:
   DINO_AZURE_SQL_CONNECTION_STRING="Driver={ODBC Driver 18 for SQL Server};Server=tcp:server.database.windows.net,1433;Database=database;Uid=username;Pwd=password;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"

2. Componentes separados:
   DINO_AZURE_SQL_SERVER=your-server.database.windows.net
   DINO_AZURE_SQL_DATABASE=your-database
   DINO_AZURE_SQL_USERNAME=your-username
   DINO_AZURE_SQL_PASSWORD=your-password
            """)
        
        return f"Driver={{ODBC Driver 18 for SQL Server}};Server=tcp:{server},1433;Database={database};Uid={username};Pwd={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    
    def _get_connection(self):
        """Cria conexão com Azure SQL"""
        try:
            connection = pyodbc.connect(self.connection_string)
            return connection
        except Exception as e:
            self.logger.error(f"Erro ao conectar com Azure SQL: {e}")
            raise
    
    def _ensure_log_table_exists(self):
        """Garante que a tabela de logs existe"""
        
        create_table_sql = """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='dino_execution_logs' AND xtype='U')
        CREATE TABLE dino_execution_logs (
            id BIGINT IDENTITY(1,1) PRIMARY KEY,
            execution_id NVARCHAR(36) NOT NULL,
            job_name NVARCHAR(255) NOT NULL,
            table_name NVARCHAR(255) NOT NULL,
            schema_name NVARCHAR(255) NOT NULL,
            catalog_name NVARCHAR(255) NOT NULL,
            status NVARCHAR(50) NOT NULL,
            source_path NVARCHAR(1000) NOT NULL,
            target_path NVARCHAR(1000) NOT NULL,
            records_read BIGINT DEFAULT 0,
            records_written BIGINT DEFAULT 0,
            execution_time_seconds FLOAT DEFAULT 0.0,
            error_message NVARCHAR(MAX) NULL,
            error_stack_trace NVARCHAR(MAX) NULL,
            ingestion_mode NVARCHAR(50) DEFAULT 'batch',
            file_format NVARCHAR(50) DEFAULT 'csv',
            created_at DATETIME2 DEFAULT GETDATE(),
            updated_at DATETIME2 DEFAULT GETDATE()
        );
        
        -- Criar índices para performance
        IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name='IX_dino_logs_execution_id')
        CREATE INDEX IX_dino_logs_execution_id ON dino_execution_logs(execution_id);
        
        IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name='IX_dino_logs_created_at')
        CREATE INDEX IX_dino_logs_created_at ON dino_execution_logs(created_at DESC);
        
        IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name='IX_dino_logs_status')
        CREATE INDEX IX_dino_logs_status ON dino_execution_logs(status);
        """
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(create_table_sql)
                conn.commit()
                self.logger.info("Tabela de logs verificada/criada com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao criar tabela de logs: {e}")
            # Não propagar erro para não quebrar a execução principal
    
    def start_execution(
        self,
        job_name: str,
        table_name: str,
        schema_name: str,
        catalog_name: str,
        source_path: str,
        ingestion_mode: str = 'batch',
        file_format: str = 'csv'
    ) -> str:
        """
        Inicia uma nova execução e registra no log
        
        Args:
            job_name: Nome do job/processo
            table_name: Nome da tabela destino
            schema_name: Nome do schema
            catalog_name: Nome do catálogo
            source_path: Caminho dos dados de origem
            ingestion_mode: Modo de ingestão (batch/streaming)
            file_format: Formato do arquivo
            
        Returns:
            execution_id: ID único da execução
        """
        
        execution_id = str(uuid.uuid4())
        self.current_execution_id = execution_id
        self.execution_start_time = datetime.now()
        
        target_path = f"{catalog_name}.{schema_name}.{table_name}"
        
        log_entry = LogEntry(
            execution_id=execution_id,
            job_name=job_name,
            table_name=table_name,
            schema_name=schema_name,
            catalog_name=catalog_name,
            status='iniciado',
            source_path=source_path,
            target_path=target_path,
            ingestion_mode=ingestion_mode,
            file_format=file_format
        )
        
        self._insert_log_entry(log_entry)
        
        print(f"🔍 Execução iniciada: {execution_id}")
        print(f"📊 Job: {job_name}")
        print(f"📁 Origem: {source_path}")
        print(f"🎯 Destino: {target_path}")
        
        return execution_id
    
    def update_execution_progress(
        self,
        execution_id: str,
        records_read: int = 0,
        records_written: int = 0,
        additional_info: Optional[Dict[str, Any]] = None
    ):
        """
        Atualiza progresso da execução
        
        Args:
            execution_id: ID da execução
            records_read: Quantidade de registros lidos
            records_written: Quantidade de registros escritos
            additional_info: Informações adicionais
        """
        
        # Modo demonstração
        if os.getenv('DINO_DEMO_MODE') == 'true':
            print(f"📊 [DEMO] Progresso atualizado: {execution_id[:8]}... | Lidos: {records_read:,} | Escritos: {records_written:,}")
            return
        
        try:
            sql = """
            UPDATE dino_execution_logs 
            SET records_read = ?, 
                records_written = ?,
                updated_at = GETDATE()
            WHERE execution_id = ?
            """
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (records_read, records_written, execution_id))
                conn.commit()
                
            self.logger.debug(f"Progresso atualizado - Lidos: {records_read}, Escritos: {records_written}")
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar progresso: {e}")
    
    def complete_execution(
        self,
        execution_id: str,
        records_read: int = 0,
        records_written: int = 0,
        additional_metrics: Optional[Dict[str, Any]] = None
    ):
        """
        Marca execução como concluída com sucesso
        
        Args:
            execution_id: ID da execução
            records_read: Total de registros lidos
            records_written: Total de registros escritos
            additional_metrics: Métricas adicionais
        """
        
        execution_time = 0.0
        if self.execution_start_time:
            execution_time = (datetime.now() - self.execution_start_time).total_seconds()
        
        # Modo demonstração
        if os.getenv('DINO_DEMO_MODE') == 'true':
            print(f"✅ [DEMO] Execução concluída: {execution_id[:8]}... | {records_read:,} → {records_written:,} registros | {execution_time:.2f}s")
            return
        
        try:
            sql = """
            UPDATE dino_execution_logs 
            SET status = 'concluido',
                records_read = ?,
                records_written = ?,
                execution_time_seconds = ?,
                updated_at = GETDATE()
            WHERE execution_id = ?
            """
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (records_read, records_written, execution_time, execution_id))
                conn.commit()
                
            print(f"✅ Execução concluída com sucesso: {execution_id}")
            print(f"📊 Registros processados: {records_read:,} → {records_written:,}")
            print(f"⏱️ Tempo total: {execution_time:.2f}s")
            
            self.logger.info(f"Execução {execution_id} concluída - {records_read} registros processados em {execution_time:.2f}s")
            
        except Exception as e:
            self.logger.error(f"Erro ao marcar execução como concluída: {e}")
    
    def log_execution_error(
        self,
        execution_id: str,
        error: Exception,
        additional_context: Optional[Dict[str, Any]] = None
    ):
        """
        Registra erro na execução
        
        Args:
            execution_id: ID da execução
            error: Exceção que ocorreu
            additional_context: Contexto adicional do erro
        """
        
        execution_time = 0.0
        if self.execution_start_time:
            execution_time = (datetime.now() - self.execution_start_time).total_seconds()
        
        error_message = str(error)
        error_stack_trace = traceback.format_exc()
        
        # Modo demonstração
        if os.getenv('DINO_DEMO_MODE') == 'true':
            print(f"❌ [DEMO] Execução falhou: {execution_id[:8]}... | {error_message} | {execution_time:.2f}s")
            return
        
        try:
            sql = """
            UPDATE dino_execution_logs 
            SET status = 'erro',
                execution_time_seconds = ?,
                error_message = ?,
                error_stack_trace = ?,
                updated_at = GETDATE()
            WHERE execution_id = ?
            """
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (execution_time, error_message, error_stack_trace, execution_id))
                conn.commit()
                
            print(f"❌ Execução falhou: {execution_id}")
            print(f"💥 Erro: {error_message}")
            print(f"⏱️ Tempo até falha: {execution_time:.2f}s")
            
            self.logger.error(f"Execução {execution_id} falhou após {execution_time:.2f}s: {error_message}")
            
        except Exception as e:
            self.logger.error(f"Erro ao registrar falha da execução: {e}")
    
    def _insert_log_entry(self, log_entry: LogEntry):
        """Insere entrada de log no banco"""
        
        # Modo demonstração
        if os.getenv('DINO_DEMO_MODE') == 'true':
            print(f"📝 [DEMO] Log inserido: {log_entry.execution_id[:8]}... | {log_entry.status} | {log_entry.table_name}")
            return
        
        try:
            sql = """
            INSERT INTO dino_execution_logs (
                execution_id, job_name, table_name, schema_name, catalog_name,
                status, source_path, target_path, records_read, records_written,
                execution_time_seconds, error_message, error_stack_trace,
                ingestion_mode, file_format, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            values = (
                log_entry.execution_id,
                log_entry.job_name,
                log_entry.table_name,
                log_entry.schema_name,
                log_entry.catalog_name,
                log_entry.status,
                log_entry.source_path,
                log_entry.target_path,
                log_entry.records_read,
                log_entry.records_written,
                log_entry.execution_time_seconds,
                log_entry.error_message,
                log_entry.error_stack_trace,
                log_entry.ingestion_mode,
                log_entry.file_format,
                log_entry.created_at
            )
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, values)
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Erro ao inserir log: {e}")
            # Não propagar erro para não quebrar execução principal
    
    def get_execution_history(
        self,
        limit: int = 50,
        status_filter: Optional[str] = None,
        table_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtém histórico de execuções
        
        Args:
            limit: Limite de registros
            status_filter: Filtrar por status
            table_filter: Filtrar por tabela
            
        Returns:
            Lista de execuções
        """
        
        try:
            sql = """
            SELECT TOP (?) 
                execution_id, job_name, table_name, schema_name, catalog_name,
                status, source_path, target_path, records_read, records_written,
                execution_time_seconds, error_message, ingestion_mode, file_format,
                created_at, updated_at
            FROM dino_execution_logs
            WHERE 1=1
            """
            
            params = [limit]
            
            if status_filter:
                sql += " AND status = ?"
                params.append(status_filter)
            
            if table_filter:
                sql += " AND table_name LIKE ?"
                params.append(f"%{table_filter}%")
            
            sql += " ORDER BY created_at DESC"
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, params)
                
                columns = [column[0] for column in cursor.description]
                results = []
                
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                
                return results
                
        except Exception as e:
            self.logger.error(f"Erro ao obter histórico: {e}")
            return []
    
    def get_execution_stats(self, days: int = 30) -> Dict[str, Any]:
        """
        Obtém estatísticas de execução
        
        Args:
            days: Período em dias para análise
            
        Returns:
            Estatísticas de execução
        """
        
        try:
            sql = """
            SELECT 
                COUNT(*) as total_executions,
                SUM(CASE WHEN status = 'concluido' THEN 1 ELSE 0 END) as successful_executions,
                SUM(CASE WHEN status = 'erro' THEN 1 ELSE 0 END) as failed_executions,
                SUM(CASE WHEN status = 'iniciado' THEN 1 ELSE 0 END) as running_executions,
                AVG(execution_time_seconds) as avg_execution_time,
                SUM(records_read) as total_records_read,
                SUM(records_written) as total_records_written,
                MAX(created_at) as last_execution
            FROM dino_execution_logs
            WHERE created_at >= DATEADD(day, -?, GETDATE())
            """
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (days,))
                
                row = cursor.fetchone()
                if row:
                    columns = [column[0] for column in cursor.description]
                    return dict(zip(columns, row))
                
                return {}
                
        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas: {e}")
            return {}
    
    def cleanup_old_logs(self, days_to_keep: int = 90):
        """
        Remove logs antigos
        
        Args:
            days_to_keep: Dias de logs para manter
        """
        
        try:
            sql = """
            DELETE FROM dino_execution_logs 
            WHERE created_at < DATEADD(day, -?, GETDATE())
            """
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (days_to_keep,))
                deleted_count = cursor.rowcount
                conn.commit()
                
            self.logger.info(f"Limpeza de logs concluída: {deleted_count} registros removidos")
            
        except Exception as e:
            self.logger.error(f"Erro na limpeza de logs: {e}")


# Instância singleton
_sql_logger = None

def get_sql_logger() -> AzureSQLLogger:
    """Obtém instância singleton do logger SQL"""
    global _sql_logger
    if _sql_logger is None:
        _sql_logger = AzureSQLLogger()
    return _sql_logger
