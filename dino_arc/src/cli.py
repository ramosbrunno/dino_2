import argparse
import os
import json
import time
from sdk.azure_auth import AzureAuth
from sdk.terraform_executor import TerraformExecutor
from databricks_config.unity_catalog_setup import DatabricksConfigurator

def configure_databricks_environment(projeto, ambiente, location, terraform_executor):
    """
    Configura automaticamente o Databricks Unity Catalog e Serverless após o deploy
    """
    print("\n🔧 Configurando Databricks Unity Catalog e Serverless...")
    
    try:
        # Obter outputs do Terraform
        print("📋 Obtendo outputs do Terraform...")
        outputs = terraform_executor.get_outputs()
        
        if not outputs:
            print("❌ Não foi possível obter outputs do Terraform")
            return False
        
        # Extrair valores necessários dos outputs
        workspace_url = outputs.get('databricks_workspace_url', {}).get('value')
        workspace_id = outputs.get('databricks_workspace_id', {}).get('value')
        unity_catalog_storage_root = outputs.get('unity_catalog_storage_root', {}).get('value')
        databricks_token = outputs.get('databricks_access_token', {}).get('value')
        
        if not all([workspace_url, workspace_id, unity_catalog_storage_root, databricks_token]):
            print("❌ Outputs do Terraform incompletos para configuração do Databricks")
            print(f"   workspace_url: {'✅' if workspace_url else '❌'}")
            print(f"   workspace_id: {'✅' if workspace_id else '❌'}")
            print(f"   storage_root: {'✅' if unity_catalog_storage_root else '❌'}")
            print(f"   access_token: {'✅' if databricks_token else '❌'}")
            return False
        
        print(f"✅ Conectando ao Databricks: {workspace_url}")
        
        # Configurar Databricks
        configurator = DatabricksConfigurator(workspace_url, databricks_token)
        
        # Executar configuração completa
        result = configurator.setup_complete_environment(
            projeto=projeto,
            ambiente=ambiente,
            storage_root=unity_catalog_storage_root,
            region=location,
            workspace_id=workspace_id
        )
        
        if result.get('status') == 'success':
            print("\n🎉 Configuração do Databricks finalizada com sucesso!")
            print("📋 Recursos criados:")
            
            if result.get('metastore'):
                print(f"   🗄️  Metastore: {result['metastore'].get('name', 'Criado')}")
            
            if result.get('catalog'):
                print(f"   📚 Catalog: {result['catalog'].get('name', f'{projeto}_{ambiente}')}")
            
            if result.get('schemas'):
                print(f"   🗂️  Schemas: {len(result['schemas'])} criados (bronze, silver, gold, workspace)")
            
            if result.get('warehouse'):
                print(f"   🏭 SQL Warehouse: {result['warehouse'].get('name', f'{projeto}-{ambiente}-warehouse')}")
            
            print("   ⚡ Serverless Compute: Habilitado")
            return True
        else:
            print(f"❌ Erro na configuração do Databricks: {result.get('error', 'Erro desconhecido')}")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante configuração do Databricks: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Dino ARC CLI - Complete Azure Infrastructure Creator')
    
    # Argumentos de autenticação Azure
    parser.add_argument('--client-id', required=True, help='Azure Client ID')
    parser.add_argument('--client-secret', required=True, help='Azure Client Secret')
    parser.add_argument('--tenant_id', required=True, help='Azure Tenant ID')
    
    # Ação do Terraform
    parser.add_argument('--action', choices=['init', 'plan', 'apply', 'destroy'], required=True, 
                       help='Ação que será executada no script Terraform')
    
    # Parâmetros principais (simplificados)
    parser.add_argument('--projeto', type=str, required=True,
                       help='Nome do projeto (será usado como base para todos os recursos)')
    parser.add_argument('--ambiente', type=str, choices=['dev', 'staging', 'prod'], default='dev',
                       help='Ambiente (dev, staging, prod) - padrão: dev')
    parser.add_argument('--location', type=str, default='East US',
                       help='Localização do Azure (padrão: East US)')

    args = parser.parse_args()

    # Validação: projeto é obrigatório para todas as ações exceto init
    if args.action in ['plan', 'apply', 'destroy'] and not args.projeto:
        parser.error(f"--projeto é obrigatório para a ação '{args.action}'")

    # Autenticação Azure
    azure_auth = AzureAuth(args.client_id, args.client_secret, args.tenant_id)
    azure_auth.authenticate()

    # Executor Terraform
    terraform_executor = TerraformExecutor()

    if args.action == 'init':
        print("🔧 Inicializando Terraform...")
        result = terraform_executor.init()
        if result.returncode == 0:
            print("✅ Terraform inicializado com sucesso!")
        else:
            print("❌ Erro ao inicializar Terraform:")
            print(result.stderr)
    
    elif args.action == 'plan':
        # Preparar variáveis para o Terraform (infraestrutura completa)
        variables = {
            "projeto": args.projeto,
            "ambiente": args.ambiente,
            "location": args.location
        }
        
        print(f"📋 Visualizando plano para projeto '{args.projeto}' no ambiente '{args.ambiente}'...")
        print(f"📍 Localização: {args.location}")
        print(f"🏗️  Infraestrutura completa:")
        print(f"   ✅ Foundation (Resource Group + Key Vault + Service Principal)")
        print(f"   ✅ Databricks Premium (Unity Catalog + Serverless)")
        
        result = terraform_executor.plan(variables=variables)
        if result.returncode == 0:
            print("✅ Plano gerado com sucesso!")
        else:
            print("❌ Erro ao gerar plano:")
            print(result.stderr)
    
    elif args.action == 'apply':
        # Gerar nomes dos recursos usando o padrão projeto-ambiente-sufixo
        resource_group_name = f"{args.projeto}-{args.ambiente}-rsg"
        service_principal_name = f"{args.projeto}-{args.ambiente}-spn"
        
        print(f"🚀 Criando infraestrutura completa para projeto '{args.projeto}' no ambiente '{args.ambiente}' em '{args.location}'...")
        print(f"📦 Resource Group: {resource_group_name}")
        print(f"🔐 Key Vault: {args.projeto}-{args.ambiente}-akv-[random]")
        print(f"👤 Service Principal: {service_principal_name}")
        print(f"🧮 Databricks Premium: {args.projeto}-{args.ambiente}-dbw-[random]")
        print(f"📊 Unity Catalog Storage: {args.projeto.replace('-', '')}{args.ambiente}ucsa[random]")
        print(f"🔑 Todas as credenciais armazenadas no Key Vault!")

        # Preparar variáveis para o Terraform (infraestrutura completa)
        variables = {
            "projeto": args.projeto,
            "ambiente": args.ambiente,
            "location": args.location
        }
        
        result = terraform_executor.apply(variables=variables)
        if result.returncode == 0:
            print("✅ Infraestrutura completa criada com sucesso!")
            print("📋 Componentes implantados:")
            print("   🏛️  Foundation (Resource Group + Key Vault + Service Principal)")
            print("   🧮 Databricks Premium (Unity Catalog + Serverless)")
            
            # Aguardar um pouco para garantir que os recursos estão prontos
            print("\n⏳ Aguardando recursos ficarem prontos para configuração...")
            time.sleep(60)
            
            # Configurar Databricks automaticamente
            databricks_success = configure_databricks_environment(
                args.projeto, 
                args.ambiente, 
                args.location, 
                terraform_executor
            )
            
            if databricks_success:
                print("\n🎊 Deploy completo finalizado!")
                print("🚀 Seu ambiente Databricks Premium está pronto para uso:")
                print(f"   📊 Unity Catalog configurado com arquitetura medallion")
                print(f"   ⚡ Serverless Compute habilitado")
                print(f"   🏭 SQL Warehouse Serverless criado")
                print(f"   📚 Catalog: {args.projeto}_{args.ambiente}")
                print(f"   🗂️  Schemas: bronze, silver, gold, workspace")
            else:
                print("\n⚠️  Infraestrutura criada, mas configuração do Databricks falhou")
                print("   Você pode executar a configuração manualmente usando os scripts em databricks_config/")
        else:
            print("❌ Erro ao criar recursos:")
            print(result.stderr)
    
    elif args.action == 'destroy':
        resource_group_name = f"{args.projeto}-{args.ambiente}-rsg"
        service_principal_name = f"{args.projeto}-{args.ambiente}-spn"
        
        print(f"🗑️  Destruindo infraestrutura completa do projeto '{args.projeto}' no ambiente '{args.ambiente}'...")
        print(f"📦 Resource Group: {resource_group_name}")
        print(f"👤 Service Principal: {service_principal_name}")
        print(f"🔐 Key Vault e secrets serão removidos")
        print(f"🧮 Databricks Workspace Premium será removido")
        print(f"📊 Unity Catalog Storage será removido")
        
        # Preparar variáveis para o Terraform (infraestrutura completa)
        variables = {
            "projeto": args.projeto,
            "ambiente": args.ambiente,
            "location": args.location
        }
        
        result = terraform_executor.destroy(variables=variables)
        if result.returncode == 0:
            print("✅ Toda a infraestrutura destruída com sucesso!")
        else:
            print("❌ Erro ao destruir recursos:")
            print(result.stderr)

if __name__ == '__main__':
    main()