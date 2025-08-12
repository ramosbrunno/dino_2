# Dino Arc - Azure Resource Creator

## 🎯 Visão Geral

**Dino Arc** é uma ferramenta CLI que automatiza a criação de recursos fundamentais no Azure usando Terraform. Com apenas 4 parâmetros obrigatórios de autenticação, você cria uma infraestrutura completa e segura com:

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

# Instalar Azure CLI (para validação - opcional)
# Windows: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-windows

# ⚠️ IMPORTANTE: Não é necessário az login
# A ferramenta usa Service Principal para autenticação
# Você precisa ter um Service Principal criado no Azure com as credenciais:
# - Client ID (Application ID)
# - Client Secret
# - Tenant ID
# - Subscription ID (onde os recursos serão criados)
```

### Opção 1: Instalação como CLI Global (Recomendado)

#### Windows
```cmd
# Clonar o repositório
git clone https://github.com/ramosbrunno/dino_2.git
cd dino_2\dino_arc

# Executar instalador automático
install.bat

# Ou manualmente
pip install -e .
```

#### Linux/MacOS
```bash
# Clonar o repositório
git clone https://github.com/ramosbrunno/dino_2.git
cd dino_2/dino_arc

# Executar instalador automático
chmod +x install.sh
./install.sh

# Ou manualmente
pip install -e .
```

#### Verificar Instalação
```bash
# Verificar se o comando está disponível
dino-arc --help

# Exemplo de uso
dino-arc --action init --projeto "test"
```

### Opção 2: Instalação Tradicional (Desenvolvimento)
```bash
# Clonar o repositório
git clone https://github.com/ramosbrunno/dino_2.git
cd dino_2/dino_arc

# Instalar dependências
pip install -r requirements.txt

# Usar diretamente
python src/cli.py --help
```

## 📋 Uso Rápido

### ⚡ Comando CLI Global (Recomendado após instalação)
```bash
# Ver ajuda
dino-arc --help

# Criar infraestrutura completa (init executado automaticamente)
dino-arc \
  --client-id "12345678-1234-1234-1234-123456789012" \
  --client-secret "sua-client-secret-aqui" \
  --tenant_id "87654321-4321-4321-4321-210987654321" \
  --subscription-id "11111111-2222-3333-4444-555555555555" \
  --action apply \
  --projeto "analytics" \
  --ambiente "dev" \
  --location "East US"

# Visualizar plano (init executado automaticamente)
dino-arc \
  --client-id "12345678-1234-1234-1234-123456789012" \
  --client-secret "sua-client-secret-aqui" \
  --tenant_id "87654321-4321-4321-4321-210987654321" \
  --subscription-id "11111111-2222-3333-4444-555555555555" \
  --action plan \
  --projeto "analytics" \
  --ambiente "dev"
```

### ⚡ Uso Tradicional (Desenvolvimento)
```bash
# Inicializar Terraform (primeira vez)
python src/cli.py \
  --client-id "12345678-1234-1234-1234-123456789012" \
  --client-secret "sua-client-secret-aqui" \
  --tenant_id "87654321-4321-4321-4321-210987654321" \
  --action init \
  --projeto "analytics"

# Criar infraestrutura completa (Foundation + Databricks Premium + Unity Catalog)
python src/cli.py \
  --client-id "12345678-1234-1234-1234-123456789012" \
  --client-secret "sua-client-secret-aqui" \
  --tenant_id "87654321-4321-4321-4321-210987654321" \
  --action apply \
  --projeto "analytics" \
  --ambiente "dev" \
  --location "East US"
```

### 📋 Parâmetros Obrigatórios
- `--client-id`: Azure Client ID do Service Principal
- `--client-secret`: Azure Client Secret do Service Principal  
- `--tenant_id`: Azure Tenant ID
- `--subscription-id`: Azure Subscription ID (onde os recursos serão criados)
- `--action`: Ação a executar (init, plan, apply, destroy)
- `--projeto`: Nome do projeto (base para nomenclatura)

### 📋 Parâmetros Opcionais
- `--ambiente`: Ambiente (dev, staging, prod) - **padrão: dev**
- `--location`: Localização Azure - **padrão: East US**

### Comandos Disponíveis

#### Com CLI Global (dino-arc)
```bash
# 1. Inicializar manualmente (opcional - executado automaticamente com outros comandos)
dino-arc --client-id "..." --client-secret "..." --tenant_id "..." --subscription-id "..." --action init --projeto "analytics"

# 2. Planejar recursos (init automático + visualizar sem criar)
dino-arc --client-id "..." --client-secret "..." --tenant_id "..." --subscription-id "..." --action plan --projeto "analytics" --ambiente "dev"

# 3. Criar infraestrutura completa (init automático + deploy + configurar Databricks)
dino-arc --client-id "..." --client-secret "..." --tenant_id "..." --subscription-id "..." --action apply --projeto "analytics" --ambiente "dev"

# 4. Destruir recursos (init automático + destroy)
dino-arc --client-id "..." --client-secret "..." --tenant_id "..." --subscription-id "..." --action destroy --projeto "analytics" --ambiente "dev"
```

#### Com Python Tradicional
```bash
# 1. Inicializar (primeira vez)
python src/cli.py --client-id "..." --client-secret "..." --tenant_id "..." --action init --projeto "analytics"

# 2. Planejar recursos (visualizar sem criar)
python src/cli.py --client-id "..." --client-secret "..." --tenant_id "..." --action plan --projeto "analytics" --ambiente "dev"

# 3. Criar infraestrutura completa + configurar Databricks automaticamente
python src/cli.py --client-id "..." --client-secret "..." --tenant_id "..." --action apply --projeto "analytics" --ambiente "dev"

# 4. Destruir recursos
python src/cli.py --client-id "..." --client-secret "..." --tenant_id "..." --action destroy --projeto "analytics" --ambiente "dev"
```

## 📦 Recursos Criados Automaticamente

### 🏛️ Foundation Module (Sempre Criado)
- **Resource Group**: `{projeto}-{ambiente}-rsg`
- **Key Vault**: `{projeto}-{ambiente}-akv-{random}`
- **Service Principal**: `{projeto}-{ambiente}-spn`

### 🧮 Databricks Premium Module (Sempre Criado)
- **Databricks Workspace**: `{projeto}-{ambiente}-dbw-{random}` (SKU Premium)
- **DBFS Storage Account**: `{projeto}{ambiente}dbwsa{random}`
- **Unity Catalog Storage**: `{projeto}{ambiente}ucsa{random}` (Data Lake Gen2)

### 🗄️ Unity Catalog (Configurado Automaticamente)
- **Metastore**: `unity-catalog-{region}`
- **Catalog**: `{projeto}_{ambiente}`
- **Schemas**: bronze, silver, gold, workspace (arquitetura medallion)

### ⚡ Serverless Compute (Habilitado Automaticamente)
- **Serverless Compute**: Habilitado para workspace
- **SQL Warehouse**: `{projeto}-{ambiente}-warehouse` (Serverless Premium)

### 🔐 Secrets no Key Vault
- `databricks-workspace-url`: URL do workspace
- `databricks-workspace-id`: ID do workspace  
- `unity-catalog-storage-name`: Nome da storage account
- `unity-catalog-storage-key`: Chave de acesso
- `spn-client-id`: Application (Client) ID
- `spn-client-secret`: Client Secret
- `spn-tenant-id`: Tenant ID

## 🎯 Exemplos de Uso

### Desenvolvimento
```bash
python src/cli.py \
  --client-id "12345678-1234-1234-1234-123456789012" \
  --client-secret "sua-client-secret-aqui" \
  --tenant_id "87654321-4321-4321-4321-210987654321" \
  --action apply \
  --projeto "webapp" \
  --ambiente "dev" \
  --location "East US"
```

### Staging
```bash
python src/cli.py \
  --client-id "12345678-1234-1234-1234-123456789012" \
  --client-secret "sua-client-secret-aqui" \
  --tenant_id "87654321-4321-4321-4321-210987654321" \
  --action apply \
  --projeto "webapp" \
  --ambiente "staging" \
  --location "East US 2"
```

### Produção
```bash
python src/cli.py \
  --client-id "12345678-1234-1234-1234-123456789012" \
  --client-secret "sua-client-secret-aqui" \
  --tenant_id "87654321-4321-4321-4321-210987654321" \
  --action apply \
  --projeto "webapp" \
  --ambiente "prod" \
  --location "Brazil South"
```

### Como Obter as Credenciais do Service Principal

#### Opção 1: Usar Azure Portal
1. Acesse o [Azure Portal](https://portal.azure.com)
2. Navegue para **Azure Active Directory > App registrations**
3. Clique em **New registration**
4. Preencha o nome e clique em **Register**
5. Copie o **Application (client) ID** e **Directory (tenant) ID**
6. Vá em **Certificates & secrets > New client secret**
7. Copie o **Client secret value**

#### Opção 2: Usar Azure CLI (se disponível)
```bash
# Criar Service Principal
az ad sp create-for-rbac --name "dino-arc-sp" --role contributor

# Resultado (exemplo):
{
  "appId": "12345678-1234-1234-1234-123456789012",     # client_id
  "password": "sua-client-secret-aqui",                # client_secret  
  "tenant": "87654321-4321-4321-4321-210987654321"    # tenant_id
}
```

## 🔒 Segurança e Boas Práticas

### ⚠️ Importante - Segurança das Credenciais
```bash
# ❌ NUNCA faça isso (credenciais expostas)
python src/cli.py --client-secret "senha123" --action apply --projeto "test"

# ✅ Use variáveis de ambiente
export AZURE_CLIENT_ID="12345678-1234-1234-1234-123456789012"
export AZURE_CLIENT_SECRET="sua-client-secret-aqui"
export AZURE_TENANT_ID="87654321-4321-4321-4321-210987654321"

python src/cli.py \
  --client-id "$AZURE_CLIENT_ID" \
  --client-secret "$AZURE_CLIENT_SECRET" \
  --tenant_id "$AZURE_TENANT_ID" \
  --action apply \
  --projeto "analytics"
```

### 🛡️ Recomendações de Segurança
1. **Nunca commitar credenciais** no código ou repositório
2. **Use variáveis de ambiente** para armazenar credenciais
3. **Rotacione secrets regularmente** (a cada 90 dias)
4. **Configure permissões mínimas** no Service Principal
5. **Monitor logs de acesso** no Azure AD
6. **Use Azure Key Vault** para credenciais em produção

## 📊 Saída Típica

```
🚀 Criando infraestrutura completa para projeto 'analytics' no ambiente 'dev' em 'East US'...
📦 Resource Group: analytics-dev-rsg
🔐 Key Vault: analytics-dev-akv-abc123
👤 Service Principal: analytics-dev-spn
🧮 Databricks Premium: analytics-dev-dbw-abc123
📊 Unity Catalog Storage: analyticsdevucsa123

✅ Infraestrutura completa criada com sucesso!
📋 Componentes implantados:
   🏛️  Foundation (Resource Group + Key Vault + Service Principal)
   🧮 Databricks Premium (Unity Catalog + Serverless)

⏳ Aguardando recursos ficarem prontos para configuração...

🔧 Configurando Databricks Unity Catalog e Serverless...
📋 Obtendo outputs do Terraform...
✅ Conectando ao Databricks: https://adb-1234567890123456.78.azuredatabricks.net

🗄️  Criando Unity Catalog Metastore...
✅ Unity Catalog Metastore criado: unity-catalog-east-us

📚 Criando Catalog: analytics_dev...
✅ Catalog criado: analytics_dev

🗂️  Criando Schemas...
✅ Schema criado: analytics_dev.bronze
✅ Schema criado: analytics_dev.silver  
✅ Schema criado: analytics_dev.gold
✅ Schema criado: analytics_dev.workspace

⚡ Habilitando Serverless Compute...
✅ Serverless Compute habilitado!

🏭 Criando SQL Warehouse Serverless...
✅ SQL Warehouse Serverless criado: analytics-dev-warehouse

🎊 Deploy completo finalizado!
🚀 Seu ambiente Databricks Premium está pronto para uso:
   📊 Unity Catalog configurado com arquitetura medallion
   ⚡ Serverless Compute habilitado
   🏭 SQL Warehouse Serverless criado
   📚 Catalog: analytics_dev
   🗂️  Schemas: bronze, silver, gold, workspace
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

✅ **Deploy Completo**: Foundation + Databricks Premium + Unity Catalog em uma execução  
✅ **Simplicidade**: Apenas 4 parâmetros de autenticação obrigatórios (client-id, client-secret, tenant-id, subscription-id)  
✅ **Segurança**: Service Principal com permissões adequadas  
✅ **Premium Features**: Databricks Premium com Unity Catalog e Serverless  
✅ **Automação Total**: Configuração completa sem interação manual  
✅ **Consistência**: Nomenclatura padronizada  
✅ **Governança**: Tags e auditoria automáticas  
✅ **Produção-Ready**: Configurações otimizadas para produção  
✅ **Arquitetura Medallion**: Schemas bronze, silver, gold pré-configurados

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
