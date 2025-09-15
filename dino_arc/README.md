# DINO ARC v2.3.0 🚀

**Ferramenta CLI Inteligente para Criação Automatizada de Infraestrutura Azure**

Automatize a criação de ambientes completos Azure com Databricks Premium, Unity Catalog, Azure SQL Database e gerenciamento inteligente de secrets usando Terraform e autenticação Service Principal (SPN).

## 🎯 Características Principais

### 🔐 **Segurança Avançada**
- ✅ Autenticação via Service Principal (SPN)
- ✅ Gerenciamento automático de secrets no Azure Key Vault
- ✅ Separação de privilégios: SPN do Dino executa, SPN criada recebe políticas
- ✅ Access policies inteligentes com permissões mínimas necessárias

### 🧠 **Sistema de Nomenclatura Inteligente**
- ✅ **Nomenclatura adaptativa**: Respeita automaticamente limites do Azure
- ✅ **Key Vault**: Máximo 24 caracteres com truncamento automático
- ✅ **Storage Account**: Máximo 24 caracteres com random ID para unicidade
- ✅ **Databricks Workspace**: Nomenclatura otimizada para Premium SKU

### 🏗️ **Infraestrutura Completa**
- ✅ **Azure Resource Group**: Organização centralizada de recursos
- ✅ **Azure Key Vault**: Armazenamento seguro de credenciais com soft delete
- ✅ **Service Principal**: Criação automática com permissões corretas
- ✅ **Databricks Premium**: Unity Catalog habilitado e Serverless ready
- ✅ **Unity Catalog Storage**: ADLS Gen2 com configurações otimizadas
- ✅ **Azure SQL Database**: Para logging de pipelines (opcional)

### 🔄 **Tratamento Inteligente de Erros**
- ✅ **Secrets duplicadas**: Detecção automática e continuidade da execução
- ✅ **Timeouts configuráveis**: Para recursos que demandam mais tempo
- ✅ **Dependencies management**: Ordem correta de criação de recursos
- ✅ **State recovery**: Recuperação inteligente do estado Terraform

## ⚡ Setup Rápido

### Pré-requisitos
- **Python 3.8+** instalado
- **Terraform 1.0+** instalado
- **Service Principal Azure** com permissões adequadas
- **Azure CLI** (opcional, para validações)

### 🚀 Instalação

#### 1. Clonar e Configurar Ambiente
```bash
# Clonar repositório
git clone <repository-url>
cd dino_arc

# Criar ambiente virtual
python -m venv dino_env

# Ativar ambiente virtual (Windows)
dino_env\Scripts\activate

# Instalar dependências
pip install -e .
```

#### 2. Instalar Terraform

**Opção A: Windows com winget (Recomendado)**
```bash
winget install HashiCorp.Terraform
```

**Opção B: Download Manual**
1. Baixar do [site oficial Terraform](https://www.terraform.io/downloads)
2. Extrair para pasta no PATH do sistema
3. Verificar: `terraform --version`
#### 3. Verificar Instalação
```bash
# Verificar Terraform
terraform --version

# Verificar Python
python --version

# Verificar DINO ARC
python -m src.cli --help
```

## 🚀 Uso Básico

### 📋 Sintaxe Principal
```bash
python -m src.cli \
  --client-id <SPN_CLIENT_ID> \
  --client-secret <SPN_CLIENT_SECRET> \
  --tenant_id <AZURE_TENANT_ID> \
  --subscription-id <AZURE_SUBSCRIPTION_ID> \
  --action apply \
  --projeto <NOME_PROJETO> \
  --location "<AZURE_REGION>"
```

### 🎯 Exemplo Prático
```bash
# Criar infraestrutura completa para projeto "data-analytics"
python -m src.cli \
  --client-id "12345678-1234-1234-1234-123456789abc" \
  --client-secret "your-client-secret-here" \
  --tenant_id "87654321-4321-4321-4321-cba987654321" \
  --subscription-id "11111111-2222-3333-4444-555555555555" \
  --action apply \
  --projeto "data-analytics" \
  --location "Brazil South"
```

### 🗑️ Destruir Infraestrutura
```bash
# Remover todos os recursos criados
python -m src.cli \
  --client-id "12345678-1234-1234-1234-123456789abc" \
  --client-secret "your-client-secret-here" \
  --tenant_id "87654321-4321-4321-4321-cba987654321" \
  --subscription-id "11111111-2222-3333-4444-555555555555" \
  --action destroy \
  --projeto "data-analytics" \
  --location "Brazil South"
```

## 📦 Recursos Criados

### 🏗️ **Infraestrutura Foundation**
| Recurso | Nomenclatura | Descrição |
|---------|-------------|-----------|
| **Resource Group** | `{projeto}-{ambiente}-rsg` | Organização de todos os recursos |
| **Key Vault** | `{projeto}-{ambiente}-akv-{random}` | Armazenamento seguro de secrets |
| **Service Principal** | `{projeto}-{ambiente}-spn` | Identidade para automação |

### 🧮 **Databricks Premium + Unity Catalog**
| Recurso | Nomenclatura | Descrição |
|---------|-------------|-----------|
| **Databricks Workspace** | `{projeto}-{ambiente}-dbw` | Workspace Premium SKU |
| **Unity Catalog Storage** | `{projeto}{ambiente}sauc{random}` | ADLS Gen2 para metastore |
| **Storage Container** | `unity-catalog` | Container para Unity Catalog |

### 💾 **Azure SQL Database (Opcional)**
| Recurso | Nomenclatura | Descrição |
|---------|-------------|-----------|
| **SQL Server** | `{projeto}-{ambiente}-sql` | Servidor Azure SQL |
| **SQL Database** | `{projeto}-{ambiente}-db-logs` | Database para logs de pipeline |

### 🔐 **Secrets Armazenadas no Key Vault**
| Secret | Descrição |
|--------|-----------|
| `spn-client-id` | Client ID da SPN criada |
| `spn-client-secret` | Secret da SPN criada |
| `databricks-workspace-url` | URL da workspace Databricks |
| `unity-catalog-storage-name` | Nome do storage do Unity Catalog |
| `databricks-access-token` | Token de acesso gerado |

## 🎯 Exemplos de Uso

### 🔐 **Ambiente de Desenvolvimento**
```bash
# Criar ambiente de desenvolvimento completo
python -m src.cli \
  --client-id "12345678-1234-1234-1234-123456789abc" \
  --client-secret "your-dev-secret" \
  --tenant_id "87654321-4321-4321-4321-cba987654321" \
  --subscription-id "11111111-2222-3333-4444-555555555555" \
  --action apply \
  --projeto "analytics-dev" \
  --location "Brazil South"
```

### 🏢 **Ambiente de Produção**
```bash
# Para produção, use variáveis de ambiente (mais seguro)
# Configure primeiro:
set ARM_CLIENT_ID=your-prod-client-id
set ARM_CLIENT_SECRET=your-prod-secret
set ARM_TENANT_ID=your-tenant-id
set ARM_SUBSCRIPTION_ID=your-prod-subscription

# Execute sem expor credenciais
python -m src.cli \
  --action apply \
  --projeto "analytics-prod" \
  --location "East US 2"
```

### 🎯 **Projeto Específico**
```bash
# Criar infraestrutura para projeto de Machine Learning
python -m src.cli \
  --client-id "your-client-id" \
  --client-secret "your-client-secret" \
  --tenant_id "your-tenant-id" \
  --subscription-id "your-subscription-id" \
  --action apply \
  --projeto "ml-platform" \
  --location "West Europe"
```

### 🗑️ **Limpeza de Recursos**
```bash
# Remover infraestrutura específica
python -m src.cli \
  --client-id "your-client-id" \
  --client-secret "your-client-secret" \
  --tenant_id "your-tenant-id" \
  --subscription-id "your-subscription-id" \
  --action destroy \
  --projeto "analytics-dev" \
  --location "Brazil South"
```

## 🛡️ Segurança e Boas Práticas

### 🔐 **Gerenciamento de Credenciais**
- ✅ **NUNCA** commite credenciais reais no código
- ✅ Use variáveis de ambiente para produção
- ✅ Mantenha secrets seguros no Azure Key Vault
- ✅ Revogue credenciais se expostas acidentalmente
- ✅ Rotacione secrets periodicamente

### 🎯 **Separação de Privilégios**
- ✅ **SPN do Dino**: Executa Terraform com privilégios de subscription
- ✅ **SPN Criada**: Recebe apenas policies específicas dos recursos
- ✅ **Key Vault**: Access policies com permissões mínimas necessárias

### 📋 **Nomenclatura Inteligente**
- ✅ **Limites Azure**: Respeitados automaticamente (Key Vault: 24 chars)
- ✅ **Unicidade**: Random IDs para evitar conflitos
- ✅ **Padrão**: `{projeto}-{ambiente}-{tipo}` para organização

## 🔧 Recursos Avançados

### 🧠 **Sistema de Tratamento de Erros**
- ✅ **Secrets Duplicadas**: Detecção automática com continuidade
- ✅ **Timeouts**: Configuráveis para recursos complexos
- ✅ **Dependencies**: Ordem correta de criação (depends_on)
- ✅ **State Recovery**: Recuperação inteligente do estado Terraform

### ⚙️ **Configurações Otimizadas**
- ✅ **Databricks Premium**: Unity Catalog e Serverless habilitados
- ✅ **ADLS Gen2**: Hierarchical namespace para Unity Catalog
- ✅ **SQL Database**: Configuração otimizada para logging
- ✅ **Network Security**: Regras padrão de segurança

## 🚨 Troubleshooting

### ❌ **Erro: "Key Vault name too long"**
```
✅ Solução: Sistema automático agora trunca nomes longos
ℹ️ Key Vault: Máximo 24 caracteres com random ID para unicidade
```

### ❌ **Erro: "Secrets already exist"**
```
✅ Solução: Sistema detecta automaticamente e continua execução
ℹ️ Comportamento: Tratamento inteligente de secrets duplicadas
```

### ❌ **Erro: "Terraform authentication failed"**
```bash
# Verificar credenciais
az login --service-principal \
  --username "your-client-id" \
  --password "your-client-secret" \
  --tenant "your-tenant-id"

# Verificar permissões
az role assignment list --assignee "your-client-id"
```

### ❌ **Erro: "Resource Group not found"**
```bash
# Verificar subscription ativa
az account show

# Verificar permissões na subscription
az role assignment list --all --assignee "your-client-id" \
  --query "[?scope=='/subscriptions/your-subscription-id']"
```

### 🔧 **Reinicializar Estado**
```bash
# Se houver problemas com estado Terraform
cd src/terraform
terraform init -reconfigure
terraform refresh
```

## 📊 Logs e Monitoramento

### 📝 **Logs de Execução**
```bash
# Logs do CLI são exibidos em tempo real com emojis
🔐 Autenticando com Azure via Service Principal...
✅ Autenticação bem-sucedida!
🔧 Verificando inicialização do Terraform...
✅ Terraform já inicializado!
🚀 Criando infraestrutura completa...
```

### 🔍 **Estado do Terraform**
```bash
# Verificar estado atual
cd src/terraform
terraform show

# Listar recursos criados
terraform state list

# Detalhes de um recurso específico
terraform state show module.foundation.azurerm_resource_group.main
```

### 📊 **Verificação no Azure Portal**
Após execução bem-sucedida, verifique no Azure Portal:
- ✅ Resource Group criado
- ✅ Key Vault com secrets armazenadas
- ✅ Service Principal configurada
- ✅ Databricks Workspace Premium
- ✅ Unity Catalog Storage Account

## 🔄 Unity Catalog - Configuração Manual

### 📋 **Passos Pós-Deploy**
1. **Acessar Databricks Account Console**
2. **Criar Metastore** (se não existir)
3. **Associar Metastore à Workspace**
4. **Configurar External Storage Location**
5. **Criar Catalog com ALL PRIVILEGES**

### 🏗️ **Comandos SQL no Databricks**
```sql
-- Criar catalog após configurar metastore
CREATE CATALOG my_catalog
MANAGED LOCATION 'abfss://unity-catalog@{storage_name}.dfs.core.windows.net/'
COMMENT 'Catalog criado via DINO ARC';

-- Conceder privilégios (substitua pelo email real)
GRANT ALL PRIVILEGES ON CATALOG my_catalog TO `admin@company.com`;
```

## �️ Arquitetura

O DINO ARC cria automaticamente:

- ✅ **Resource Group**: `{projeto}-{ambiente}-rsg`
- ✅ **Key Vault**: Para armazenamento seguro de secrets
- ✅ **Service Principal**: Para autenticação automatizada
- ✅ **Azure SQL Database**: Para logs e metadados
## 🏗️ Arquitetura

### 📊 **Módulos Terraform**
```
dino_arc/
├── src/terraform/
│   ├── main.tf                    # Orquestração principal
│   ├── variables.tf               # Variáveis globais
│   ├── outputs.tf                 # Outputs consolidados
│   └── modules/
│       ├── foundation/            # RG + Key Vault + SPN
│       │   ├── main.tf
│       │   ├── variables.tf
│       │   └── outputs.tf
│       ├── databricks/            # Databricks + Unity Catalog
│       │   ├── main.tf
│       │   ├── variables.tf
│       │   └── outputs.tf
│       └── sql_database/          # Azure SQL (opcional)
│           ├── main.tf
│           ├── variables.tf
│           └── outputs.tf
```

### 🔄 **Fluxo de Execução**
1. **🔐 Autenticação**: Service Principal do Dino
2. **📦 Foundation**: Resource Group + Key Vault + SPN nova
3. **🧮 Databricks**: Workspace Premium + Unity Catalog Storage
4. **💾 SQL Database**: Para logging de pipelines (opcional)
5. **🔑 Secrets**: Armazenamento automático no Key Vault

### 🛡️ **Modelo de Segurança**
- **SPN Dino**: Executa Terraform (privilégios subscription)
- **SPN Criada**: Recebe apenas policies específicas dos recursos
- **Key Vault**: Access policies granulares
- **Databricks**: Unity Catalog com external storage

## � Parâmetros CLI

| Parâmetro | Descrição | Obrigatório | Exemplo |
|-----------|-----------|-------------|---------|
| `--client-id` | Azure SPN Client ID | ✅ | `12345678-1234-...` |
| `--client-secret` | Azure SPN Secret | ✅ | `your-secret-here` |
| `--tenant_id` | Azure Tenant ID | ✅ | `87654321-4321-...` |
| `--subscription-id` | Azure Subscription ID | ✅ | `11111111-2222-...` |
| `--action` | Ação (apply/destroy) | ✅ | `apply` |
| `--projeto` | Nome do projeto | ✅ | `analytics-platform` |
| `--location` | Região Azure | ✅ | `"Brazil South"` |

## � Recursos Avançados

### 🔄 **Idempotência**
- ✅ Múltiplas execuções sem conflitos
- ✅ Detecção automática de resources existentes
- ✅ State management inteligente

### 📏 **Validações Automáticas**
- ✅ Limites de nomenclatura Azure
- ✅ Formato de parâmetros (UUIDs, nomes)
- ✅ Permissões do Service Principal

### 🔧 **Error Recovery**
- ✅ Timeouts configuráveis
- ✅ Retry logic para recursos instáveis
- ✅ Rollback automático em caso de falha

## 📞 Suporte

### 🐛 **Reportar Issues**
- Crie uma issue detalhada com logs completos
- Inclua versões (Python, Terraform, DINO ARC)
- Mascare informações sensíveis (IDs, secrets)

### 📚 **Documentação Adicional**
- **Azure Databricks**: [Documentação oficial](https://docs.microsoft.com/azure/databricks/)
- **Unity Catalog**: [Guia Unity Catalog](https://docs.databricks.com/data-governance/unity-catalog/)
- **Terraform Azure**: [Provider documentation](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)

---

## 🎉 **DINO ARC v2.3.0 - Pronto para Produção!**

**✨ Infraestrutura Azure moderna, segura e escalável em um comando!** ✨

**⚡ Desenvolvido com ❤️ para acelerar projetos de Data & Analytics** ⚡

## Requisitos

- Python 3.8+
- Azure CLI configurado
- Credenciais de Service Principal do Azure

## Gerenciamento do Ambiente

### Desativar Ambiente Virtual
```bash
deactivate
```

### Reativar Ambiente Virtual (sessões futuras)
```bash
# No Windows:
dino_env\Scripts\activate

# No Linux/Mac:
source dino_env/bin/activate
```
