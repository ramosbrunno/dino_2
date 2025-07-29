import argparse
from sdk.azure_auth import AzureAuth
from sdk.terraform_executor import TerraformExecutor

def main():
    parser = argparse.ArgumentParser(description='Dino ARC CLI')
    parser.add_argument('--client-id', required=True, help='Azure Client ID')
    parser.add_argument('--client-secret', required=True, help='Azure Client Secret')
    parser.add_argument('--tenant_id', required=True, help='Azure Tenant ID')
    parser.add_argument('--action', choices=['init', 'apply', 'destroy'], required=True, help='Ação que será executada no script Terraform')

    args = parser.parse_args()

    azure_auth = AzureAuth(args.client_id, args.client_secret, args.tenant_id)
    azure_auth.authenticate()

    terraform_executor = TerraformExecutor()

    if args.action == 'init':
        terraform_executor.init()
    elif args.action == 'apply':
        terraform_executor.apply()
    elif args.action == 'destroy':
        terraform_executor.destroy()

if __name__ == '__main__':
    main()