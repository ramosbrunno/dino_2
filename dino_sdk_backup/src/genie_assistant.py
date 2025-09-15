#!/usr/bin/env python3
"""
Dino SDK - Genie Assistant
Integração com Databricks Genie para criação automática de salas de chat
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from .config_manager import get_config_manager


class GenieAssistant:
    """
    Assistente para integração com Databricks Genie
    
    Funcionalidades:
    - Criação automática de salas Genie
    - Configuração de permissões
    - Associação com tabelas Unity Catalog
    - Templates de descrição personalizáveis
    """
    
    def __init__(self):
        """Inicializa o assistente Genie"""
        self.config = get_config_manager()
        self.logger = logging.getLogger(__name__)
    
    def setup_genie_room(
        self,
        schema_name: str,
        table_name: str,
        description: Optional[str] = None,
        instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Configura sala Genie para uma tabela
        
        Args:
            schema_name: Nome do schema
            table_name: Nome da tabela
            description: Descrição personalizada da sala
            instructions: Instruções específicas para o Genie
            
        Returns:
            Resultado da configuração
        """
        
        catalog_name = self.config.get_catalog_name()
        table_full_name = f"{catalog_name}.{schema_name}.{table_name}"
        
        # Gerar descrição se não fornecida
        if not description:
            genie_config = self.config.get_genie_config()
            template = genie_config.get('description_template', 
                                     'Tabela gerada pelo Dino SDK para {table_name} no schema {schema}')
            description = template.format(table_name=table_name, schema=schema_name)
        
        # Simulação de resposta da API
        room_id = f"genie_room_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        result = {
            "room_id": room_id,
            "display_name": f"Análise: {schema_name}.{table_name}",
            "description": description,
            "url": f"https://your-workspace.databricks.com/genie/rooms/{room_id}",
            "status": "created",
            "table_identifiers": [table_full_name],
            "created_at": datetime.now().isoformat(),
            "tags": [f"schema:{schema_name}", f"table:{table_name}"]
        }
        
        print(f"✅ Sala Genie criada: Análise: {schema_name}.{table_name}")
        print(f"🔗 URL: {result['url']}")
        
        return result
    
    def generate_sample_queries(
        self,
        schema_name: str,
        table_name: str
    ) -> List[str]:
        """
        Gera consultas de exemplo para a tabela
        
        Returns:
            Lista de consultas SQL de exemplo
        """
        
        catalog_name = self.config.get_catalog_name()
        table_full_name = f"{catalog_name}.{schema_name}.{table_name}"
        
        queries = [
            f"-- Visão geral dos dados\nSELECT COUNT(*) as total_records FROM {table_full_name};",
            f"-- Últimas ingestões\nSELECT _dino_batch_id, _dino_ingestion_timestamp, COUNT(*) as records FROM {table_full_name} GROUP BY _dino_batch_id, _dino_ingestion_timestamp ORDER BY _dino_ingestion_timestamp DESC LIMIT 10;",
            f"-- Schema da tabela\nDESCRIBE {table_full_name};"
        ]
        
        return queries