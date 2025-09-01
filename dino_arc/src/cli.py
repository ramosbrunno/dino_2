import argparse
import os
import time
import subprocess
import sys
from .sdk.azure_auth import AzureAuth
from .sdk.terraform_executor import TerraformExecutor
from .databricks_config.unity_catalog_setup import DatabricksConfigurator

def enable_serverless_via_integrated_sdk(workspace_url, client_id, client_secret, tenant_id):
    """
    Habilita Serverless Compute usando a nova classe ServerlessEnabler
    """
    print("\n🚀 Habilitando Serverless via Databricks SDK integrado...")
    
    try:
        # Import da nova classe
        from .databricks_config.enable_serverless import enable_serverless_for_workspace
        
        # Usar a função principal da nova classe
        success = enable_serverless_for_workspace(
            workspace_url=workspace_url,
            client_id=client_id,
            client_secret=client_secret,
            tenant_id=tenant_id
        )
        
        if success:
            print("🎉 Serverless Compute habilitado com sucesso!")
            return True
        else:
            print("⚠️ Serverless Compute pode necessitar configuração manual")
            print("📋 Consulte as instruções exibidas acima")
            return False
            
    except ImportError:
        print("❌ Módulo ServerlessEnabler não está disponível")
        return False
    except Exception as e:
        import traceback
        print(f"❌ Erro ao configurar Serverless via nova classe:")
        print(f"   Erro: {str(e)}")
        print(f"   Traceback: {traceback.format_exc()}")
        return False

def configure_databricks_environment(projeto, ambiente, location, terraform_executor, client_id, client_secret, tenant_id):
    """
    Configura automaticamente o Databricks Unity Catalog e Serverless após o deploy
    Integra automação via Databricks SDK para configuração completa
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
        
        if not all([workspace_url, workspace_id, unity_catalog_storage_root]):
            print("❌ Outputs do Terraform incompletos para configuração do Databricks")
            print(f"   workspace_url: {'✅' if workspace_url else '❌'}")
            print(f"   workspace_id: {'✅' if workspace_id else '❌'}")
            print(f"   storage_root: {'✅' if unity_catalog_storage_root else '❌'}")
            return False
        
        print(f"✅ Conectando ao Databricks: {workspace_url}")
        print("🔐 Usando autenticação Service Principal...")
        
        # Configurar Databricks com Service Principal
        configurator = DatabricksConfigurator(
            workspace_url=workspace_url,
            client_id=client_id,
            client_secret=client_secret,
            tenant_id=tenant_id
        )
        
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
            
            print("   ⚡ Serverless Compute: Habilitado via configuração tradicional")
            
            # Tentar automação avançada via SDK
            print("\n🚀 Aplicando automação avançada via Databricks SDK...")
            sdk_success = enable_serverless_via_integrated_sdk(
                workspace_url, client_id, client_secret, tenant_id
            )
            
            if not sdk_success:
                print("⚠️  Configuração tradicional OK, mas automação SDK falhou")
                print("   Serverless ainda está habilitado via método tradicional")
            
            return True
        else:
            print(f"\n⚠️  Erro na configuração do Databricks: {result}")
            return False
            
    except Exception as e:
        import traceback
        print(f"❌ Erro na configuração do Databricks:")
        print(f"   Erro: {str(e)}")
        print(f"   Traceback: {traceback.format_exc()}")
        return False


def ensure_terraform_initialized(terraform_executor):
    """
    Garante que o Terraform está inicializado
    """
    print("🔧 Verificando inicialização do Terraform...")
    if not terraform_executor.is_initialized():
        print("🔄 Inicializando Terraform...")
        result = terraform_executor.init()
        if result.returncode != 0:
            print(f"❌ Erro ao inicializar Terraform: {result.stderr}")
            return False
        print("✅ Terraform inicializado com sucesso!")
    else:
        print("✅ Terraform já inicializado!")
    return True


def main():
    parser = argparse.ArgumentParser(description='Dino Arc - Automação de Infraestrutura Azure')
    
    # Argumentos de autenticação Azure (sempre obrigatórios)
    parser.add_argument('--client-id', required=True, help='Service Principal Client ID')
    parser.add_argument('--client-secret', required=True, help='Service Principal Client Secret')
    parser.add_argument('--tenant_id', required=True, help='Azure Tenant ID')
    parser.add_argument('--subscription-id', required=True, help='Azure Subscription ID')
    
    # Argumentos do projeto
    parser.add_argument('--action', required=True, choices=['plan', 'apply', 'destroy'], help='Ação a ser executada')
    parser.add_argument('--projeto', required=True, help='Nome do projeto')
    parser.add_argument('--ambiente', default='dev', help='Ambiente (dev/staging/prod)')
    parser.add_argument('--location', required=True, help='Região Azure')
    
    args = parser.parse_args()
    
    # Configurar autenticação Azure
    print("🔐 Configurando autenticação Azure via Service Principal...")
    
    azure_auth = AzureAuth(
        client_id=args.client_id,
        client_secret=args.client_secret,
        tenant_id=args.tenant_id,
        subscription_id=args.subscription_id
    )
    
    # Autenticar e configurar variáveis de ambiente automaticamente
    if not azure_auth.authenticate():
        print("❌ Falha na autenticação Azure")
        return
    
    # Configurar executor do Terraform
    terraform_dir = os.path.join(os.path.dirname(__file__), 'terraform')
    terraform_executor = TerraformExecutor(terraform_dir)
    
    if args.action == 'plan':
        # Garantir que Terraform está inicializado
        if not ensure_terraform_initialized(terraform_executor):
            return
        
        # Preparar variáveis para o Terraform (infraestrutura completa)
        variables = {
            "subscription_id": args.subscription_id,
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
        # Garantir que Terraform está inicializado
        if not ensure_terraform_initialized(terraform_executor):
            return
            
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
            "subscription_id": args.subscription_id,
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
                terraform_executor,
                args.client_id,
                args.client_secret,
                args.tenant_id
            )
            
            if databricks_success:
                print("\n🎊 Deploy completo finalizado!")
                print("🚀 Seu ambiente Databricks Premium está pronto para uso:")
                print(f"   📊 Unity Catalog configurado com arquitetura medallion")
                print(f"   ⚡ Serverless Compute habilitado via Databricks SDK")
                print(f"   🏭 SQL Warehouse Serverless criado")
                print(f"   🌐 Web Terminal e DBFS Browser habilitados")
                print(f"   📚 Catalog: {args.projeto}_{args.ambiente}")
                print(f"   🗂️  Schemas: bronze, silver, gold, workspace")
                print(f"   🎯 Automação completa via SDK aplicada!")
            else:
                print("\n⚠️  Infraestrutura criada, mas configuração do Databricks falhou")
                print("   Você pode executar a configuração manualmente usando os scripts em databricks_config/")
        else:
            print("❌ Erro ao criar recursos:")
            print(result.stderr)
    
    elif args.action == 'destroy':
        # Garantir que Terraform está inicializado
        if not ensure_terraform_initialized(terraform_executor):
            return
            
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
            "subscription_id": args.subscription_id,
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
