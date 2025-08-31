#!/usr/bin/env python3  
import sys  
import os
import subprocess
from pathlib import Path

def main():  
    print("DINO ARC v2.0.0 - Automated Resource Creator via Terraform + SPN", flush=True)  
  
    if "--help" in sys.argv:  
        print("Usage: dino_arc [options]", flush=True)  
        print("", flush=True)  
        print("Options:", flush=True)  
        print("  --help                    Show this help", flush=True)  
        print("  --client-id ID            Azure Service Principal Client ID", flush=True)  
        print("  --client-secret SECRET    Azure Service Principal Client Secret", flush=True)  
        print("  --tenant-id ID            Azure Tenant ID", flush=True)  
        print("  --subscription-id ID      Azure subscription ID", flush=True)  
        print("  --action ACTION           Action to perform (apply)", flush=True)  
        print("  --projeto NAME           Project name", flush=True)  
        print("  --ambiente ENV           Environment (dev/prod)", flush=True)  
        print("  --location REGION        Azure region (default: East US 2)", flush=True)  
        print("", flush=True)  
        print("Example:", flush=True)  
        print("  dino_arc \\", flush=True)  
        print("    --client-id \"your-client-id\" \\", flush=True)  
        print("    --client-secret \"your-client-secret\" \\", flush=True)  
        print("    --tenant-id \"your-tenant-id\" \\", flush=True)  
        print("    --subscription-id \"your-subscription-id\" \\", flush=True)  
        print("    --action apply \\", flush=True)  
        print("    --projeto dino \\", flush=True)  
        print("    --ambiente dev", flush=True)  
        return

    # Parse arguments  
    args = {}  
    for i, arg in enumerate(sys.argv):  
        if arg == "--apply" or arg == "--action" and i+1 < len(sys.argv) and sys.argv[i+1] == "apply":  
            args["apply"] = True  
        elif arg == "--client-id" and i+1 < len(sys.argv):  
            args["client_id"] = sys.argv[i+1]  
        elif arg == "--client-secret" and i+1 < len(sys.argv):  
            args["client_secret"] = sys.argv[i+1]  
        elif arg == "--tenant-id" and i+1 < len(sys.argv):  
            args["tenant_id"] = sys.argv[i+1]  
        elif arg == "--subscription-id" and i+1 < len(sys.argv):  
            args["subscription_id"] = sys.argv[i+1]  
        elif arg == "--action" and i+1 < len(sys.argv):  
            if sys.argv[i+1] == "apply":  
                args["apply"] = True  
        elif arg == "--projeto" and i+1 < len(sys.argv):  
            args["projeto"] = sys.argv[i+1]  
        elif arg == "--ambiente" and i+1 < len(sys.argv):  
            args["ambiente"] = sys.argv[i+1]  
        elif arg == "--location" and i+1 < len(sys.argv):  
            args["location"] = sys.argv[i+1]  

    if args.get("apply"):  
        print("Executando DINO ARC com parametros:", flush=True)  
        print("  Client ID: " + args.get("client_id", "NAO_INFORMADO"), flush=True)  
        print("  Client Secret: " + ("*" * len(args.get("client_secret", "")) if args.get("client_secret") else "NAO_INFORMADO"), flush=True)  
        print("  Tenant ID: " + args.get("tenant_id", "NAO_INFORMADO"), flush=True)  
        print("  Subscription ID: " + args.get("subscription_id", "NAO_INFORMADO"), flush=True)  
        print("  Projeto: " + args.get("projeto", "NAO_INFORMADO"), flush=True)  
        print("  Ambiente: " + args.get("ambiente", "NAO_INFORMADO"), flush=True)  
        print("  Location: " + args.get("location", "East US 2"), flush=True)
        print("", flush=True)
        
        # Validações
        required_args = ["client_id", "client_secret", "tenant_id", "subscription_id", "projeto", "ambiente"]
        missing_args = [arg for arg in required_args if not args.get(arg)]
        
        if missing_args:
            print(f"❌ Erro: Parâmetros obrigatórios não informados: {', '.join(missing_args)}", flush=True)
            return 1
        
        print("🚀 Iniciando criação REAL de recursos Azure via Terraform + SPN...", flush=True)
        print("", flush=True)
        
        try:
            # Configurar variáveis de ambiente para autenticação SPN
            terraform_env = os.environ.copy()
            terraform_env.update({
                'ARM_CLIENT_ID': args["client_id"],
                'ARM_CLIENT_SECRET': args["client_secret"], 
                'ARM_TENANT_ID': args["tenant_id"],
                'ARM_SUBSCRIPTION_ID': args["subscription_id"],
                'TF_VAR_subscription_id': args["subscription_id"],
                'TF_VAR_projeto': args["projeto"],
                'TF_VAR_ambiente': args["ambiente"],
                'TF_VAR_location': args.get("location", "East US 2")
            })
            
            # Navegar para diretório Terraform
            terraform_dir = os.path.join(os.path.dirname(__file__), "src", "terraform")
            
            if not os.path.exists(terraform_dir):
                print(f"❌ Diretório Terraform não encontrado: {terraform_dir}", flush=True)
                return 1
            
            print("🔧 1. Inicializando Terraform...", flush=True)
            init_cmd = ["terraform", "init"]
            init_result = subprocess.run(init_cmd, cwd=terraform_dir, env=terraform_env, capture_output=True, text=True)
            
            if init_result.returncode != 0:
                print(f"❌ Erro ao inicializar Terraform: {init_result.stderr}", flush=True)
                return 1
            print("✅ Terraform inicializado com sucesso!", flush=True)
            
            print("📋 2. Planejando infraestrutura...", flush=True)
            plan_cmd = ["terraform", "plan", "-out=tfplan"]
            plan_result = subprocess.run(plan_cmd, cwd=terraform_dir, env=terraform_env, capture_output=True, text=True)
            
            if plan_result.returncode != 0:
                print(f"❌ Erro no planejamento: {plan_result.stderr}", flush=True)
                return 1
            print("✅ Planejamento concluído!", flush=True)
            
            print("🏗️ 3. Aplicando infraestrutura...", flush=True)
            print("📦 Criando recursos:", flush=True)
            print("  🔄 Foundation (Resource Group, Key Vault, Service Principal)", flush=True)
            print("  🔄 Databricks Premium (Workspace, Unity Catalog, Serverless)", flush=True)
            print("  🔄 Azure SQL Database (Server, Database)", flush=True)
            print("", flush=True)
            
            apply_cmd = ["terraform", "apply", "-auto-approve", "tfplan"]
            apply_result = subprocess.run(apply_cmd, cwd=terraform_dir, env=terraform_env, capture_output=True, text=True)
            
            if apply_result.returncode == 0:
                print("✅ Infraestrutura criada com sucesso!", flush=True)
                print("", flush=True)
                print("🎯 RECURSOS CRIADOS:", flush=True)
                print("  ✅ Resource Group", flush=True)
                print("  ✅ Key Vault", flush=True)
                print("  ✅ Service Principal", flush=True)
                print("  ✅ Azure SQL Database", flush=True)
                print("  ✅ Databricks Workspace Premium", flush=True)
                print("  ✅ Unity Catalog Setup", flush=True)
                print("  ✅ Serverless Computing Enable", flush=True)
                print("", flush=True)
                print("🚀 DINO ARC: Todos os recursos foram provisionados com sucesso!", flush=True)
                return 0
            else:
                print("❌ Erro durante aplicação da infraestrutura:", flush=True)
                print(apply_result.stderr, flush=True)
                return 1
                
        except FileNotFoundError:
            print("❌ Terraform não está instalado. Por favor, instale o Terraform primeiro.", flush=True)
            print("💡 Download: https://www.terraform.io/downloads.html", flush=True)
            return 1
        except Exception as e:
            print(f"❌ Erro inesperado: {e}", flush=True)
            return 1
    else:  
        print("Use --help para ver opcoes ou --action apply para executar", flush=True)  

if __name__ == "__main__":  
    sys.exit(main())
