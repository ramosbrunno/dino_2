# Dino Arc - Azure Resource Creator

## 🎯 Visão Geral

**Dino Arc** é uma ferramenta CLI que automatiza a criação de recursos fundamentais no Azure usando Terraform. Com apenas 3 parâmetros obrigatórios, você cria uma infraestrutura completa e segura com:

- 📦 **Resource Group** com nomenclatura padronizada
- 🔐 **Key Vault** com configurações de segurança adequadas
- 👤 **Service Principal** com permissões específicas e credenciais seguras
- 🏷️ **Tags** automáticas para governança

## 🚀 Recursos Principais

### ✅ Criação Automática Completa
- Resource Group com tags de governança
- Key Vault com configurações de produção
- Service Principal com permissões adequadas
- Credenciais armazenadas automaticamente no Key Vault

### ✅ Nomenclatura Consistente
Todos os recursos seguem o padrão `{projeto}-{ambiente}-{sufixo}`:
- Resource Group: `analytics-dev-rsg`
- Key Vault: `analytics-dev-akv-abc123`
- Service Principal: `analytics-dev-spn`

### ✅ Configurações de Segurança
- Service Principal com permissões mínimas necessárias
- Key Vault com access policies adequadas
- Credenciais armazenadas como secrets seguros
- Network access configurado adequadamente

## 🛠️ Instalação

### Pré-requisitos
```bash
# Instalar Terraform (≥ 1.0)
# Windows: https://www.terraform.io/downloads.html

# Instalar Azure CLI
# Windows: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-windows

# Fazer login no Azure
az login
```

### Instalar Dino Arc
```bash
# Clonar o repositório
git clone <repo-url>
cd dino_arc

# Instalar dependências
pip install -r requirements.txt

# Instalar como pacote
pip install -e .
```

## 📋 Uso Rápido

### Comando Básico
```bash
# Criar infraestrutura completa
dino-arc apply --projeto "meu-projeto" --ambiente "dev" --location "East US"
```

### Comandos Disponíveis
```bash
# Planejar recursos (visualizar sem criar)
dino-arc plan --projeto "analytics" --ambiente "dev" --location "East US"

# Criar recursos
dino-arc apply --projeto "analytics" --ambiente "dev" --location "East US"

# Destruir recursos
dino-arc destroy --projeto "analytics" --ambiente "dev" --location "East US"
```

## 📦 Recursos Criados

### Resource Group
- Nome: `{projeto}-{ambiente}-rsg`
- Localização: Conforme especificado
- Tags automáticas de governança

### Key Vault
- Nome: `{projeto}-{ambiente}-akv-{random}`
- SKU: Standard (adequado para a maioria dos casos)
- Soft Delete: 7 dias
- Access policies configuradas para o Service Principal

### Service Principal
- Nome: `{projeto}-{ambiente}-spn`
- Permissões:
  - **Reader** no nível da assinatura
  - **Contributor** no Resource Group
  - **Key Vault Secrets Officer** no Key Vault

### Secrets no Key Vault
- `spn-client-id`: Application (Client) ID
- `spn-client-secret`: Client Secret
- `spn-tenant-id`: Tenant ID

## 🎯 Exemplos de Uso

### Desenvolvimento
```bash
dino-arc apply --projeto "webapp" --ambiente "dev" --location "East US"
```

### Staging
```bash
dino-arc apply --projeto "webapp" --ambiente "staging" --location "East US 2"
```

### Produção
```bash
dino-arc apply --projeto "webapp" --ambiente "prod" --location "Brazil South"
```

## 📊 Saída Típica

```
🚀 Criando recursos para projeto 'analytics' no ambiente 'dev' em 'East US'...
📦 Resource Group: analytics-dev-rsg
🔐 Key Vault: analytics-dev-akv-abc123
👤 Service Principal: analytics-dev-spn
🔑 Service Principal criada e credenciais armazenadas no Key Vault!

✅ Recursos criados com sucesso!

📋 Resumo da Implantação:
{
  "resource_group": {
    "name": "analytics-dev-rsg",
    "location": "eastus"
  },
  "key_vault": {
    "name": "analytics-dev-akv-abc123",
    "uri": "https://analytics-dev-akv-abc123.vault.azure.net/"
  },
  "service_principal": {
    "name": "analytics-dev-spn",
    "application_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
  }
}
```

## 🔧 Estrutura do Projeto

```
dino_arc/
├── src/
│   ├── cli.py                    # Interface CLI principal
│   ├── sdk/
│   │   ├── azure_auth.py         # Autenticação Azure
│   │   ├── terraform_executor.py # Execução Terraform
│   │   └── utils.py              # Utilitários
│   └── terraform/
│       ├── main.tf               # Recursos principais
│       ├── variables.tf          # Variáveis simplificadas
│       └── outputs.tf            # Saídas completas
├── tests/                        # Testes automatizados
├── EXEMPLOS_CLI.md              # Exemplos detalhados
├── requirements.txt             # Dependências Python
└── setup.py                     # Configuração do pacote
```

## 🎯 Vantagens

✅ **Simplicidade**: Apenas 3 parâmetros obrigatórios  
✅ **Segurança**: Service Principal com permissões adequadas  
✅ **Consistência**: Nomenclatura padronizada  
✅ **Automação**: Configurações otimizadas  
✅ **Governança**: Tags e auditoria automáticas  
✅ **Produção-Ready**: Configurações adequadas para produção

## 📚 Documentação

- [Exemplos de Uso](EXEMPLOS_CLI.md) - Exemplos detalhados de todos os comandos
- [Terraform README](src/terraform/README.md) - Documentação da infraestrutura

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.
