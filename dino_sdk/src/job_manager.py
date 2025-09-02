#!/usr/bin/env python3
"""
Dino SDK - Job Manager
Gerenciador de jobs do Databricks para ingestão automatizada
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from .config_manager import get_config_manager


class JobManager:
    """
    Gerenciador de jobs do Databricks para execução automatizada de ingestões
    
    Funcionalidades:
    - Criação de jobs com File Arrival Trigger
    - Configuração de clusters de execução
    - Monitoramento de execuções
    - Integração com Unity Catalog
    """
    
    def __init__(self):
        """Inicializa o gerenciador de jobs"""
        self.config = get_config_manager()
        self.logger = logging.getLogger(__name__)
    
    def create_ingestion_job(
        self,
        job_name: str,
        target_schema: str,
        table_name: str,
        file_path: str,
        delimiter: str = ",",
        is_automated: bool = False,
        file_format: str = "csv",
        has_genie: bool = False
    ) -> Dict[str, Any]:
        """
        Cria job de ingestão no Databricks
        
        Args:
            job_name: Nome do job
            target_schema: Schema destino
            table_name: Nome da tabela
            file_path: Caminho dos arquivos
            delimiter: Delimitador do arquivo
            is_automated: Se deve ter file arrival trigger
            file_format: Formato do arquivo
            has_genie: Se deve configurar Genie
            
        Returns:
            Configuração do job criado
        """
        
        # Gerar comando CLI para execução no job
        cli_command = self._generate_cli_command(
            target_schema, table_name, file_path, delimiter, 
            is_automated, has_genie, file_format
        )
        
        # Configuração do cluster
        cluster_config = self._get_job_cluster_config()
        
        # Configuração do job
        job_config = {
            "name": job_name,
            "description": f"Dino SDK - Ingestão automatizada para {target_schema}.{table_name}",
            "tags": {
                "created_by": "dino-sdk",
                "schema": target_schema,
                "table": table_name,
                "format": file_format,
                "automated": str(is_automated).lower()
            },
            "tasks": [
                {
                    "task_key": "dino_ingestion",
                    "description": f"Ingestão de dados para {target_schema}.{table_name}",
                    "new_cluster": cluster_config,
                    "spark_python_task": {
                        "python_file": "dbfs:/dino-sdk/scripts/run_ingestion.py",
                        "parameters": [
                            f"--target-schema={target_schema}",
                            f"--table-name={table_name}",
                            f"--file-path={file_path}",
                            f"--delimiter={delimiter}",
                            f"--file-format={file_format}"
                        ]
                    },
                    "libraries": self._get_job_libraries(),
                    "timeout_seconds": 3600  # 1 hora
                }
            ],
            "job_clusters": [
                {
                    "job_cluster_key": "dino_cluster",
                    "new_cluster": cluster_config
                }
            ],
            "email_notifications": {
                "on_failure": [],
                "on_success": []
            }
        }
        
        # Adicionar file arrival trigger se automatizado
        if is_automated:
            job_config["trigger"] = self._get_file_arrival_trigger(file_path)
            self.logger.info(f"File arrival trigger configurado para {file_path}")
        
        # Adicionar task do Genie se solicitado
        if has_genie:
            genie_task = self._get_genie_task(target_schema, table_name)
            job_config["tasks"].append(genie_task)
            
            # Definir dependência
            job_config["tasks"][1]["depends_on"] = [{"task_key": "dino_ingestion"}]
        
        return job_config
    
    def _generate_cli_command(
        self,
        target_schema: str,
        table_name: str,
        file_path: str,
        delimiter: str,
        is_automated: bool,
        has_genie: bool,
        file_format: str
    ) -> str:
        """Gera comando CLI para execução no job"""
        
        cmd_parts = [
            "dino-ingest",
            f"--target-schema {target_schema}",
            f"--table-name {table_name}",
            f"--file-path {file_path}",
            f"--delimiter '{delimiter}'",
            f"--file-format {file_format}"
        ]
        
        if is_automated:
            cmd_parts.append("--is-automated")
        
        if has_genie:
            cmd_parts.append("--has-genie")
        
        return " ".join(cmd_parts)
    
    def _get_job_cluster_config(self) -> Dict[str, Any]:
        """Obtém configuração do cluster para jobs"""
        base_config = self.config.get_job_cluster_config()
        
        return {
            "spark_version": base_config.get("spark_version", "13.3.x-scala2.12"),
            "node_type_id": base_config.get("node_type_id", "i3.xlarge"),
            "num_workers": base_config.get("num_workers", 2),
            "spark_conf": {
                **base_config.get("spark_conf", {}),
                "spark.databricks.cluster.profile": "singleNode" if base_config.get("num_workers", 2) == 0 else "serverless",
                "spark.master": "local[*]" if base_config.get("num_workers", 2) == 0 else None
            },
            "custom_tags": {
                "ResourceClass": "SingleNode" if base_config.get("num_workers", 2) == 0 else "Serverless",
                "CreatedBy": "DinoSDK"
            },
            "enable_elastic_disk": True,
            "data_security_mode": "SINGLE_USER",
            "runtime_engine": "STANDARD"
        }
    
    def _get_job_libraries(self) -> List[Dict[str, Any]]:
        """Define bibliotecas necessárias para o job"""
        return [
            {"pypi": {"package": "dino-sdk"}},
            {"pypi": {"package": "databricks-sdk>=0.18.0"}},
            {"pypi": {"package": "pyspark>=3.4.0"}}
        ]
    
    def _get_file_arrival_trigger(self, file_path: str) -> Dict[str, Any]:
        """Configura file arrival trigger"""
        return {
            "file_arrival": {
                "url": file_path,
                "min_time_between_triggers_seconds": 60,  # 1 minuto mínimo entre triggers
                "wait_after_last_change_seconds": 300     # 5 minutos após última mudança
            }
        }
    
    def _get_genie_task(self, target_schema: str, table_name: str) -> Dict[str, Any]:
        """Configura task do Genie"""
        return {
            "task_key": "configure_genie",
            "description": f"Configurar Genie para {target_schema}.{table_name}",
            "new_cluster": self._get_job_cluster_config(),
            "python_wheel_task": {
                "package_name": "dino_sdk",
                "entry_point": "configure_genie",
                "parameters": [
                    f"--schema={target_schema}",
                    f"--table={table_name}"
                ]
            },
            "timeout_seconds": 900  # 15 minutos
        }
    
    def generate_job_script(
        self,
        target_schema: str,
        table_name: str,
        file_path: str,
        delimiter: str = ",",
        is_automated: bool = False,
        file_format: str = "csv"
    ) -> str:
        """
        Gera script Python para execução no job
        
        Returns:
            Código Python para execução
        """
        
        code = f'''#!/usr/bin/env python3
"""
Dino SDK - Script de Job
Gerado automaticamente em {datetime.now().isoformat()}
"""

import sys
import os
import argparse
from pyspark.sql import SparkSession

# Adicionar dino-sdk ao path se instalado via wheel
sys.path.append('/databricks/python/lib/python3.9/site-packages/')

try:
    from dino_sdk.ingestion_engine import IngestionEngine
    from dino_sdk.genie_assistant import GenieAssistant
    from dino_sdk.config_manager import get_config_manager
except ImportError as e:
    print(f"❌ Erro ao importar Dino SDK: {{e}}")
    print("Verifique se o SDK está instalado corretamente no cluster")
    sys.exit(1)

def main():
    """Função principal do job"""
    parser = argparse.ArgumentParser(description='Dino SDK Job Runner')
    parser.add_argument('--target-schema', required=True)
    parser.add_argument('--table-name', required=True)
    parser.add_argument('--file-path', required=True)
    parser.add_argument('--delimiter', default=',')
    parser.add_argument('--file-format', default='csv')
    parser.add_argument('--is-automated', action='store_true')
    parser.add_argument('--has-genie', action='store_true')
    
    args = parser.parse_args()
    
    print("🦕 Dino SDK - Job Execution")
    print("=" * 50)
    print(f"📊 Schema: {{args.target_schema}}")
    print(f"📋 Tabela: {{args.table_name}}")
    print(f"📁 Origem: {{args.file_path}}")
    print(f"📄 Formato: {{args.file_format}}")
    print(f"🔄 Automatizado: {{args.is_automated}}")
    
    try:
        # Configurar Spark Session
        spark = SparkSession.builder \\
            .appName(f"DinoSDK-{{args.target_schema}}-{{args.table_name}}") \\
            .getOrCreate()
        
        # Criar engine de ingestão
        engine = IngestionEngine(
            target_schema=args.target_schema,
            table_name=args.table_name,
            file_path=args.file_path,
            delimiter=args.delimiter,
            is_automated=args.is_automated,
            file_format=args.file_format
        )
        
        # Executar ingestão
        if args.is_automated:
            print("🔄 Executando ingestão streaming...")
            engine.run_streaming_ingestion()
        else:
            print("📊 Executando ingestão batch...")
            engine.run_batch_ingestion()
        
        # Configurar Genie se solicitado
        if args.has_genie:
            print("🧞 Configurando Genie Assistant...")
            genie = GenieAssistant()
            genie.setup_genie_room(
                schema_name=args.target_schema,
                table_name=args.table_name
            )
        
        print("✅ Job executado com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro na execução do job: {{e}}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        if 'spark' in locals():
            spark.stop()

if __name__ == "__main__":
    main()
'''
        
        return code
    
    def create_job_definition_file(
        self,
        job_name: str,
        target_schema: str,
        table_name: str,
        file_path: str,
        delimiter: str = ",",
        is_automated: bool = False,
        file_format: str = "csv",
        has_genie: bool = False,
        output_file: Optional[str] = None
    ) -> str:
        """
        Cria arquivo JSON com definição do job
        
        Returns:
            Caminho do arquivo criado
        """
        
        job_config = self.create_ingestion_job(
            job_name=job_name,
            target_schema=target_schema,
            table_name=table_name,
            file_path=file_path,
            delimiter=delimiter,
            is_automated=is_automated,
            file_format=file_format,
            has_genie=has_genie
        )
        
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"dino_job_{target_schema}_{table_name}_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(job_config, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Definição do job salva em: {output_file}")
        return output_file
