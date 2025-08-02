# Unity Catalog and Serverless Configuration Scripts
# This directory contains configuration scripts for Databricks post-deployment setup

import json
import requests
import time
from typing import Dict, List, Optional

class DatabricksConfigurator:
    """
    Configurador para Databricks Unity Catalog e Serverless
    """
    
    def __init__(self, workspace_url: str, access_token: str):
        self.workspace_url = workspace_url.rstrip('/')
        self.access_token = access_token
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    
    def _make_request(self, method: str, endpoint: str, data: dict = None) -> requests.Response:
        """Faz requisição para a API do Databricks"""
        url = f"{self.workspace_url}/api/2.1/{endpoint}"
        
        if method.upper() == 'GET':
            response = requests.get(url, headers=self.headers, params=data)
        elif method.upper() == 'POST':
            response = requests.post(url, headers=self.headers, json=data)
        elif method.upper() == 'PUT':
            response = requests.put(url, headers=self.headers, json=data)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=self.headers, json=data)
        else:
            raise ValueError(f"Método HTTP não suportado: {method}")
        
        return response
    
    def create_unity_catalog_metastore(self, storage_root: str, region: str) -> Dict:
        """
        Cria Unity Catalog Metastore
        """
        print("🗄️  Criando Unity Catalog Metastore...")
        
        metastore_data = {
            "name": f"unity-catalog-{region.lower().replace(' ', '-')}",
            "storage_root": storage_root,
            "region": region
        }
        
        response = self._make_request('POST', 'unity-catalog/metastores', metastore_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Unity Catalog Metastore criado: {result['name']}")
            return result
        else:
            print(f"❌ Erro ao criar Metastore: {response.text}")
            return {}
    
    def assign_metastore_to_workspace(self, metastore_id: str, workspace_id: str) -> bool:
        """
        Atribui Metastore ao Workspace
        """
        print("🔗 Atribuindo Metastore ao Workspace...")
        
        assignment_data = {
            "metastore_id": metastore_id,
            "default_catalog_name": "main"
        }
        
        response = self._make_request('PUT', f'unity-catalog/workspaces/{workspace_id}/metastore', assignment_data)
        
        if response.status_code == 200:
            print("✅ Metastore atribuído ao workspace com sucesso!")
            return True
        else:
            print(f"❌ Erro ao atribuir Metastore: {response.text}")
            return False
    
    def create_catalog(self, catalog_name: str, comment: str = None) -> Dict:
        """
        Cria Catalog no Unity Catalog
        """
        print(f"📚 Criando Catalog: {catalog_name}...")
        
        catalog_data = {
            "name": catalog_name,
            "comment": comment or f"Catalog para dados do projeto"
        }
        
        response = self._make_request('POST', 'unity-catalog/catalogs', catalog_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Catalog criado: {result['name']}")
            return result
        else:
            print(f"❌ Erro ao criar Catalog: {response.text}")
            return {}
    
    def create_schema(self, catalog_name: str, schema_name: str, comment: str = None) -> Dict:
        """
        Cria Schema dentro do Catalog
        """
        print(f"🗂️  Criando Schema: {catalog_name}.{schema_name}...")
        
        schema_data = {
            "name": schema_name,
            "catalog_name": catalog_name,
            "comment": comment or f"Schema para dados do ambiente"
        }
        
        response = self._make_request('POST', 'unity-catalog/schemas', schema_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Schema criado: {result['full_name']}")
            return result
        else:
            print(f"❌ Erro ao criar Schema: {response.text}")
            return {}
    
    def enable_serverless_compute(self) -> bool:
        """
        Habilita Serverless Compute
        """
        print("⚡ Habilitando Serverless Compute...")
        
        # Configuração para habilitar Serverless
        serverless_config = {
            "enable_serverless_compute": True,
            "enable_automatic_cluster_update": True
        }
        
        response = self._make_request('PUT', 'workspace-conf', serverless_config)
        
        if response.status_code == 200:
            print("✅ Serverless Compute habilitado!")
            return True
        else:
            print(f"❌ Erro ao habilitar Serverless: {response.text}")
            return False
    
    def create_serverless_warehouse(self, warehouse_name: str, cluster_size: str = "2X-Small") -> Dict:
        """
        Cria SQL Warehouse Serverless
        """
        print(f"🏭 Criando SQL Warehouse Serverless: {warehouse_name}...")
        
        warehouse_data = {
            "name": warehouse_name,
            "cluster_size": cluster_size,
            "min_num_clusters": 1,
            "max_num_clusters": 1,
            "auto_stop_mins": 10,
            "enable_photon": True,
            "enable_serverless_compute": True,
            "warehouse_type": "PRO",
            "spot_instance_policy": "COST_OPTIMIZED"
        }
        
        response = self._make_request('POST', 'sql/warehouses', warehouse_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SQL Warehouse Serverless criado: {result['name']}")
            return result
        else:
            print(f"❌ Erro ao criar SQL Warehouse: {response.text}")
            return {}
    
    def setup_complete_environment(self, projeto: str, ambiente: str, storage_root: str, region: str, workspace_id: str) -> Dict:
        """
        Configuração completa do ambiente Unity Catalog + Serverless
        """
        print(f"🚀 Configurando ambiente completo para {projeto}-{ambiente}...")
        
        results = {
            "metastore": {},
            "catalog": {},
            "schemas": [],
            "warehouse": {},
            "status": "success"
        }
        
        try:
            # 1. Criar Metastore
            metastore = self.create_unity_catalog_metastore(storage_root, region)
            if metastore:
                results["metastore"] = metastore
                
                # 2. Atribuir Metastore ao Workspace
                self.assign_metastore_to_workspace(metastore["metastore_id"], workspace_id)
            
            # 3. Aguardar alguns segundos para propagação
            print("⏳ Aguardando propagação da configuração...")
            time.sleep(30)
            
            # 4. Criar Catalog principal
            catalog_name = f"{projeto}_{ambiente}"
            catalog = self.create_catalog(catalog_name, f"Catalog principal para {projeto} em {ambiente}")
            if catalog:
                results["catalog"] = catalog
            
            # 5. Criar Schemas padrão
            schemas = ["bronze", "silver", "gold", "workspace"]
            for schema_name in schemas:
                schema = self.create_schema(catalog_name, schema_name, f"Schema {schema_name} para arquitetura medallion")
                if schema:
                    results["schemas"].append(schema)
            
            # 6. Habilitar Serverless
            self.enable_serverless_compute()
            
            # 7. Criar SQL Warehouse Serverless
            warehouse_name = f"{projeto}-{ambiente}-warehouse"
            warehouse = self.create_serverless_warehouse(warehouse_name)
            if warehouse:
                results["warehouse"] = warehouse
            
            print("🎉 Configuração completa do ambiente finalizada!")
            
        except Exception as e:
            print(f"❌ Erro durante configuração: {str(e)}")
            results["status"] = "error"
            results["error"] = str(e)
        
        return results

def main():
    """
    Função principal para execução standalone
    """
    import os
    
    # Parâmetros podem ser passados via variáveis de ambiente
    workspace_url = os.getenv('DATABRICKS_WORKSPACE_URL')
    access_token = os.getenv('DATABRICKS_ACCESS_TOKEN')
    projeto = os.getenv('PROJETO', 'test')
    ambiente = os.getenv('AMBIENTE', 'dev')
    storage_root = os.getenv('UNITY_CATALOG_STORAGE_ROOT')
    region = os.getenv('AZURE_REGION', 'East US')
    workspace_id = os.getenv('DATABRICKS_WORKSPACE_ID')
    
    if not all([workspace_url, access_token, storage_root, workspace_id]):
        print("❌ Variáveis de ambiente necessárias não encontradas!")
        print("Necessário: DATABRICKS_WORKSPACE_URL, DATABRICKS_ACCESS_TOKEN, UNITY_CATALOG_STORAGE_ROOT, DATABRICKS_WORKSPACE_ID")
        return
    
    configurator = DatabricksConfigurator(workspace_url, access_token)
    result = configurator.setup_complete_environment(projeto, ambiente, storage_root, region, workspace_id)
    
    print("\n📋 Resumo da Configuração:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
